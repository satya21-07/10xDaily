from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.health_service import get_or_generate_daily_health_lesson
from app.schemas.health import DailyHealthLesson

router = APIRouter()

@router.get("/daily", response_model=DailyHealthLesson)
def get_daily_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated health lesson."""
    return get_or_generate_daily_health_lesson(db)
