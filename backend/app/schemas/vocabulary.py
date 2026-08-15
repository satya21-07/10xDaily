from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone

class DefinitionItem(BaseModel):
    part_of_speech: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None

class VocabularyWordBase(BaseModel):
    word: str
    definitions: Optional[List[DefinitionItem]] = []
    part_of_speech: Optional[List[str]] = []
    pronunciation: Optional[str] = None
    audio_url: Optional[str] = None
    synonyms: Optional[List[str]] = []
    antonyms: Optional[List[str]] = []
    origin: Optional[str] = None
    difficulty: Optional[str] = "Medium"
    usage_tips: Optional[str] = None
    source: Optional[str] = "free_dictionary"
    
    # Backwards compatibility
    meaning: Optional[str] = None
    example: Optional[str] = None
    
    # For user progress in UI
    bookmarked: Optional[bool] = False
    learned: Optional[bool] = False

class VocabularyWordCreate(VocabularyWordBase):
    pass

class VocabularyWordUpdate(VocabularyWordBase):
    word: Optional[str] = None

class VocabularyWordInDBBase(VocabularyWordBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VocabularyWord(VocabularyWordInDBBase):
    pass

class DailyVocabularyResponse(BaseModel):
    date: str
    total: int
    words: List[VocabularyWord]

class VocabularyGroqFallbackSchema(BaseModel):
    example: Optional[str] = None
    synonyms: Optional[List[str]] = Field(default_factory=list)
    antonyms: Optional[List[str]] = Field(default_factory=list)
