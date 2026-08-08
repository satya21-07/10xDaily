from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.finance_service import generate_daily_finance_lesson
from app.core.cache import get_cache, set_cache
from app.models.core_models import User
from app.api import deps
from app.db.session import get_db
from datetime import datetime, timezone

router = APIRouter()

@router.get("/daily")
def get_daily_finance(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated finance lesson."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    cache_key = f"finance_lesson:{day_of_year}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    lesson_data = generate_daily_finance_lesson()
    set_cache(cache_key, lesson_data, expire=86400)
    
    return lesson_data
