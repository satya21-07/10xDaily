from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class FeedbackCreate(BaseModel):
    subject: str = Field(..., min_length=2, max_length=255, description="Brief summary of the feedback")
    message: str = Field(..., min_length=5, description="Detailed feedback or issue description")
    feedback_type: str = Field(default="general", description="bug_report, feature_request, content_issue, general")
    category: Optional[str] = Field(default="General", description="Module/Area e.g. Vocabulary, Games, Quiz, News")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating from 1 to 5")
    user_name: Optional[str] = Field(default=None, max_length=255)
    user_email: Optional[EmailStr] = Field(default=None, description="Contact email if not logged in or overriding")
    device_info: Optional[str] = Field(default=None, description="App version, OS, browser info")

class FeedbackStatusUpdate(BaseModel):
    status: str = Field(..., description="pending, in_review, resolved")

class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: str
    user_name: Optional[str] = None
    feedback_type: str
    category: Optional[str] = None
    subject: str
    message: str
    rating: Optional[int] = None
    device_info: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

