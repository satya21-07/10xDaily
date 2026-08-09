from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class HealthFact(BaseModel):
    title: str
    explanation: str
    key_points: List[str]

class DailyExercise(BaseModel):
    name: str
    duration: str
    instructions: str
    safety_note: Optional[str] = None

class DailyActivity(BaseModel):
    name: str
    duration: str
    level: str
    exercises: List[DailyExercise]

class FeaturedFood(BaseModel):
    name: str
    calories: str
    protein: str
    carbs: str
    fat: str
    fiber: str

class NutritionTip(BaseModel):
    title: str
    description: str
    featured_foods: Optional[List[FeaturedFood]] = None

class DailyHabit(BaseModel):
    title: str
    description: str

class HealthSource(BaseModel):
    name: str
    url: str
    type: str
    retrieved_at: str

class DailyHealthLessonBase(BaseModel):
    topic: str
    learning_objective: str
    health_facts: List[HealthFact]
    daily_activity: DailyActivity
    nutrition_tip: NutritionTip
    daily_habit: DailyHabit
    source: HealthSource
    disclaimer: str

class DailyHealthLessonCreate(DailyHealthLessonBase):
    pass

class DailyHealthLesson(DailyHealthLessonBase):
    id: int
    lesson_date: date

    class Config:
        from_attributes = True
