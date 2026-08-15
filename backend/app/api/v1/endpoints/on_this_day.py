from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Any
import logging
from app.services.on_this_day_service import get_on_this_day_event
from app.api import deps

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/today")
def read_on_this_day_today(db: Session = Depends(deps.get_db)) -> Any:
    """
    Get the historical event for today.
    """
    try:
        event = get_on_this_day_event(db)
        return event
    except Exception as e:
        logger.error(f"Error getting on this day event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
