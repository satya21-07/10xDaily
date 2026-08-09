from typing import List, Optional
from pydantic import BaseModel

class SourceMetadataSchema(BaseModel):
    name: str
    reference: str
    chapter: Optional[int] = None
    verse: Optional[int] = None
    translation: Optional[str] = None   # The actual scripture passage text
    character: Optional[str] = None     # Speaker / character (e.g. Krishna, Hanuman)
    section: Optional[str] = None       # e.g. Sundara Kanda, Chapter 2

class ReflectionSchema(BaseModel):
    title: str
    explanation: str
    key_takeaways: List[str]

class TodayPracticeSchema(BaseModel):
    title: str
    description: str

class GroqSpiritualLessonSchema(BaseModel):
    topic: str
    source: SourceMetadataSchema
    reflection: ReflectionSchema
    today_practice: TodayPracticeSchema
    journal_prompt: str

class DailySpiritualLessonResponse(GroqSpiritualLessonSchema):
    lesson_date: str

class SpiritualSourceSchema(BaseModel):
    id: int
    source_name: str
    section: Optional[str]
    chapter: Optional[int]
    verse: Optional[int]
    character: Optional[str]
    topic: str
    original_text: Optional[str]
    translation: str
    source_reference: str
    source_url: Optional[str]
    translation_name: Optional[str]
    language: str
    license_or_rights_note: Optional[str]

    class Config:
        from_attributes = True
