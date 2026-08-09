from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.spiritual_service import get_or_generate_daily_spiritual_lesson
from app.schemas.spiritual import DailySpiritualLessonResponse

router = APIRouter()

@router.get("/daily", response_model=DailySpiritualLessonResponse)
def get_daily_spiritual(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated spiritual lesson from the database."""
    lesson_data = get_or_generate_daily_spiritual_lesson(db)
    return lesson_data
