from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone

class BookmarkBase(BaseModel):
    title: str
    url: Optional[str] = None
    content_type: str
    reference_id: Optional[str] = None
    folder: Optional[str] = "General"
    details: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

