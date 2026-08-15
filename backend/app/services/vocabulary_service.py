import httpx
import random
import logging
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from app.models.vocabulary import VocabularyWord, DailyVocabulary
from app.utils.curated_words import CURATED_WORDS
import os
import asyncio

logger = logging.getLogger(__name__)

INDIA_TZ = ZoneInfo("Asia/Kolkata")
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

# Import Groq for AI fallback
try:
    from groq import Groq
except ImportError:
    Groq = None

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here" or Groq is None:
        return None
    return Groq(api_key=api_key)

def fetch_word_definition(word: str) -> dict:
    """Fetch the definition of a word from the Free Dictionary API."""
    try:
        response = httpx.get(DICTIONARY_API_URL.format(word), timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                return data[0]
        elif response.status_code == 404:
            logger.warning(f"Word '{word}' not found in dictionary.")
        elif response.status_code == 429:
            logger.warning(f"Rate limited by dictionary API for '{word}'.")
        else:
            logger.error(f"Dictionary API error {response.status_code} for '{word}'.")
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching definition for {word}.")
    except httpx.RequestError as e:
        logger.error(f"Connection error fetching definition for {word}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching definition for {word}: {e}")
    return None

def fallback_groq_completion(word: str, needs_example: bool, needs_synonyms: bool, needs_antonyms: bool) -> dict:
    """Use Groq to generate missing example, synonyms, or antonyms."""
    client = get_groq_client()
    if not client:
        return {}
        
    prompt = f"Provide information for the vocabulary word '{word}'. "
    
    requirements = []
    if needs_example:
        requirements.append("a natural, highly useful example sentence clearly demonstrating the word's meaning")
    if needs_synonyms:
        requirements.append("a list of up to 5 genuine synonyms (empty list if none exist)")
    if needs_antonyms:
        requirements.append("a list of up to 5 genuine antonyms (empty list if none exist)")
        
    prompt += "I need " + ", and ".join(requirements) + ". "
    prompt += "Return the response strictly as a JSON object with the keys: "
    if needs_example:
        prompt += "'example' (string), "
    if needs_synonyms:
        prompt += "'synonyms' (list of strings), "
    if needs_antonyms:
        prompt += "'antonyms' (list of strings). "
    prompt += "Do NOT wrap in markdown. Output ONLY valid JSON."
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=256
        )
        response_content = completion.choices[0].message.content
        
        # simple json cleaning if it has markdown formatting
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
            
        data = json.loads(response_content.strip())
        return data
    except Exception as e:
        logger.error(f"Groq fallback failed for '{word}': {e}")
        return {}

def process_dictionary_data(word: str, data: dict) -> dict:
    """Process the dictionary API response into our DB model format."""
    phonetics = data.get("phonetics", [])
    pronunciation = None
    audio_url = None
    for p in phonetics:
        if p.get("text") and not pronunciation:
            pronunciation = p.get("text")
        if p.get("audio") and not audio_url:
            audio_url = p.get("audio")
            
    meanings = data.get("meanings", [])
    
    definitions = []
    part_of_speech_set = set()
    all_synonyms = []
    all_antonyms = []
    
    for m in meanings:
        pos = m.get("partOfSpeech")
        if pos:
            part_of_speech_set.add(pos)
            
        all_synonyms.extend(m.get("synonyms", []))
        all_antonyms.extend(m.get("antonyms", []))
        
        for d in m.get("definitions", []):
            definitions.append({
                "part_of_speech": pos,
                "definition": d.get("definition", "No definition available."),
                "example": d.get("example")
            })
            all_synonyms.extend(d.get("synonyms", []))
            all_antonyms.extend(d.get("antonyms", []))
                
    # Deduplicate preserving order
    synonyms = list(dict.fromkeys(all_synonyms))[:5]
    antonyms = list(dict.fromkeys(all_antonyms))[:5]
    part_of_speech = list(part_of_speech_set)
    
    # Check what is missing to determine if Groq fallback is needed
    needs_example = all([not d.get("example") for d in definitions]) if definitions else True
    needs_synonyms = len(synonyms) == 0
    needs_antonyms = len(antonyms) == 0
    
    if (needs_example or needs_synonyms or needs_antonyms):
        groq_data = fallback_groq_completion(word, needs_example, needs_synonyms, needs_antonyms)
        if needs_example and groq_data.get("example"):
            if definitions:
                definitions[0]["example"] = groq_data.get("example")
            else:
                definitions.append({"part_of_speech": None, "definition": "No definition available.", "example": groq_data.get("example")})
        if needs_synonyms and isinstance(groq_data.get("synonyms"), list):
            synonyms = list(dict.fromkeys(groq_data.get("synonyms")))[:5]
        if needs_antonyms and isinstance(groq_data.get("antonyms"), list):
            antonyms = list(dict.fromkeys(groq_data.get("antonyms")))[:5]
    
    return {
        "word": word,
        "definitions": definitions,
        "part_of_speech": part_of_speech,
        "pronunciation": pronunciation,
        "audio_url": audio_url,
        "synonyms": synonyms,
        "antonyms": antonyms,
        "difficulty": "Hard",
        "origin": data.get("origin"),
        "source": "free_dictionary"
    }

def get_today_date_in_india():
    return datetime.now(INDIA_TZ).date()

def generate_new_word(db: Session, available_words: list, existing_words: set) -> VocabularyWord:
    """Generate a single new valid word and save it to DB."""
    while available_words:
        # Pop random word
        word = available_words.pop(random.randrange(len(available_words)))
        
        if word in existing_words:
            continue
            
        data = fetch_word_definition(word)
        if data:
            processed = process_dictionary_data(word, data)
            # Ensure it has at least one definition
            if processed.get("definitions"):
                word_obj = VocabularyWord(**processed)
                db.add(word_obj)
                try:
                    db.commit()
                    db.refresh(word_obj)
                    existing_words.add(word)
                    return word_obj
                except IntegrityError:
                    db.rollback()
                    # It was added concurrently
                    existing = db.query(VocabularyWord).filter(VocabularyWord.word == word).first()
                    if existing:
                        return existing
                    continue
    return None

def get_or_generate_daily_words(db: Session, limit: int = 10) -> list[VocabularyWord]:
    """Get today's words or generate them if they don't exist yet."""
    
    today = get_today_date_in_india()
    cache_key = f"vocabulary:today:{today}"
            
    # 2. Check DB Daily mapping
    daily_mappings = db.query(DailyVocabulary).filter(DailyVocabulary.date == today).order_by(DailyVocabulary.position).all()
    
    words = []
    if len(daily_mappings) >= limit:
        for m in daily_mappings[:limit]:
            words.append(m.word)
        return words
        
    # We need to generate missing words
    needed = limit - len(daily_mappings)
    current_position = len(daily_mappings) + 1
    
    existing_words = {w[0] for w in db.query(VocabularyWord.word).all()}
    available_words = [w for w in CURATED_WORDS if w not in existing_words]
    
    for _ in range(needed):
        new_word_obj = generate_new_word(db, available_words, existing_words)
        if new_word_obj:
            # Map to today
            daily_vocab = DailyVocabulary(date=today, word_id=new_word_obj.id, position=current_position)
            db.add(daily_vocab)
            try:
                db.commit()
                words.append(new_word_obj)
                current_position += 1
            except IntegrityError:
                db.rollback()
                # Concurrent insertion might have happened, let's fetch it
                existing_mapping = db.query(DailyVocabulary).filter(DailyVocabulary.date == today, DailyVocabulary.position == current_position).first()
                if existing_mapping:
                    words.append(existing_mapping.word)
                    current_position += 1
                    
    # Cache the result in Redis for fast API response if we were doing dicts
    # but since this returns objects, the API layer could cache the serialized form.
    # We will let the API layer handle the caching so it caches the exact JSON string.

    # Combine existing mappings and newly created ones
    final_words = []
    final_mappings = db.query(DailyVocabulary).filter(DailyVocabulary.date == today).order_by(DailyVocabulary.position).all()
    for m in final_mappings[:limit]:
        final_words.append(m.word)
        
    return final_words

