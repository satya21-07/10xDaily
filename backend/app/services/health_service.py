import os
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

FALLBACK_DATA = {
    "topic": "Optimizing Deep Sleep",
    "workout_of_the_day": {
        "name": "10-Minute Morning Mobility",
        "duration": "10 mins",
        "exercises": ["Neck Rolls (30s)", "Cat-Cow (1m)", "World's Greatest Stretch (2m)", "Deep Squat Hold (1m)"]
    },
    "health_facts": [
        {
            "title": "The Power of Deep Sleep",
            "explanation": "Deep sleep (slow-wave sleep) is when the body physically repairs itself, builds bone and muscle, and strengthens the immune system. Aim for 1.5 to 2 hours of it per night."
        },
        {
            "title": "Caffeine Half-Life",
            "explanation": "Caffeine has a half-life of about 5 hours. If you drink a coffee at 4 PM, half of that caffeine is still in your system at 9 PM, destroying your deep sleep architecture."
        }
    ],
    "diet_tip": "Stop eating at least 3 hours before bed. Digestion raises your core body temperature, which prevents you from entering deep sleep."
}

def generate_daily_health_lesson() -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_DATA

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return FALLBACK_DATA
    
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    topics = [
        "Hydration & Electrolytes", "HIIT vs Steady State Cardio", 
        "Gut Health & Microbiome", "Intermittent Fasting", 
        "Posture & Spine Health", "Managing Cortisol levels", "Macronutrients basics"
    ]
    topic_seed = topics[day_of_year % len(topics)]

    prompt = f"""
    You are an expert fitness coach and nutritionist.
    Generate a daily health/fitness lesson focused on the topic: {topic_seed}.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "topic": "{topic_seed}",
      "workout_of_the_day": {{
        "name": "A catchy workout name",
        "duration": "e.g., 15 mins",
        "exercises": ["Exercise 1 (time/reps)", "Exercise 2 (time/reps)"]
      }},
      "health_facts": [
        {{ "title": "Fact 1", "explanation": "Scientific but accessible explanation..." }},
        {{ "title": "Fact 2", "explanation": "Scientific but accessible explanation..." }}
      ],
      "diet_tip": "A quick, highly actionable nutrition tip."
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
        return json.loads(text_response.strip())
    except Exception as e:
        logger.error(f"Error generating Groq health lesson: {e}")
        return FALLBACK_DATA
