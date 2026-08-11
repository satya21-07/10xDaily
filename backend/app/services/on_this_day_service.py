import os
import json
import logging
import random
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

INDIA_TZ = ZoneInfo("Asia/Kolkata")
WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"

_cache = {}
_cache_date = None

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None

def fetch_wikipedia_events(month: str, day: str) -> list:
    url = WIKIPEDIA_API_URL.format(month=month, day=day)
    try:
        # Wikipedia requires a user-agent header
        headers = {"User-Agent": "10xDailyApp/1.0 (https://github.com/10xDaily)"}
        response = httpx.get(url, headers=headers, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            return data.get("events", [])
        else:
            logger.error(f"Wikipedia API error {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching from Wikipedia: {e}")
    return []

def enhance_event_with_groq(event: dict) -> dict:
    client = get_groq_client()
    if not client:
        return event

    prompt = f"""
    Rewrite the following historical event description to be concise and user-friendly. 
    Explain why this event is interesting or historically important.
    
    Event Year: {event.get('year')}
    Event Description: {event.get('text')}
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "title": "A short, engaging title for the event",
      "summary": "A concise 2-3 sentence explanation of what happened.",
      "why_it_matters": "A short explanation of why this event is historically important."
    }}
    
    IMPORTANT RULES:
    - Do NOT invent facts.
    - Do NOT change the year.
    - Do NOT change the core event.
    - Output ONLY JSON.
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=256
        )
        response_content = completion.choices[0].message.content
        
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
            
        data = json.loads(response_content.strip())
        
        event["enhanced_title"] = data.get("title")
        event["enhanced_summary"] = data.get("summary")
        event["why_it_matters"] = data.get("why_it_matters")
    except Exception as e:
        logger.error(f"Groq fallback failed for on_this_day: {e}")
        
    return event

def get_fallback_event(date_obj) -> dict:
    return {
        "date": date_obj.strftime("%Y-%m-%d"),
        "month": date_obj.month,
        "day": date_obj.day,
        "year": 1969,
        "title": "Apollo 11 Moon Landing",
        "description": "American astronauts Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon.",
        "category": "Science & Technology",
        "country": "World",
        "source_name": "Wikipedia",
        "source_url": "https://en.wikipedia.org/wiki/Apollo_11",
        "why_it_matters": "A monumental achievement in human history and space exploration."
    }

def get_on_this_day_event() -> dict:
    global _cache, _cache_date
    
    now = datetime.now(INDIA_TZ)
    current_date_str = now.strftime("%Y-%m-%d")
    
    if _cache_date == current_date_str and _cache:
        return _cache
        
    month_str = now.strftime("%m")
    day_str = now.strftime("%d")
    
    events = fetch_wikipedia_events(month_str, day_str)
    
    if not events:
        fallback = get_fallback_event(now)
        _cache = fallback
        _cache_date = current_date_str
        return fallback
        
    # Select a notable event.
    selected_event = random.choice(events)
    # Give priority to events with a "pages" array that is not empty
    pages = selected_event.get("pages", [])
    if not pages:
        for ev in events:
            if ev.get("pages"):
                selected_event = ev
                pages = ev.get("pages")
                break
                
    enhanced_event = enhance_event_with_groq(selected_event)
    
    source_name = "Wikipedia"
    source_url = None
    if pages:
        source_url = pages[0].get("content_urls", {}).get("desktop", {}).get("page")
        
    final_event = {
        "date": current_date_str,
        "month": now.month,
        "day": now.day,
        "year": enhanced_event.get("year", "Unknown Year"),
        "title": enhanced_event.get("enhanced_title") or f"Event in {enhanced_event.get('year')}",
        "description": enhanced_event.get("enhanced_summary") or enhanced_event.get("text"),
        "category": "History",
        "country": "World",
        "source_name": source_name,
        "source_url": source_url,
        "why_it_matters": enhanced_event.get("why_it_matters", "")
    }
    
    _cache = final_event
    _cache_date = current_date_str
    
    return final_event
