from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class NewsArticle(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100))
    url = Column(String(500))
    image_url = Column(String(500))
    category = Column(String(100), index=True) # e.g., AI, Tech, World
    published_at = Column(DateTime(timezone=True))
    ai_summary = Column(Text) # Custom generated summary
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
