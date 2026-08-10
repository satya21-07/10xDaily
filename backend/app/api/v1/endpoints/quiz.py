from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.quiz_service import generate_daily_quiz
from app.models.core_models import User
from app.api import deps
from app.db.session import get_db

router = APIRouter()

@router.get("/daily")
async def get_daily_quiz(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated mixed quiz."""
    quiz_data = await generate_daily_quiz()
    return quiz_data
