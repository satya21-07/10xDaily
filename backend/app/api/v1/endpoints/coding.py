from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.coding import CodingProblem
from app.models.coding import CodingProblem as CodingProblemModel
from app.models.core_models import User
from app.api import deps

router = APIRouter()

@router.get("/daily")
def get_daily_coding_problem(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated coding lesson."""
    from app.services.coding_service import generate_daily_coding_lesson
    from app.core.cache import get_cache, set_cache
    from datetime import datetime, timezone
    
    # We cache it per day so we don't spam the Gemini API on every page load
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    cache_key = f"coding_lesson:{day_of_year}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    lesson_data = generate_daily_coding_lesson()
    
    # Store for 24 hours (86400 seconds)
    set_cache(cache_key, lesson_data, expire=86400)
    
    return lesson_data
