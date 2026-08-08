import httpx
import random
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.vocabulary import VocabularyWord
from app.utils.curated_words import CURATED_WORDS

logger = logging.getLogger(__name__)

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

def fetch_word_definition(word: str) -> dict:
    """Fetch the definition of a word from the Free Dictionary API."""
    try:
        response = httpx.get(DICTIONARY_API_URL.format(word), timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                return data[0]
    except Exception as e:
        logger.error(f"Error fetching definition for {word}: {e}")
    return None

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
    meaning_text = ""
    example_text = None
    synonyms = []
    antonyms = []
    
    if meanings:
        # Get first meaning definition
        def_obj = meanings[0].get("definitions", [{}])[0]
        meaning_text = def_obj.get("definition", "No definition found.")
        example_text = def_obj.get("example")
        
        # Collect synonyms and antonyms from all meanings
        for m in meanings:
            synonyms.extend(m.get("synonyms", []))
            antonyms.extend(m.get("antonyms", []))
            for d in m.get("definitions", []):
                synonyms.extend(d.get("synonyms", []))
                antonyms.extend(d.get("antonyms", []))
                
    # Deduplicate and format
    synonyms = list(set(synonyms))[:5]
    antonyms = list(set(antonyms))[:5]
    
    return {
        "word": word,
        "meaning": meaning_text,
        "pronunciation": pronunciation,
        "audio_url": audio_url,
        "synonyms": ", ".join(synonyms) if synonyms else None,
        "antonyms": ", ".join(antonyms) if antonyms else None,
        "example": example_text,
        "difficulty": "Hard", # Our curated list is mostly Hard/GRE level
        "origin": data.get("origin")
    }

def get_or_generate_daily_words(db: Session, limit: int = 10) -> list[VocabularyWord]:
    """Get today's words or generate them if they don't exist yet."""
    # Check if we already have enough words generated today
    # We define 'today' using UTC date
    today = datetime.now(timezone.utc).date()
    
    # Simple check: let's see how many words were created today
    # For a real app, we might want a separate DailyWord mapping table, 
    # but for simplicity, we just look at the latest 10 words added.
    
    latest_words = db.query(VocabularyWord).order_by(VocabularyWord.created_at.desc()).limit(limit).all()
    
    # If we have 10 words and they were created today, return them
    if len(latest_words) == limit and latest_words[0].created_at.date() == today:
        return latest_words
        
    # Otherwise, we need to fetch new words
    # Get all existing words to avoid duplicates
    existing_words = {w.word for w in db.query(VocabularyWord.word).all()}
    
    available_words = [w for w in CURATED_WORDS if w not in existing_words]
    
    # If we run out of curated words, just pick randomly from existing
    if not available_words:
        # We could implement a fallback or reset the list, but for now just return the latest 10
        return latest_words if latest_words else []
        
    # Randomly select words to process
    num_to_pick = min(limit, len(available_words))
    words_to_fetch = random.sample(available_words, num_to_pick)
    
    new_word_objs = []
    for word in words_to_fetch:
        data = fetch_word_definition(word)
        if data:
            processed = process_dictionary_data(word, data)
            word_obj = VocabularyWord(**processed)
            db.add(word_obj)
            new_word_objs.append(word_obj)
        else:
            # Fallback if API fails
            word_obj = VocabularyWord(
                word=word, 
                meaning="A challenging vocabulary word.",
                difficulty="Hard"
            )
            db.add(word_obj)
            new_word_objs.append(word_obj)
            
    db.commit()
    for obj in new_word_objs:
        db.refresh(obj)
        
    return new_word_objs
