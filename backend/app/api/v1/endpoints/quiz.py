from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.quiz_service import generate_daily_quiz
from app.core.cache import get_cache, set_cache
from app.models.core_models import User
from app.api import deps
from app.db.session import get_db
from datetime import datetime, timezone

router = APIRouter()

@router.get("/daily")
def get_daily_quiz(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated mixed quiz."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    cache_key = f"quiz_lesson:{day_of_year}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    quiz_data = generate_daily_quiz()
    set_cache(cache_key, quiz_data, expire=86400)
    
    return quiz_data
