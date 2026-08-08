import os
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

FALLBACK_DATA = {
    "topic": "Dharma and Duty",
    "quote": "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. - Bhagavad Gita",
    "learnings": [
        {
            "source": "Mahabharat",
            "title": "The Consequence of Ego",
            "explanation": "Duryodhana's ego and refusal to share even a needlepoint of land led to the destruction of his entire lineage. Ego blinds us to reason and compassion."
        },
        {
            "source": "Ramayana",
            "title": "Unwavering Devotion",
            "explanation": "Hanuman's absolute devotion to Lord Rama demonstrates that when action is fueled by pure love and surrender, even mountains can be moved."
        },
        {
            "source": "Bhagavad Gita",
            "title": "Nishkama Karma",
            "explanation": "Do your duty without attachment to the outcome. When you detach from success or failure, you perform with absolute clarity and peace."
        }
    ],
    "journal_prompt": "Are my current actions driven by ego (Ahankar) or by a sense of righteous duty (Dharma)?"
}

def generate_daily_spiritual_lesson() -> dict:
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
        "Karma and Consequence", "Dharma (Righteous Duty)", 
        "Detachment from Outcomes", "The Illusion of Ego", 
        "Devotion and Surrender", "Overcoming Inner Demons", "Focus and Clarity"
    ]
    topic_seed = topics[day_of_year % len(topics)]

    prompt = f"""
    You are a wise spiritual guide deeply rooted in ancient Indian philosophy and epics.
    Generate a daily spiritual lesson focused on the topic: {topic_seed}.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "topic": "{topic_seed}",
      "quote": "A profound quote from ancient Indian scriptures related to the topic.",
      "learnings": [
        {{ "source": "Mahabharat", "title": "A core lesson from Mahabharat on this topic", "explanation": "Detailed explanation..." }},
        {{ "source": "Ramayana", "title": "A core lesson from Ramayana on this topic", "explanation": "Detailed explanation..." }},
        {{ "source": "Bhagavad Gita", "title": "A core lesson from Bhagavad Gita on this topic", "explanation": "Detailed explanation..." }}
      ],
      "journal_prompt": "A deep, introspective journaling question for the user to reflect on today."
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
        logger.error(f"Error generating Groq spiritual lesson: {e}")
        return FALLBACK_DATA
