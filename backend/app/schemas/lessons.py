from typing import Optional
from pydantic import BaseModel

class FinanceLessonBase(BaseModel):
    topic: str
    problem: Optional[str] = None
    solution: Optional[str] = None
    example: Optional[str] = None
    calculator_type: Optional[str] = None

class FinanceLesson(FinanceLessonBase):
    id: int
    class Config: from_attributes = True

class HealthLessonBase(BaseModel):
    category: Optional[str] = None
    title: str
    advice: Optional[str] = None
    scientific_evidence: Optional[str] = None
    action_step: Optional[str] = None

class HealthLesson(HealthLessonBase):
    id: int
    class Config: from_attributes = True

class SpiritualLessonBase(BaseModel):
    source_text: Optional[str] = None
    story: Optional[str] = None
    meaning: Optional[str] = None
    context: Optional[str] = None
    modern_example: Optional[str] = None
    reflection: Optional[str] = None

class SpiritualLesson(SpiritualLessonBase):
    id: int
    class Config: from_attributes = True
