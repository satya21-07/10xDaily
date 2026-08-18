import os
import json
import logging
import random
import httpx
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.core_models import DailyOnThisDayEvent

load_dotenv()

logger = logging.getLogger(__name__)

INDIA_TZ = ZoneInfo("Asia/Kolkata")
WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"

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

def score_event(event: dict) -> float:
    """
    Score an event based on notability heuristics to prioritize major global 
    and audience-relevant historical events over minor or obscure ones.
    
    Heuristics:
    - Number of linked Wikipedia pages (more pages = more notable).
    - Presence of thumbnail images on linked pages.
    - Length of Wikipedia extracts.
    - Bonus points for matching keywords relevant to an Indian audience 
      (e.g., independence, republic day, gandhi, etc.).
    """
    score = 0.0
    pages = event.get("pages", [])
    
    score += len(pages) * 2.0
    
    for page in pages:
        if page.get("thumbnail"):
            score += 5.0
        extract = page.get("extract", "")
        score += len(extract) / 100.0
        
    india_power_terms = [
        "india", "indian", "republic day", "gandhi", "isro", 
        "space research", "kalam", "vivekananda", "bose", "shivaji", 
        "new delhi", "bombay", "mumbai"
    ]
    generic_history_terms = ["independence", "constitution", "prime minister", "president", "treaty"]
    
    text = event.get("text", "").lower()
    
    # Check for direct mentions in the main text
    for term in india_power_terms:
        if term in text:
            score += 300.0  # Massive boost for explicit India mentions
            
    for term in generic_history_terms:
        if term in text:
            score += 20.0
            
    for page in pages:
        title = page.get("title", "").lower()
        desc = page.get("description", "").lower()
        
        for term in india_power_terms:
            if term in title or term in desc:
                score += 150.0
                
        for term in generic_history_terms:
            if term in title or term in desc:
                score += 10.0
                
    return score

def get_top_candidate_events(events: list, top_n: int = 5) -> list:
    """
    Sort events by notability score descending and return the top N.
    """
    scored = [(score_event(e), e) for e in events]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for score, e in scored[:top_n]]

def choose_and_enhance_with_groq(candidates: list) -> dict:
    """
    We use Groq to make the final selection among the top candidate events because LLMs 
    are better at understanding the nuanced historical significance of events than raw 
    heuristics. Groq acts as a historian, picking the single most globally or locally 
    significant event from the top N candidates, and simultaneously writes an engaging 
    title, summary, and explanation of why it matters.
    """
    if not candidates:
        return {}
        
    client = get_groq_client()
    if not client:
        return candidates[0]
        
    candidates_text = ""
    for i, candidate in enumerate(candidates):
        candidates_text += f"[{i}] Year: {candidate.get('year')}\nText: {candidate.get('text')}\n\n"
        
    prompt = f"""
    You are a historian. From the following list of historical events, pick the SINGLE most historically 
    significant or broadly interesting one.
    
    CRITICAL INSTRUCTION: You are writing for an Indian audience. You MUST strongly prefer events that 
    represent powerful, positive, and major moments in Indian history (e.g., India's independence, 
    Indian achievements in science/space/culture, famous Indian leaders). If a major Indian event 
    is in the list, you MUST choose it over non-Indian events.
    
    Candidates:
    {candidates_text}
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "chosen_index": 0,
      "title": "A short, engaging title for the event",
      "summary": "A concise 2-3 sentence explanation of what happened.",
      "why_it_matters": "A short explanation of why this event is historically important."
    }}
    
    IMPORTANT RULES:
    - Do NOT invent facts.
    - Do NOT change the year.
    - Do NOT change the core event.
    - chosen_index MUST be between 0 and {len(candidates) - 1}.
    - Output ONLY JSON.
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            temperature=0.3,
            max_tokens=512
        )
        response_content = completion.choices[0].message.content
        
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
            
        data = json.loads(response_content.strip())
        
        chosen_index = data.get("chosen_index", 0)
        if not isinstance(chosen_index, int) or chosen_index < 0 or chosen_index >= len(candidates):
            chosen_index = 0
            
        chosen_event = candidates[chosen_index].copy()
        chosen_event["enhanced_title"] = data.get("title")
        chosen_event["enhanced_summary"] = data.get("summary")
        chosen_event["why_it_matters"] = data.get("why_it_matters")
        return chosen_event
        
    except Exception as e:
        logger.error(f"Groq selection/enhancement failed: {e}")
        return candidates[0]

def get_fallback_event(date_obj) -> dict:
    return {
        "date": date_obj.strftime("%Y-%m-%d"),
        "month": date_obj.month,
        "day": date_obj.day,
        "year": "1969",
        "title": "Apollo 11 Moon Landing",
        "description": "American astronauts Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon.",
        "category": "Science & Technology",
        "country": "World",
        "source_name": "Wikipedia",
        "source_url": "https://en.wikipedia.org/wiki/Apollo_11",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Apollo_11_first_step.jpg/440px-Apollo_11_first_step.jpg",
        "why_it_matters": "A monumental achievement in human history and space exploration."
    }

def get_on_this_day_event(db: Session) -> dict:
    now = datetime.now(INDIA_TZ)
    current_date_str = now.strftime("%Y-%m-%d")
    
    # 1. Return existing event if it was already generated today
    existing_event = db.query(DailyOnThisDayEvent).filter(
        DailyOnThisDayEvent.date == current_date_str
    ).first()
    
    if existing_event:
        return {
            "date": existing_event.date,
            "month": existing_event.month,
            "day": existing_event.day,
            "year": existing_event.year,
            "title": existing_event.title,
            "description": existing_event.description,
            "category": existing_event.category,
            "country": existing_event.country,
            "source_name": existing_event.source_name,
            "source_url": existing_event.source_url,
            "image_url": existing_event.image_url,
            "why_it_matters": existing_event.why_it_matters
        }
        
    month_str = now.strftime("%m")
    day_str = now.strftime("%d")
    
    events = fetch_wikipedia_events(month_str, day_str)
    
    if not events:
        final_event_dict = get_fallback_event(now)
    else:
        # Get top candidates and enhance
        candidates = get_top_candidate_events(events, top_n=5)
        enhanced_event = choose_and_enhance_with_groq(candidates)
        
        pages = enhanced_event.get("pages", [])
        source_name = "Wikipedia"
        source_url = None
        image_url = None
        if pages:
            source_url = pages[0].get("content_urls", {}).get("desktop", {}).get("page")
            if pages[0].get("originalimage"):
                image_url = pages[0].get("originalimage").get("source")
            elif pages[0].get("thumbnail"):
                image_url = pages[0].get("thumbnail").get("source")
            
        fallback_title = f"Event in {enhanced_event.get('year')}"
        if pages:
            fallback_title = pages[0].get("normalizedtitle") or pages[0].get("title", "").replace("_", " ")
            if not fallback_title:
                fallback_title = f"Event in {enhanced_event.get('year')}"
                
        final_event_dict = {
            "date": current_date_str,
            "month": now.month,
            "day": now.day,
            "year": str(enhanced_event.get("year", "Unknown Year")),
            "title": enhanced_event.get("enhanced_title") or fallback_title,
            "description": enhanced_event.get("enhanced_summary") or enhanced_event.get("text"),
            "category": "History",
            "country": "World",
            "source_name": source_name,
            "source_url": source_url,
            "image_url": image_url,
            "why_it_matters": enhanced_event.get("why_it_matters", "")
        }
        
    try:
        new_event = DailyOnThisDayEvent(
            date=final_event_dict["date"],
            month=final_event_dict["month"],
            day=final_event_dict["day"],
            year=final_event_dict["year"],
            title=final_event_dict["title"],
            description=final_event_dict["description"],
            category=final_event_dict["category"],
            country=final_event_dict["country"],
            source_name=final_event_dict["source_name"],
            source_url=final_event_dict["source_url"],
            image_url=final_event_dict["image_url"],
            why_it_matters=final_event_dict["why_it_matters"]
        )
        db.add(new_event)
        db.commit()
    except IntegrityError:
        # Race condition
        db.rollback()
        logger.warning("IntegrityError on on_this_day insert — concurrent request. Returning existing.")
        existing_event = db.query(DailyOnThisDayEvent).filter(
            DailyOnThisDayEvent.date == current_date_str
        ).first()
        if existing_event:
            return {
                "date": existing_event.date,
                "month": existing_event.month,
                "day": existing_event.day,
                "year": existing_event.year,
                "title": existing_event.title,
                "description": existing_event.description,
                "category": existing_event.category,
                "country": existing_event.country,
                "source_name": existing_event.source_name,
                "source_url": existing_event.source_url,
                "image_url": existing_event.image_url,
                "why_it_matters": existing_event.why_it_matters
            }
    except Exception as e:
        logger.error(f"Error generating daily on this day event: {e}")
        db.rollback()

    return final_event_dict
