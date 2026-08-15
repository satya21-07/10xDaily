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
    from app.services.coding_service import get_or_generate_daily_coding_lesson
    
    lesson_data = get_or_generate_daily_coding_lesson(db)
    return lesson_data
