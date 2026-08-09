from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class SavedNews(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100))
    url = Column(String(500))
    image_url = Column(String(500))
    category = Column(String(100), index=True)
    language = Column(String(10), default="en")
    published_at = Column(DateTime(timezone=True))
    ai_summary = Column(Text)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="saved_news")
