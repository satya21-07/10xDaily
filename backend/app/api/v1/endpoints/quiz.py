from typing import Any, Optional, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.quiz_service import generate_daily_quiz
from app.models.core_models import User
from app.models.games import GameProgress
from app.api import deps
from app.db.session import get_db
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

router = APIRouter()

@router.get("/daily")
async def get_daily_quiz(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Retrieve the daily AI generated mixed quiz."""
    quiz_data = await generate_daily_quiz(db)
    return quiz_data

class QuizStateUpdate(BaseModel):
    user_answers: List[Optional[int]]
    score: int
    is_finished: bool
    stats_synced: bool

@router.get("/progress/today")
def get_today_quiz_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "quiz",
        GameProgress.completion_date == today_str
    ).first()
    
    return {
        "completed": progress is not None and progress.game_data and progress.game_data.get("is_finished", False),
        "saved_state": progress.game_data if progress else None
    }

@router.post("/progress/complete")
def complete_quiz(
    request: QuizStateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "quiz",
        GameProgress.completion_date == today_str
    ).first()
    
    game_data = {
        "user_answers": request.user_answers,
        "score": request.score,
        "is_finished": request.is_finished,
        "stats_synced": request.stats_synced
    }
    
    if progress:
        progress.game_data = game_data
        db.commit()
        return {"message": "Quiz progress updated!"}
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="quiz",
        completion_date=today_str,
        score=request.score,
        game_data=game_data
    )
    db.add(new_progress)
    db.commit()
    
    return {"message": "Quiz progress saved!"}
