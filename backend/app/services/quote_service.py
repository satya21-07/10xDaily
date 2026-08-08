import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

FALLBACK_QUOTE = {
    "text": "10x results require 10x thinking. Break the limits of what you believe is possible.",
    "author": "Antigravity AI"
}

def generate_random_quote() -> dict:
    """Uses Groq API to generate a unique, highly motivational 10x style quote."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_QUOTE

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return FALLBACK_QUOTE
    
    prompt = """
    Generate a highly motivational, intense, "10x mentality" quote about productivity, coding, or success. 
    It must be a completely unique quote that you invent right now. Do not use famous existing quotes.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {
      "text": "The motivational quote here...",
      "author": "A cool sounding fictional author name or 'Anonymous'"
    }
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a highly motivational AI that strictly outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        text_response = response.choices[0].message.content
        return json.loads(text_response.strip())
    except Exception as e:
        logger.error(f"Error generating Groq quote: {e}")
        return FALLBACK_QUOTE
