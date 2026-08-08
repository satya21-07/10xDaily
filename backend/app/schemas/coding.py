from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CodingProblemBase(BaseModel):
    title: str
    description: str
    difficulty: Optional[str] = "Medium"
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    hint: Optional[str] = None
    ai_explanation: Optional[str] = None
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
