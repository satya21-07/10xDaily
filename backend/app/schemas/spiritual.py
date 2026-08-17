from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SpiritualCommentary(BaseModel):
    author: str
    text: str

class ScriptureSourceDetail(BaseModel):
    name: str                           # e.g. "Bhagavad Gita", "Valmiki Ramayana", "Vyasa Mahabharata"
    scripture_type: str                 # "gita" | "ramayana" | "mahabharata"
    reference: str                      # e.g. "Bhagavad Gita 2.47" or "Bala Kanda 1.1"
    chapter: Optional[int] = None
    verse: Optional[int] = None
    kanda_or_parva: Optional[str] = None
    character: Optional[str] = None     # Speaker / character (e.g. Krishna, Arjuna, Rama, Hanuman, Bhishma)
    original_sanskrit: Optional[str] = None
    transliteration: Optional[str] = None
    translation: str                    # English translation
    hindi_translation: Optional[str] = None # हिन्दी अनुवाद
    commentators: Optional[Dict[str, str]] = None


class ReflectionSchema(BaseModel):
    title: str
    story_context: Optional[str] = None
    explanation: str
    key_takeaways: List[str]

class TodayPracticeSchema(BaseModel):
    title: str
    description: str

class DailySpiritualLessonResponse(BaseModel):
    lesson_date: str
    day_number: int
    total_days_or_verses: int
    topic: str
    source: ScriptureSourceDetail
    reflection: ReflectionSchema
    today_practice: TodayPracticeSchema
    journal_prompt: str

class SpiritualProgressSchema(BaseModel):
    scripture: str
    current_day: int
    total_items: int
    last_studied_date: Optional[str] = None

