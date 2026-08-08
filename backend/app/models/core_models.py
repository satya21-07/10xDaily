from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
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
    url = Column(String(255))
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
