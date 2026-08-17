from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.api import deps
from app.models.core_models import User, Bookmark

router = APIRouter()

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Get statistics for the admin dashboard."""
    total_users = db.query(User).count()
    
    # Calculate active today
    today_start = datetime.now(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0)
    active_today = db.query(User).filter(
        User.last_login_at >= today_start
    ).count()

    # Total content items (using bookmarks as a proxy)
    total_content = db.query(Bookmark).count()
    
    return {
        "users": total_users,
        "activeToday": active_today,
        "totalContent": total_content
    }

from app.models.vocabulary import VocabularyWord
from app.models.news import SavedNews
from app.models.core_models import Topic, UserTopic, Bookmark, Note, SpiritualSource, DailyOnThisDayEvent, DailySpiritualLesson
from app.models.games import GameProgress
from sqlalchemy import func

@router.get("/content-summary")
def get_content_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    return {
        "vocabulary_words": db.query(VocabularyWord).count(),
        "saved_news": db.query(SavedNews).count(),
        "bookmarks": db.query(Bookmark).count(),
        "notes": db.query(Note).count(),
        "spiritual_sources": db.query(SpiritualSource).count(),
        "spiritual_lessons": db.query(DailySpiritualLesson).count(),
        "on_this_day_events": db.query(DailyOnThisDayEvent).count(),
    }

@router.get("/topics")
def get_admin_topics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    # Get all topics and count how many users subscribe to each
    results = db.query(
        Topic.id,
        Topic.name,
        Topic.description,
        Topic.is_default,
        func.count(UserTopic.id).label("subscribed_users")
    ).outerjoin(UserTopic, Topic.id == UserTopic.topic_id).group_by(Topic.id).all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_default": r.is_default,
            "subscribed_users": r.subscribed_users
        }
        for r in results
    ]

@router.get("/gamification")
def get_admin_gamification(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    users = db.query(User).all()
    
    result = []
    for u in users:
        games_played = db.query(GameProgress).filter(GameProgress.user_id == u.id).count()
        last_played = db.query(func.max(GameProgress.completion_date)).filter(GameProgress.user_id == u.id).scalar()
        
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "games_played": games_played,
            "last_played": last_played,
            "has_played": games_played > 0
        })
    return result

@router.get("/vocabulary")
def get_admin_vocabulary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    return db.query(VocabularyWord).order_by(VocabularyWord.id.desc()).all()

@router.get("/news")
def get_admin_news(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    # Join with User to get who saved it
    results = db.query(SavedNews, User).join(User, SavedNews.user_id == User.id).order_by(SavedNews.id.desc()).all()
    return [
        {
            "id": news.id,
            "title": news.title,
            "category": news.category,
            "source": news.source,
            "saved_at": news.saved_at,
            "user_email": user.email,
            "user_name": user.full_name
        }
        for news, user in results
    ]

@router.get("/games-history")
def get_admin_games_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    results = db.query(GameProgress, User).join(User, GameProgress.user_id == User.id).order_by(GameProgress.id.desc()).all()
    return [
        {
            "id": game.id,
            "game_name": game.game_name,
            "completion_date": game.completion_date,
            "score": game.score,
            "user_email": user.email,
            "user_name": user.full_name,
            "created_at": game.created_at
        }
        for game, user in results
    ]

@router.get("/bookmarks")
def get_admin_bookmarks(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    results = db.query(Bookmark, User).join(User, Bookmark.user_id == User.id).order_by(Bookmark.id.desc()).all()
    return [
        {
            "id": bm.id,
            "title": bm.title,
            "content_type": bm.content_type,
            "folder": bm.folder,
            "created_at": bm.created_at,
            "user_email": user.email,
            "user_name": user.full_name
        }
        for bm, user in results
    ]

@router.get("/notes")
def get_admin_notes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    results = db.query(Note, User).join(User, Note.user_id == User.id).order_by(Note.id.desc()).all()
    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at,
            "user_email": user.email,
            "user_name": user.full_name
        }
        for note, user in results
    ]
