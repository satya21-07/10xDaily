from sqlalchemy import Column, Integer, String, Text, DateTime
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
