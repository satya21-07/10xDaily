from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class VocabularyWord(Base):
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, index=True, nullable=False)
    # Using JSON to store lists of structured objects
    definitions = Column(JSON, default=list) # List of {"part_of_speech": "", "definition": "", "example": ""}
    part_of_speech = Column(JSON, default=list) # List of strings
    
    pronunciation = Column(String(100))
    audio_url = Column(String(255))
    
    synonyms = Column(JSON, default=list) # List of strings
    antonyms = Column(JSON, default=list) # List of strings
    origin = Column(Text)
    
    difficulty = Column(String(50), default="Medium") # Easy, Medium, Hard
    usage_tips = Column(Text)
    source = Column(String(100), default="free_dictionary")
    
    # Keeping old columns for backward compatibility if needed, but nullable
    meaning = Column(Text, nullable=True)
    example = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DailyVocabulary(Base):
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("vocabulary_word.id"), nullable=False)
    position = Column(Integer, nullable=False) # 1 to 10
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    word = relationship("VocabularyWord")
    
    __table_args__ = (
        UniqueConstraint('date', 'word_id', name='uix_daily_word'),
        UniqueConstraint('date', 'position', name='uix_daily_position'),
    )
