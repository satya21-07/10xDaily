"""
seed_sources.py

One-time (or occasional) offline script to populate SpiritualSource with
verses from multiple free, public-domain / free-API traditions, and
auto-tag each with a `topic` using Groq.

Run this LOCALLY / as a one-off management command, NOT at request time.

Usage:
    python seed_sources.py --tradition sefaria_pirkei_avot
    python seed_sources.py --tradition suttacentral_dhammapada
    python seed_sources.py --tradition bible_proverbs
    python seed_sources.py --all

Adjust the field names in `SpiritualSource(...)` near the bottom to match
your actual model if they differ from what's used in daily_spiritual.py:
    source_name, source_reference, chapter, verse, character, section,
    original_text, translation, topic
"""

import os
import sys
import time
import json
import logging
import argparse
import requests
from typing import Iterator, Optional

# Ensure app is in path if running directly from scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal  # adjust to your actual session factory
from app.models.core_models import SpiritualSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_sources")

GROQ_MODEL = os.getenv("GROQ_SEED_MODEL", "llama-3.3-70b-versatile")

# A small fixed topic taxonomy keeps rotation logic sane later.
# Feel free to expand, but keep it a closed set so filtering/UI stays simple.
TOPIC_TAXONOMY = [
    "Karma", "Duty", "Detachment", "Grief", "Anger", "Fear", "Impermanence",
    "Compassion", "Forgiveness", "Patience", "Humility", "Truth",
    "Self-Discipline", "Gratitude", "Suffering", "Wisdom", "Faith",
    "Love", "Justice", "Purpose",
]


# ---------------------------------------------------------------------------
# 1. COLLECTORS — one per tradition/API. Each yields a raw dict per verse.
# ---------------------------------------------------------------------------

def collect_sefaria(work: str, refs: list[str]) -> Iterator[dict]:
    """
    Sefaria API (Torah, Mishnah, Talmud, Pirkei Avot, etc.)
    Docs: https://developers.sefaria.org/
    Free, no API key required.
    """
    for ref in refs:
        url = f"https://www.sefaria.org/api/texts/{ref}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"Sefaria fetch failed for {ref}: {e}")
            continue

        # Sefaria returns "he" (original) and "text" (English) —
        # sometimes as nested lists depending on the ref granularity.
        original = data.get("he")
        translation = data.get("text")
        if isinstance(original, list):
            original = " ".join(x for x in original if x)
        if isinstance(translation, list):
            translation = " ".join(x for x in translation if x)

        if not translation:
            continue

        yield {
            "source_name": work,
            "source_reference": ref,
            "original_text": original,
            "translation": strip_html(translation),
            "character": None,
            "section": data.get("sectionNames", [None])[0],
            "chapter": None,
            "verse": None,
        }
        time.sleep(0.3)  # be polite to the free API


def collect_suttacentral(sutta_ids: list[str]) -> Iterator[dict]:
    """
    SuttaCentral API (Buddhist suttas, e.g. Dhammapada).
    Docs: https://suttacentral.net/api  (no key required)
    """
    for sid in sutta_ids:
        url = f"https://suttacentral.net/api/bilarasuttas/{sid}/en/sujato"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"SuttaCentral fetch failed for {sid}: {e}")
            continue

        translation_segments = data.get("translation_text", {})
        root_segments = data.get("root_text", {})
        translation = " ".join(translation_segments.values()) if isinstance(translation_segments, dict) else None
        original = " ".join(root_segments.values()) if isinstance(root_segments, dict) else None

        if not translation:
            continue

        yield {
            "source_name": "Dhammapada",
            "source_reference": sid,
            "original_text": original,
            "translation": translation.strip(),
            "character": "The Buddha",
            "section": None,
            "chapter": None,
            "verse": None,
        }
        time.sleep(0.3)


def collect_bible(book: str, chapters: list[int]) -> Iterator[dict]:
    """
    bible-api.com — free, no key, WEB (public domain) translation by default.
    """
    for ch in chapters:
        url = f"https://bible-api.com/{book}+{ch}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"bible-api fetch failed for {book} {ch}: {e}")
            continue

        for v in data.get("verses", []):
            yield {
                "source_name": "Bible",
                "source_reference": f"{book} {v['chapter']}:{v['verse']}",
                "original_text": None,
                "translation": v["text"].strip(),
                "character": None,
                "section": None,
                "chapter": v["chapter"],
                "verse": v["verse"],
            }
        time.sleep(0.3)


def collect_quran(surahs: list[int]) -> Iterator[dict]:
    """
    alquran.cloud API — free, no key.
    """
    for surah in surahs:
        url = f"https://api.alquran.cloud/v1/surah/{surah}/en.asad"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()["data"]
        except Exception as e:
            logger.warning(f"alquran.cloud fetch failed for surah {surah}: {e}")
            continue

        for ayah in data.get("ayahs", []):
            yield {
                "source_name": "Quran",
                "source_reference": f"Surah {data['englishName']} {ayah['numberInSurah']}",
                "original_text": None,
                "translation": ayah["text"].strip(),
                "character": None,
                "section": data.get("englishName"),
                "chapter": surah,
                "verse": ayah["numberInSurah"],
            }
        time.sleep(0.3)


def collect_gita() -> Iterator[dict]:
    """
    vedicscriptures.github.io — free, keyless, community-run Gita API.
    18 chapters, ~700 verses total. Includes Sanskrit + several English
    translations (we use Swami Tejomayananda's, `tej.ec`, as the default —
    change `translator_key` if you prefer another).
    https://github.com/vedicscriptures/bhagavad-gita-api
    """
    chapter_verse_counts = {  # verses per chapter, so we know how far to go
        1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28, 9: 34,
        10: 42, 11: 55, 12: 20, 13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78,
    }
    translator_key = "tej"  # Swami Tejomayananda — clear, accessible English

    for chapter, verse_count in chapter_verse_counts.items():
        for verse in range(1, verse_count + 1):
            url = f"https://vedicscriptures.github.io/slok/{chapter}/{verse}"
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.warning(f"Gita API fetch failed for {chapter}.{verse}: {e}")
                continue

            translation = (data.get(translator_key) or {}).get("ec")
            if not translation:
                continue  # some verses lack this particular translator

            yield {
                "source_name": "Bhagavad Gita",
                "source_reference": f"Bhagavad Gita {chapter}.{verse}",
                "original_text": data.get("slok"),
                "translation": translation.strip(),
                "character": None,  # API doesn't reliably tag speaker; leave for manual fill if needed
                "section": None,
                "chapter": chapter,
                "verse": verse,
            }
            time.sleep(0.2)


def collect_ramayana(max_shlokas: Optional[int] = None) -> Iterator[dict]:
    """
    Community-maintained structured dataset (NOT an official/vetted source —
    spot-check a sample before trusting it at scale, per your own accuracy rules).
    Pulls raw JSON from GitHub.
    https://github.com/Ashutosh-Vijay/Valmiki_Ramayan_Dataset
    """
    url = (
        "https://raw.githubusercontent.com/Ashutosh-Vijay/"
        "Valmiki_Ramayan_Dataset/main/data/Valmiki_Ramayan_Shlokas.json"
    )
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        shlokas = resp.json()
    except Exception as e:
        logger.warning(f"Ramayana dataset fetch failed: {e}")
        return

    if max_shlokas:
        shlokas = shlokas[:max_shlokas]

    for entry in shlokas:
        translation = entry.get("translation") or entry.get("meaning")
        if not translation:
            continue

        kanda = entry.get("kanda") or entry.get("Kanda")
        sarga = entry.get("sarga") or entry.get("Sarga")
        shloka_num = entry.get("shloka") or entry.get("Shloka")

        yield {
            "source_name": "Ramayana",
            "source_reference": f"Ramayana {kanda} {sarga}.{shloka_num}",
            "original_text": entry.get("sanskrit") or entry.get("shloka_text"),
            "translation": translation.strip(),
            "character": None,
            "section": kanda,
            "chapter": sarga,
            "verse": shloka_num,
        }
        time.sleep(0.05)  # local-ish, lighter throttle than external APIs


def strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ---------------------------------------------------------------------------
# 2. TOPIC TAGGING — batched Groq calls with a keyword fallback
# ---------------------------------------------------------------------------

def tag_topic_with_groq(client, translation: str) -> Optional[str]:
    prompt = f"""Classify the following spiritual/philosophical passage into EXACTLY ONE
topic from this fixed list, and respond with ONLY the topic word, nothing else:

{", ".join(TOPIC_TAXONOMY)}

Passage:
\"\"\"{translation[:800]}\"\"\"

Topic:"""

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0,
        )
        topic = resp.choices[0].message.content.strip()
        # Guard against the model inventing a topic outside the taxonomy
        if topic not in TOPIC_TAXONOMY:
            return fallback_keyword_topic(translation)
        return topic
    except Exception as e:
        logger.warning(f"Groq tagging failed, using keyword fallback: {e}")
        return fallback_keyword_topic(translation)


def fallback_keyword_topic(text: str) -> str:
    """Cheap heuristic so seeding never fully blocks on Groq rate limits."""
    text_l = (text or "").lower()
    keyword_map = {
        "Karma": ["action", "deed", "consequence"],
        "Grief": ["sorrow", "grief", "mourn", "loss"],
        "Anger": ["anger", "wrath", "rage"],
        "Fear": ["fear", "afraid", "anxiety"],
        "Impermanence": ["impermanen", "fleeting", "temporary", "transient"],
        "Compassion": ["compassion", "kindness", "mercy"],
        "Forgiveness": ["forgive", "pardon"],
        "Patience": ["patience", "endure"],
        "Humility": ["humility", "humble", "pride"],
        "Truth": ["truth", "honesty"],
        "Gratitude": ["gratitude", "thankful"],
        "Suffering": ["suffering", "pain", "affliction"],
        "Wisdom": ["wisdom", "knowledge", "understanding"],
        "Love": ["love", "affection"],
        "Justice": ["justice", "righteous"],
    }
    for topic, keywords in keyword_map.items():
        if any(k in text_l for k in keywords):
            return topic
    return "Wisdom"  # safe default


# ---------------------------------------------------------------------------
# 3. DEDUP + BULK INSERT
# ---------------------------------------------------------------------------

def seed(db: Session, raw_verses: Iterator[dict], use_groq: bool = True, batch_size: int = 25):
    groq_client = None
    if use_groq:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key != "your_groq_api_key_here":
            from groq import Groq
            groq_client = Groq(api_key=api_key)
        else:
            logger.warning("No GROQ_API_KEY set — falling back to keyword tagging for all verses.")

    existing_refs = {
        r[0] for r in db.query(SpiritualSource.source_reference).all()
    }

    inserted = 0
    buffer = []

    for v in raw_verses:
        if v["source_reference"] in existing_refs:
            continue  # already seeded, skip

        translation = v.get("translation") or ""
        if not translation:
            continue

        topic = (
            tag_topic_with_groq(groq_client, translation)
            if groq_client else fallback_keyword_topic(translation)
        )

        buffer.append(SpiritualSource(
            source_name=v["source_name"],
            source_reference=v["source_reference"],
            chapter=v.get("chapter"),
            verse=v.get("verse"),
            character=v.get("character"),
            section=v.get("section"),
            original_text=v.get("original_text"),
            translation=translation,
            topic=topic,
        ))
        existing_refs.add(v["source_reference"])  # avoid dupes within this same run

        if len(buffer) >= batch_size:
            db.bulk_save_objects(buffer)
            db.commit()
            inserted += len(buffer)
            logger.info(f"Inserted {inserted} sources so far...")
            buffer = []

        # Respect Groq free-tier RPM if tagging live
        if groq_client:
            time.sleep(0.5)

    if buffer:
        db.bulk_save_objects(buffer)
        db.commit()
        inserted += len(buffer)

    logger.info(f"Done. Inserted {inserted} new sources.")
    return inserted


# ---------------------------------------------------------------------------
# 4. TRADITION REGISTRY — add new traditions here
# ---------------------------------------------------------------------------

TRADITIONS = {
    "gita": lambda: collect_gita(),  # ~700 verses, official-quality community API
    "ramayana": lambda: collect_ramayana(max_shlokas=2000),  # unvetted dataset — spot-check first
    "sefaria_pirkei_avot": lambda: collect_sefaria(
        "Pirkei Avot",
        [f"Pirkei_Avot.{ch}.{v}" for ch in range(1, 7) for v in range(1, 20)],
    ),
    "suttacentral_dhammapada": lambda: collect_suttacentral(
        [f"dhp{i}" for i in range(1, 27)]  # Dhammapada has 26 chapters
    ),
    "bible_proverbs": lambda: collect_bible("proverbs", list(range(1, 32))),
    "bible_psalms": lambda: collect_bible("psalms", list(range(1, 151))),
    "quran_selected": lambda: collect_quran([1, 2, 18, 36, 55, 67, 112, 113, 114]),
    # "mahabharata": not included — no clean free API/dataset exists yet.
    # See notes below for your options (sacred-texts.com scrape or manual curation).
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tradition", choices=list(TRADITIONS.keys()))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--no-groq", action="store_true", help="Use keyword tagging only (faster, free, less accurate)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.all:
            for name, collector_fn in TRADITIONS.items():
                logger.info(f"=== Seeding {name} ===")
                seed(db, collector_fn(), use_groq=not args.no_groq)
        elif args.tradition:
            seed(db, TRADITIONS[args.tradition](), use_groq=not args.no_groq)
        else:
            parser.error("Pass --tradition <name> or --all")
    finally:
        db.close()


if __name__ == "__main__":
    main()
