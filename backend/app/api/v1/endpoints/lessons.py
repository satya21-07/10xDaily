from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lessons import FinanceLesson, HealthLesson, SpiritualLesson
from app.models.lessons import FinanceLesson as FinanceLessonModel, HealthLesson as HealthLessonModel, SpiritualLesson as SpiritualLessonModel
from app.models.core_models import User
from app.api import deps

router = APIRouter()

@router.get("/finance/daily", response_model=FinanceLesson)
def get_daily_finance(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lesson = db.query(FinanceLessonModel).first()
    if not lesson: raise HTTPException(status_code=404, detail="No lesson found")
    return lesson

@router.get("/health/daily", response_model=HealthLesson)
def get_daily_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lesson = db.query(HealthLessonModel).first()
    if not lesson: raise HTTPException(status_code=404, detail="No lesson found")
    return lesson

@router.get("/spiritual/daily", response_model=SpiritualLesson)
def get_daily_spiritual(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lesson = db.query(SpiritualLessonModel).first()
    if not lesson: raise HTTPException(status_code=404, detail="No lesson found")
    return lesson
