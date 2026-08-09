from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.news import NewsArticle, NewsArticleCreate, SavedNewsResponse
from app.models.news import SavedNews as SavedNewsModel
from app.models.core_models import User
from app.api import deps
from app.core.cache import get_cache, set_cache
import logging

logger = logging.getLogger(__name__)

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
    
    articles_data = []
    if cached_data:
        articles_data = cached_data
    else:
        from app.services.news_service import get_or_fetch_daily_news
        # We default to 'for you' if no category provided
        articles_data = get_or_fetch_daily_news(category or "for you", limit=limit)
        # Store in cache for 15 minutes (900 seconds) since news changes fast
        set_cache(cache_key, articles_data, expire=900)
        
    # Check which ones are saved by current user
    if current_user and articles_data:
        article_ids = [a["id"] for a in articles_data]
        saved_urls = db.query(SavedNewsModel.url).filter(
            SavedNewsModel.user_id == current_user.id
        ).all()
        saved_url_set = {u[0] for u in saved_urls}
        
        for article in articles_data:
            article["is_saved"] = article["url"] in saved_url_set

    return articles_data

@router.get("/saved", response_model=List[SavedNewsResponse])
def get_saved_news(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get saved news for current user."""
    saved_news = db.query(SavedNewsModel).filter(
        SavedNewsModel.user_id == current_user.id
    ).order_by(SavedNewsModel.saved_at.desc()).offset(skip).limit(limit).all()
    return saved_news

@router.post("/{article_id}/save", response_model=SavedNewsResponse)
def save_article(
    article_id: str,
    article_in: NewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Save an article for the current user."""
    # Check if already saved
    existing = db.query(SavedNewsModel).filter(
        SavedNewsModel.user_id == current_user.id,
        SavedNewsModel.url == article_in.url
    ).first()
    
    if existing:
        return existing
        
    # Create new saved article
    try:
        saved_article = SavedNewsModel(
            user_id=current_user.id,
            title=article_in.title[:255] if article_in.title else "Untitled",
            summary=article_in.summary or "",
            source=article_in.source[:100] if article_in.source else None,
            url=article_in.url[:500] if article_in.url else None,
            image_url=article_in.image_url[:500] if article_in.image_url else None,
            category=article_in.category[:100] if article_in.category else None,
            language=(article_in.language or "en")[:10],
            published_at=article_in.published_at,
            ai_summary=article_in.ai_summary
        )
        db.add(saved_article)
        db.commit()
        db.refresh(saved_article)
        
        # Attach the article_id to response
        setattr(saved_article, "article_id", article_id)
        return saved_article
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save article: {str(e)}")

@router.delete("/{article_id}/save")
def unsave_article(
    article_id: str,
    url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Remove a saved article."""
    existing = db.query(SavedNewsModel).filter(
        SavedNewsModel.user_id == current_user.id,
        SavedNewsModel.url == url
    ).first()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Saved article not found")
        
    db.delete(existing)
    db.commit()
    return {"success": True}
