from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.quote_service import get_daily_quote
from app.core.cache import get_cache, set_cache
from datetime import datetime, timezone

router = APIRouter()

@router.get("/daily-quote")
def get_random_quote(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve an AI generated unique quote, cached daily."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    cache_key = f"quote_of_the_day:{day_of_year}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    quote_data = get_daily_quote()
    set_cache(cache_key, quote_data, expire=86400)
    
    return quote_data
