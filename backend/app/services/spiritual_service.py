import os
import json
import logging
import random
from datetime import datetime, timezone
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


def get_daily_spiritual_source(db: Session) -> SpiritualSource:
    """
    Selects a source passage using weighted random rotation:
    - Prefer sources NOT recently used.
    - If all have been used, pick any random source.
    - Ensures variety across Bhagavad Gita, Ramayana, and Mahabharata.
    """
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
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise Exception("GROQ_API_KEY is not set.")

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
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

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are an educational content writer. Output ONLY valid JSON, no markdown, no code blocks."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    text_response = response.choices[0].message.content
    # Strip any accidental markdown wrappers
    if text_response.startswith("```json"):
        text_response = text_response.replace("```json", "", 1)
    if text_response.endswith("```"):
        text_response = text_response.rsplit("```", 1)[0]

    return json.loads(text_response.strip())


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
        # Shouldn't happen, but fall through to fallback
        fallback = FALLBACK_DATA.copy()
        fallback["lesson_date"] = today_str
        return fallback

    except Exception as e:
        logger.error(f"Error generating daily spiritual lesson: {e}")
        db.rollback()
        fallback = FALLBACK_DATA.copy()
        fallback["lesson_date"] = today_str
        return fallback
