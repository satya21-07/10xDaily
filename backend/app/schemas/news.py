from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class NewsArticleBase(BaseModel):
    title: str
    summary: str
    source: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    published_at: Optional[datetime] = None
    ai_summary: Optional[str] = None

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
