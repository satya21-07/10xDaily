from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.spiritual_service import generate_daily_spiritual_lesson
from app.core.cache import get_cache, set_cache
from datetime import datetime, timezone

router = APIRouter()

@router.get("/daily")
def get_daily_spiritual(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated spiritual lesson."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    cache_key = f"spiritual_lesson:{day_of_year}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    lesson_data = generate_daily_spiritual_lesson()
    set_cache(cache_key, lesson_data, expire=86400)
    
    return lesson_data
