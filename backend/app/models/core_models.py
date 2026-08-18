from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    date_of_birth = Column(String(50), nullable=True)
    avatar = Column(Text, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Dynamic Stats
    words_learned = Column(Integer, default=0)
    quiz_correct_answers = Column(Integer, default=0)
    quiz_total_answers = Column(Integer, default=0)
    modules_completed = Column(Integer, default=0)
    modules_explored = Column(Integer, default=0)
    total_time_spent_seconds = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    topics = relationship("UserTopic", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    notes = relationship("Note", back_populates="user")

class Topic(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("UserTopic", back_populates="topic")

class UserTopic(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topic.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="topics")
    topic = relationship("Topic", back_populates="users")

class Bookmark(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(Text)
    content_type = Column(String(50)) # e.g. 'news', 'vocabulary', 'coding'
    reference_id = Column(String(100)) # ID of the actual content
    folder = Column(String(100), default="General")
    details = Column(String) # For storing full JSON representation of the item
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmarks")

class Note(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    content = Column(String)
    reference_id = Column(String(100)) # Optional link to content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="notes")

class UserProgress(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    module_name = Column(String(100), nullable=False) # e.g., 'vocabulary', 'coding'
    items_completed = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="progress")

class SpiritualSource(Base):
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False) # e.g., 'Bhagavad Gita'
    section = Column(String(100)) # e.g., 'Sundara Kanda'
    chapter = Column(Integer)
    verse = Column(Integer)
    character = Column(String(100)) # e.g., 'Hanuman'
    topic = Column(String(100), nullable=False) # e.g., 'Karma'
    original_text = Column(Text)
    translation = Column(Text, nullable=False)
    source_reference = Column(String(255), nullable=False) # e.g., 'Bhagavad Gita 2.47'
    source_url = Column(String(255))
    translation_name = Column(String(255))
    language = Column(String(50), default="English")
    license_or_rights_note = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lessons = relationship("DailySpiritualLesson", back_populates="source_passage")

class DailySpiritualLesson(Base):
    id = Column(Integer, primary_key=True, index=True)
    lesson_date = Column(String(10), unique=True, index=True, nullable=False) # YYYY-MM-DD
    topic = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey("spiritual_source.id", ondelete="CASCADE"), nullable=False)
    
    # Store the generated content as JSON string or Text
    reflection = Column(Text, nullable=False)
    today_practice = Column(Text, nullable=False)
    journal_prompt = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_passage = relationship("SpiritualSource", back_populates="lessons")

class DailyOnThisDayEvent(Base):
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True, nullable=False) # YYYY-MM-DD
    month = Column(Integer)
    day = Column(Integer)
    year = Column(String(50))
    title = Column(String(255))
    description = Column(Text)
    category = Column(String(100))
    country = Column(String(100))
    source_name = Column(String(100))
    source_url = Column(String(255))
    image_url = Column(String(500))
    why_it_matters = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
