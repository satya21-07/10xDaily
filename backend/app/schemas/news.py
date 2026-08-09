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
    language: Optional[str] = "en"
    published_at: Optional[datetime] = None
    ai_summary: Optional[str] = None

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: str  # URL hash string
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True

class SavedNewsResponse(NewsArticleBase):
    id: int # database ID
    article_id: Optional[str] = None
    saved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
