import os
import json
import logging
import random
import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.core_models import SpiritualSource, DailySpiritualLesson
from app.schemas.spiritual import GroqSpiritualLessonSchema, DailySpiritualLessonResponse

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"

FALLBACK_DATA = {
    "topic": "Karma",
    "source": {
        "name": "Bhagavad Gita",
        "reference": "Bhagavad Gita 2.47",
        "chapter": 2,
        "verse": 47
    },
    "reflection": {
        "title": "Nishkama Karma — Action Without Attachment",
        "explanation": (
            "In the second chapter of the Bhagavad Gita, Krishna delivers one of the most "
            "transformative teachings in world philosophy. Arjuna stands frozen on the battlefield "
            "of Kurukshetra, unable to fight because he fears the outcome. Krishna's response "
            "cuts to the root of all human suffering: we suffer because we are attached to results "
            "rather than to the quality of our effort. You have a right to act — but you do not "
            "own the outcome. Nishkama karma (desireless action) is not passivity; it is the art "
            "of giving your absolute best without making your peace of mind contingent on the result."
        ),
        "key_takeaways": [
            "Your job is to act with full effort — the outcome is beyond your control",
            "Attachment to results distorts your judgment and creates anxiety",
            "Detachment from outcomes paradoxically leads to better performance"
        ]
    },
    "today_practice": {
        "title": "One Task, Full Effort",
        "description": (
            "Choose the most important task on your plate today. Before beginning, "
            "silently commit: 'I will give this my complete attention and best effort. "
            "Whatever happens after is not mine to control.' Notice how this changes "
            "your relationship to the work itself."
        )
    },
    "journal_prompt": (
        "Think of a situation where fear of a bad outcome stopped you from acting "
        "or caused you to act poorly. What would you have done differently if you "
        "had been fully detached from the result?"
    )
}

def get_recent_source_ids(db: Session, days: int = 30) -> set:
    """Return source IDs used in lessons from the last N days to avoid repetition."""
    lessons = db.query(DailySpiritualLesson).order_by(
        DailySpiritualLesson.lesson_date.desc()
    ).limit(days).all()
    return {lesson.source_id for lesson in lessons}


def fallback_keyword_topic(text: str) -> str:
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
    return "Wisdom"


def fetch_live_gita() -> dict:
    chapter_verse_counts = {
        1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28, 9: 34,
        10: 42, 11: 55, 12: 20, 13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78,
    }
    chapter = random.choice(list(chapter_verse_counts.keys()))
    verse = random.randint(1, chapter_verse_counts[chapter])
    url = f"https://vedicscriptures.github.io/slok/{chapter}/{verse}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    translation = (data.get("tej") or {}).get("ec")
    if not translation:
        raise Exception("Missing translation")
    return {
        "source_name": "Bhagavad Gita",
        "source_reference": f"Bhagavad Gita {chapter}.{verse}",
        "original_text": data.get("slok"),
        "translation": translation.strip(),
        "character": None,
        "section": None,
        "chapter": chapter,
        "verse": verse,
    }


def fetch_live_bible() -> dict:
    # Proverbs has 31 chapters
    chapter = random.randint(1, 31)
    url = f"https://bible-api.com/proverbs+{chapter}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    verses = data.get("verses", [])
    if not verses:
        raise Exception("No verses")
    v = random.choice(verses)
    return {
        "source_name": "Bible",
        "source_reference": f"Proverbs {v['chapter']}:{v['verse']}",
        "original_text": None,
        "translation": v["text"].strip(),
        "character": None,
        "section": None,
        "chapter": v["chapter"],
        "verse": v["verse"],
    }


def fetch_live_quran() -> dict:
    ayah = random.randint(1, 6236)
    url = f"https://api.alquran.cloud/v1/ayah/{ayah}/en.asad"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()["data"]
    return {
        "source_name": "Quran",
        "source_reference": f"Surah {data['surah']['englishName']} {data['numberInSurah']}",
        "original_text": None,
        "translation": data["text"].strip(),
        "character": None,
        "section": data['surah']['englishName'],
        "chapter": data['surah']['number'],
        "verse": data['numberInSurah'],
    }


def fetch_live_spiritual_source() -> dict:
    fetchers = [fetch_live_gita, fetch_live_bible, fetch_live_quran]
    random.shuffle(fetchers)
    for fetcher in fetchers:
        try:
            return fetcher()
        except Exception as e:
            logger.warning(f"Live fetch failed: {e}")
            continue
    return None


def get_daily_spiritual_source(db: Session) -> SpiritualSource:
    """
    Attempts to fetch a live source from free APIs for infinite variety.
    If it fails, falls back to the database rotation.
    """
    try:
        live_data = fetch_live_spiritual_source()
        if live_data:
            topic = fallback_keyword_topic(live_data["translation"])
            # Check if this exact source already exists in DB
            existing = db.query(SpiritualSource).filter(
                SpiritualSource.source_reference == live_data["source_reference"]
            ).first()
            if existing:
                return existing

            new_source = SpiritualSource(
                source_name=live_data["source_name"],
                source_reference=live_data["source_reference"],
                chapter=live_data["chapter"],
                verse=live_data["verse"],
                character=live_data["character"],
                section=live_data["section"],
                original_text=live_data["original_text"],
                translation=live_data["translation"],
                topic=topic,
            )
            db.add(new_source)
            db.commit()
            db.refresh(new_source)
            return new_source
    except Exception as e:
        logger.error(f"Error saving live spiritual source: {e}")
        db.rollback()

    logger.warning("Falling back to database sources due to API failure.")
    all_sources = db.query(SpiritualSource).all()
    if not all_sources:
        return None

    recent_ids = get_recent_source_ids(db)
    fresh_sources = [s for s in all_sources if s.id not in recent_ids]

    if fresh_sources:
        return random.choice(fresh_sources)
    else:
        # All sources recently used — pick random
        return random.choice(all_sources)


def generate_with_groq(source: SpiritualSource) -> dict:
    import time
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise Exception("GROQ_API_KEY is not set.")

    try:
        from groq import Groq
        # Set explicit timeout for robustness
        client = Groq(api_key=api_key, timeout=30.0)
    except ImportError:
        raise Exception("Failed to import groq.")

    prompt = f"""You are an educational content writer specializing in Indian philosophy and literature.

The supplied source passage below is the AUTHORITATIVE source. You are NOT the author of the scripture.
Your task is to write an engaging, educational daily lesson based solely on this passage.

---
SOURCE DATA:
SOURCE: {source.source_name}
SECTION: {source.section or "N/A"}
REFERENCE: {source.source_reference}
CHARACTER/SPEAKER: {source.character or "N/A"}
ORIGINAL TEXT: {source.original_text or "N/A"}
TRANSLATION: {source.translation}
TOPIC: {source.topic}
---

STRICT RULES:
1. NEVER invent or modify scripture quotations, chapter numbers, verse numbers, or source references.
2. NEVER attribute content to a source unless it is supplied in SOURCE DATA above.
3. NEVER make religious claims that go beyond the supplied passage.
4. Do NOT persuade the user to follow any religion.
5. The "source" object in your response must use EXACTLY the values from SOURCE DATA.
6. Clearly distinguish the original source from your explanation.
7. Respect multiple interpretations and traditions.
8. Make the tone highly inspiring, profound, and deeply practical for a modern person.

YOUR TASK:
Write a rich, engaging daily lesson with these elements:
- A compelling reflection title (5-8 words)
- A detailed explanation (3-4 paragraphs) that includes:
  * The STORY CONTEXT: who is speaking, what is happening in the narrative at this moment
  * WHAT THE PASSAGE MEANS in clear, accessible modern language
  * WHY IT MATTERS: the deeper philosophical or psychological insight
- 3 to 4 specific, actionable key takeaways a modern person can apply today
- A practical daily exercise (not vague — be specific about what to do and when)
- A deep journaling question that challenges the reader to introspect honestly

Respond with ONLY a valid JSON object in this exact structure:
{{
    "topic": "{source.topic}",
    "source": {{
        "name": "{source.source_name}",
        "reference": "{source.source_reference}",
        "chapter": {source.chapter if source.chapter is not None else 'null'},
        "verse": {source.verse if source.verse is not None else 'null'}
    }},
    "reflection": {{
        "title": "A compelling, specific title for today's reflection",
        "explanation": "3-4 detailed paragraphs covering story context, meaning of the passage, and why it matters for modern life. Be specific and rich — avoid vague platitudes.",
        "key_takeaways": [
            "Specific, actionable takeaway 1",
            "Specific, actionable takeaway 2",
            "Specific, actionable takeaway 3",
            "Specific, actionable takeaway 4"
        ]
    }},
    "today_practice": {{
        "title": "A specific title for the daily practice",
        "description": "A specific, practical exercise — tell the reader exactly what to do, when, and for how long. Make it concrete and doable."
    }},
    "journal_prompt": "A deep, honest journaling question that challenges the reader to reflect specifically on this lesson in their own life."
}}"""

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an educational content writer. Output ONLY valid JSON, no markdown, no code blocks."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000
            )

            text_response = response.choices[0].message.content
            # Strip any accidental markdown wrappers
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "", 1)
            if text_response.endswith("```"):
                text_response = text_response.rsplit("```", 1)[0]

            return json.loads(text_response.strip())
        except Exception as e:
            logger.error(f"Groq generation failed on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise e


def build_lesson_response(lesson: DailySpiritualLesson) -> dict:
    src = lesson.source_passage
    return {
        "lesson_date": lesson.lesson_date,
        "topic": lesson.topic,
        "source": {
            "name": src.source_name,
            "reference": src.source_reference,
            "chapter": src.chapter,
            "verse": src.verse,
            "translation": src.translation,
            "character": src.character,
            "section": src.section,
        },
        "reflection": json.loads(lesson.reflection),
        "today_practice": json.loads(lesson.today_practice),
        "journal_prompt": lesson.journal_prompt
    }


def get_or_generate_daily_spiritual_lesson(db: Session) -> dict:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Return existing lesson if it was already generated today
    existing_lesson = db.query(DailySpiritualLesson).filter(
        DailySpiritualLesson.lesson_date == today_str
    ).first()

    if existing_lesson:
        logger.info(f"Returning cached lesson for {today_str}. Groq NOT called.")
        return build_lesson_response(existing_lesson)

    # 2. Select a source passage (rotation-aware)
    source = get_daily_spiritual_source(db)

    if not source:
        logger.warning("No sources in DB — returning fallback lesson.")
        fallback = FALLBACK_DATA.copy()
        fallback["lesson_date"] = today_str
        return fallback

    logger.info(f"Selected source: {source.source_reference} for {today_str}")

    # 3. Generate with Groq
    try:
        raw_data = generate_with_groq(source)

        # 4. Validate with Pydantic
        validated = GroqSpiritualLessonSchema.model_validate(raw_data)

        # 5. Save to DB
        new_lesson = DailySpiritualLesson(
            lesson_date=today_str,
            topic=validated.topic,
            source_id=source.id,
            reflection=json.dumps(validated.reflection.model_dump()),
            today_practice=json.dumps(validated.today_practice.model_dump()),
            journal_prompt=validated.journal_prompt
        )
        db.add(new_lesson)
        db.commit()
        db.refresh(new_lesson)

        # Use build_lesson_response so translation/character/section are always included
        result = build_lesson_response(new_lesson)
        logger.info(f"Generated and saved lesson for {today_str}: '{validated.reflection.title}'")
        return result

    except IntegrityError:
        # Race condition — another concurrent request beat us
        db.rollback()
        logger.warning("IntegrityError on lesson insert — concurrent request. Returning existing.")
        existing_lesson = db.query(DailySpiritualLesson).filter(
            DailySpiritualLesson.lesson_date == today_str
        ).first()
        if existing_lesson:
            return build_lesson_response(existing_lesson)

    except Exception as e:
        logger.error(f"Error during Groq generation or Pydantic validation: {e}")
        db.rollback()
        
    # Resilient fallback: Try to return the most recent lesson in DB
    logger.warning("Falling back to most recent DB lesson due to generation failure.")
    last_lesson = db.query(DailySpiritualLesson).order_by(DailySpiritualLesson.lesson_date.desc()).first()
    if last_lesson:
        return build_lesson_response(last_lesson)
        
    # Ultimate fallback if DB is empty
    logger.error("No recent DB lesson available. Using static FALLBACK_DATA.")
    fallback = FALLBACK_DATA.copy()
    fallback["lesson_date"] = today_str
    return fallback
