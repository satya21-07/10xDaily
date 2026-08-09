import os
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.schemas.health import DailyHealthLessonCreate, DailyHealthLesson
from app.models.lessons import DailyHealthLesson as DailyHealthLessonModel
from app.services.health_sources.nutrition import ExcelNutritionSource

logger = logging.getLogger(__name__)

FALLBACK_DATA = {
    "topic": "Hydration basics",
    "learning_objective": "Understand the importance of hydration.",
    "health_facts": [
        {
            "title": "Water and energy",
            "explanation": "Dehydration can significantly reduce your energy levels.",
            "key_points": ["Drink water", "Stay hydrated"]
        }
    ],
    "daily_activity": {
        "name": "Stretching",
        "duration": "5 mins",
        "level": "Beginner",
        "exercises": [
            {
                "name": "Neck rolls",
                "duration": "1 min",
                "instructions": "Roll your neck slowly.",
                "safety_note": "Stop if you feel pain."
            }
        ]
    },
    "nutrition_tip": {
        "title": "Drink a glass of water right when you wake up.",
        "description": "It helps kickstart your metabolism, flushes out toxins that have accumulated overnight, and gives your brain the hydration it needs to stay focused.",
        "featured_foods": [
            {
                "name": "Water",
                "calories": "0 kcal",
                "protein": "0g",
                "carbs": "0g",
                "fat": "0g",
                "fiber": "0g"
            }
        ]
    },
    "daily_habit": {
        "title": "Carry a water bottle",
        "description": "Keep it with you all day."
    },
    "source": {
        "name": "10xDaily General Wellness",
        "url": "",
        "type": "fallback",
        "retrieved_at": ""
    },
    "disclaimer": "This content is for general educational purposes and is not medical advice."
}

import random

def fetch_source_data(topic_seed: str):
    source = ExcelNutritionSource()
    
    # Try fetching based on topic first
    data = source.fetch_data(topic_seed)
    
    # If topic doesn't yield a food, pick a random common healthy food to feature
    if not data:
        common_foods = ["Apple", "Banana", "Almonds", "Oats", "Spinach", "Broccoli", "Chicken", "Salmon", "Eggs", "Yogurt", "Lentils", "Walnuts", "Quinoa", "Avocado", "Sweet Potato"]
        random_food = random.choice(common_foods)
        data = source.fetch_data(random_food)
        
    metadata = source.get_source_metadata()
    return data, metadata

def generate_health_lesson(topic_seed: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_DATA

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return FALLBACK_DATA

    source_data, source_metadata = fetch_source_data(topic_seed)
    
    source_context = ""
    if source_data:
        source_context = f"""
SOURCE:
{source_metadata.get('name')}

TOPIC:
{topic_seed}

SOURCE DATA:
{json.dumps(source_data, indent=2)}
"""

    prompt = f"""
You are an educational health and wellness content generator.

Use the supplied source data as the factual basis for this lesson if provided.
Do not invent numerical nutritional values.
Do not change values supplied by the source.
Do not diagnose diseases.
Do not claim that a food, supplement, exercise, or habit can cure or prevent a disease.
Do not provide individualized medical treatment.
Avoid fear-based or sensational language.
Use simple language suitable for a general audience.
Clearly distinguish factual information from general wellness suggestions.

You MUST make the explanations highly detailed, informative, and engaging. Go deep into the science in a way that is easy to understand. Do not provide brief, one-sentence explanations. 
Provide at least 3 comprehensive health facts.
If source data is provided for specific foods, include 1-2 of them in the "featured_foods" array inside the "nutrition_tip" object.

Topic for today: {topic_seed}

{source_context}

You MUST respond with ONLY a valid JSON object matching this exact structure:
{{
  "topic": "...",
  "learning_objective": "...",
  "health_facts": [
    {{
      "title": "...",
      "explanation": "...",
      "key_points": ["...", "..."]
    }}
  ],
  "daily_activity": {{
    "name": "...",
    "duration": "...",
    "level": "Beginner",
    "exercises": [
      {{
        "name": "...",
        "duration": "...",
        "instructions": "...",
        "safety_note": "..."
      }}
    ]
  }},
  "nutrition_tip": {{
    "title": "...",
    "description": "...",
    "featured_foods": [
      {{
        "name": "...",
        "calories": "...",
        "protein": "...",
        "carbs": "...",
        "fat": "...",
        "fiber": "..."
      }}
    ]
  }},
  "daily_habit": {{
    "title": "...",
    "description": "..."
  }},
  "source": {{
    "name": "{source_metadata.get('name') if source_metadata else 'General Knowledge'}",
    "url": "{source_metadata.get('url') if source_metadata else ''}",
    "type": "{source_metadata.get('type') if source_metadata else 'general'}",
    "retrieved_at": "{source_metadata.get('retrieved_at') if source_metadata else datetime.now(timezone.utc).isoformat()}"
  }},
  "disclaimer": "This content is for general educational purposes and is not medical advice."
}}
Ensure the JSON is perfectly formatted and contains no markdown code blocks outside of the raw JSON itself.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that strictly outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        text_response = response.choices[0].message.content
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response.rsplit("```", 1)[0]
        
        parsed_json = json.loads(text_response.strip())
        # Validate with Pydantic
        DailyHealthLessonCreate(**parsed_json)
        return parsed_json
    except ValidationError as e:
        logger.error(f"Pydantic validation error for Groq health lesson: {e}")
        return FALLBACK_DATA
    except Exception as e:
        logger.error(f"Error generating Groq health lesson: {e}")
        return FALLBACK_DATA

def get_or_generate_daily_health_lesson(db: Session) -> DailyHealthLesson:
    today = datetime.now(timezone.utc).date()
    
    # Check existing
    existing = db.query(DailyHealthLessonModel).filter(DailyHealthLessonModel.lesson_date == today).first()
    if existing:
        return DailyHealthLesson.from_orm(existing)

    # Generate new
    topics = [
        "Hydration", "Sleep & Recovery", "Daily Movement", "Walking",
        "Strength Training Basics", "Mobility & Flexibility", "Posture & Ergonomics",
        "Balanced Nutrition", "Protein", "Fiber", "Fruits & Vegetables",
        "Healthy Eating Habits", "Stress Management", "Mindfulness", "Screen Time",
        "Digital Wellness", "Healthy Daily Routines", "Rest & Recovery",
        "Outdoor Activity", "Workplace Wellness", "Sustainable Habits"
    ]
    day_of_year = today.timetuple().tm_yday
    topic_seed = topics[day_of_year % len(topics)]
    
    lesson_data = generate_health_lesson(topic_seed)
    
    # Save to db
    db_lesson = DailyHealthLessonModel(
        lesson_date=today,
        topic=lesson_data["topic"],
        learning_objective=lesson_data["learning_objective"],
        health_facts=lesson_data["health_facts"],
        daily_activity=lesson_data["daily_activity"],
        nutrition_tip=lesson_data["nutrition_tip"],
        daily_habit=lesson_data["daily_habit"],
        source_name=lesson_data["source"]["name"],
        source_url=lesson_data["source"]["url"],
        source_type=lesson_data["source"]["type"],
        source_retrieved_at=lesson_data["source"]["retrieved_at"],
        disclaimer=lesson_data["disclaimer"]
    )
    
    try:
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return DailyHealthLesson.from_orm(db_lesson)
    except IntegrityError:
        db.rollback()
        # If another process already inserted it
        existing = db.query(DailyHealthLessonModel).filter(DailyHealthLessonModel.lesson_date == today).first()
        if existing:
            return DailyHealthLesson.from_orm(existing)
        raise
