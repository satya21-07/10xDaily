from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone

class CodingProblemBase(BaseModel):
    title: str
    description: str
    difficulty: Optional[str] = "Medium"
    pattern: Optional[str] = None
    tags: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    hint: Optional[str] = None
    approach: Optional[str] = None
    explanation: Optional[str] = None
    java_solution: Optional[str] = None
    python_solution: Optional[str] = None
    cpp_solution: Optional[str] = None
    javascript_solution: Optional[str] = None

class CodingProblemCreate(CodingProblemBase):
    pass

class CodingProblem(CodingProblemBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConceptSchema(BaseModel):
    title: str
    explanation: str
    key_points: List[str]
    example: str

class QuestionSchema(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    pattern: str
    tags: List[str]
    hint: str
    approach: str
    explanation: str
    time_complexity: str
    space_complexity: str
    solution_java: str
    solution_python: str
    solution_javascript: str
    solution_cpp: str

class GroqCodingLessonSchema(BaseModel):
    topic: str
    learning_objective: str
    concepts: List[ConceptSchema] = Field(..., min_length=4, max_length=4)
    questions: List[QuestionSchema] = Field(..., min_length=5, max_length=5)
