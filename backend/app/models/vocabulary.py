from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class VocabularyWord(Base):
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, index=True, nullable=False)
    meaning = Column(Text, nullable=False)
    pronunciation = Column(String(100))
    audio_url = Column(String(255))
    synonyms = Column(Text) # Stored as comma-separated or JSON string
    antonyms = Column(Text)
    origin = Column(Text)
    example = Column(Text)
    difficulty = Column(String(50), default="Medium") # Easy, Medium, Hard
    usage_tips = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
