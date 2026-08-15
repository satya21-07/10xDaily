from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class GameProgress(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    game_name = Column(String(50), nullable=False)  # e.g., 'flow'
    completion_date = Column(String(10), nullable=False, index=True) # YYYY-MM-DD
    score = Column(Integer, default=0)
    game_data = Column(JSON, nullable=True) # To store completion state (e.g. paths)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
