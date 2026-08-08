from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class CodingProblem(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50)) # Easy, Medium, Hard
    time_complexity = Column(String(100))
    space_complexity = Column(String(100))
    hint = Column(Text)
    ai_explanation = Column(Text)
    
    # Code templates/solutions
    java_solution = Column(Text)
    python_solution = Column(Text)
    cpp_solution = Column(Text)
    javascript_solution = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
