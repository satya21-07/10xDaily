from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.news import NewsArticle
from app.models.news import NewsArticle as NewsArticleModel
from app.models.core_models import User
from app.api import deps
from app.core.cache import get_cache, set_cache

router = APIRouter()

@router.get("", response_model=List[NewsArticle])
def get_news(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve news articles with optional category filtering (cached)."""
    cache_key = f"news:{category or 'all'}:{limit}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    from app.services.news_service import get_or_fetch_daily_news
    
    # We default to 'world' if no category provided, or use what's passed ('india' or 'world')
    articles_data = get_or_fetch_daily_news(category or "world", limit=limit)
    
    # Store in cache for 15 minutes (900 seconds) since news changes fast
    set_cache(cache_key, articles_data, expire=900)
    
    return articles_data
