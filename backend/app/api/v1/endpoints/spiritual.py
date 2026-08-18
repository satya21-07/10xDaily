from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.spiritual_service import get_daily_spiritual_lesson
from app.schemas.spiritual import DailySpiritualLessonResponse

router = APIRouter()

@router.get("/daily", response_model=DailySpiritualLessonResponse)
def get_daily_spiritual(
    scripture: str = Query("gita", description="Scripture type: 'gita' or 'character'"),
    day: Optional[int] = Query(None, description="Sequential day or verse index"),
    chapter: Optional[int] = Query(None, description="Chapter number (for Gita)"),
    verse: Optional[int] = Query(None, description="Verse number (for Gita)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve authentic sequential lessons from Bhagavad Gita,
    or a Mythological Character of the Day.
    """
    lesson_data = get_daily_spiritual_lesson(
        scripture=scripture,
        day=day,
        chapter=chapter,
        verse=verse
    )
    return lesson_data

