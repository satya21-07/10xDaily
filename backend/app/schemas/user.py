from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    xp: Optional[int] = 0
    current_streak: Optional[int] = 0
    words_learned: Optional[int] = 0
    quiz_correct_answers: Optional[int] = 0
    quiz_total_answers: Optional[int] = 0
    modules_completed: Optional[int] = 0
    modules_explored: Optional[int] = 0
    total_time_spent_seconds: Optional[int] = 0
    avatar: Optional[str] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None

class UserAvatarUpdate(BaseModel):
    avatar: str

class UserStatsUpdate(BaseModel):
    words_learned_increment: Optional[int] = 0
    quiz_correct_increment: Optional[int] = 0
    quiz_total_increment: Optional[int] = 0
    modules_completed_increment: Optional[int] = 0
    modules_explored_increment: Optional[int] = 0
    time_spent_increment_seconds: Optional[int] = 0

import re
from pydantic import field_validator

class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*?&#]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

