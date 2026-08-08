from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class VocabularyWordBase(BaseModel):
    word: str
    meaning: str
    pronunciation: Optional[str] = None
    audio_url: Optional[str] = None
    synonyms: Optional[str] = None
    antonyms: Optional[str] = None
    origin: Optional[str] = None
    example: Optional[str] = None
    difficulty: Optional[str] = "Medium"
    usage_tips: Optional[str] = None

class VocabularyWordCreate(VocabularyWordBase):
    pass

class VocabularyWordUpdate(VocabularyWordBase):
    word: Optional[str] = None
    meaning: Optional[str] = None

class VocabularyWordInDBBase(VocabularyWordBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VocabularyWord(VocabularyWordInDBBase):
    pass
