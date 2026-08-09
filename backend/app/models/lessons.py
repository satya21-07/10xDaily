from sqlalchemy import Column, Integer, String, Text, DateTime, Date, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base

class FinanceLesson(Base):
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False) # e.g., Budgeting, Emergency Fund
    problem = Column(Text)
    solution = Column(Text)
    example = Column(Text)
    calculator_type = Column(String(50)) # e.g., SIP, CompoundInterest, Budget
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HealthLesson(Base):
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100)) # e.g., Sleep, Nutrition
    title = Column(String(255))
    advice = Column(Text)
    scientific_evidence = Column(Text)
    action_step = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SpiritualLesson(Base):
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(String(100)) # e.g., Bhagavad Gita
    story = Column(Text)
    meaning = Column(Text)
    context = Column(Text)
    modern_example = Column(Text)
    reflection = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyHealthLesson(Base):
    __tablename__ = "daily_health_lesson"
    id = Column(Integer, primary_key=True, index=True)
    lesson_date = Column(Date, unique=True, index=True, nullable=False)
    topic = Column(String(255), nullable=False)
    learning_objective = Column(Text)
    health_facts = Column(JSON) # Array of facts
    daily_activity = Column(JSON) # Dict with activity details
    nutrition_tip = Column(JSON) # Dict with nutrition tip
    daily_habit = Column(JSON) # Dict with daily habit
    source_name = Column(String(255))
    source_url = Column(String(512))
    source_type = Column(String(100))
    source_retrieved_at = Column(String(100))
    disclaimer = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def source(self):
        return {
            "name": self.source_name,
            "url": self.source_url,
            "type": self.source_type,
            "retrieved_at": self.source_retrieved_at
        }


class DailyFinanceLesson(Base):
    __tablename__ = "daily_finance_lesson"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_date = Column(Date, nullable=False, index=True)
    country = Column(String(10), nullable=False, index=True)
    currency = Column(String(10), nullable=False)
    topic = Column(String(255), nullable=False)
    content = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('lesson_date', 'country', name='uix_daily_finance_date_country'),
    )
