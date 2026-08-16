from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import User, UserCreate
from app.models.core_models import User as UserModel
from app.api import deps
from app.core.security import get_password_hash
from app.api.v1.endpoints.auth import update_user_streak

router = APIRouter()

@router.post("", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Create new user."""
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user_obj = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.get("", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """Retrieve users."""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Get current user."""
    update_user_streak(db, current_user)
    return current_user

from app.schemas.user import UserStatsUpdate

@router.patch("/me/stats", response_model=User)
def update_user_stats(
    *,
    db: Session = Depends(deps.get_db),
    stats_in: UserStatsUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Update user statistics incrementally."""
    update_user_streak(db, current_user)
    
    if stats_in.words_learned_increment:
        current_user.words_learned = (current_user.words_learned or 0) + stats_in.words_learned_increment
    
    if stats_in.quiz_correct_increment:
        current_user.quiz_correct_answers = (current_user.quiz_correct_answers or 0) + stats_in.quiz_correct_increment
        
    if stats_in.quiz_total_increment:
        current_user.quiz_total_answers = (current_user.quiz_total_answers or 0) + stats_in.quiz_total_increment
        
    if stats_in.modules_completed_increment:
        current_user.modules_completed = (current_user.modules_completed or 0) + stats_in.modules_completed_increment
        
    if stats_in.modules_explored_increment:
        current_user.modules_explored = (current_user.modules_explored or 0) + stats_in.modules_explored_increment
        
    if stats_in.time_spent_increment_seconds:
        current_user.total_time_spent_seconds = (current_user.total_time_spent_seconds or 0) + stats_in.time_spent_increment_seconds

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

from app.schemas.user import UserAvatarUpdate

@router.patch("/me/avatar", response_model=User)
def update_user_avatar(
    *,
    db: Session = Depends(deps.get_db),
    avatar_in: UserAvatarUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Update user avatar."""
    current_user.avatar = avatar_in.avatar
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

from app.schemas.user import UserProfileUpdate

@router.patch("/me/profile", response_model=User)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: UserProfileUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Update user profile information."""
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name
    if profile_in.phone_number is not None:
        current_user.phone_number = profile_in.phone_number
    if profile_in.date_of_birth is not None:
        current_user.date_of_birth = profile_in.date_of_birth
        
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me", response_model=User)
def delete_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Delete current user."""
    db.delete(current_user)
    db.commit()
    return current_user

from app.models.games import GameProgress
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

class ModulesProgressUpdate(BaseModel):
    visited_modules: List[str]

class HabitsProgressUpdate(BaseModel):
    completed_habits: List[str]

@router.get("/me/progress/modules")
def get_today_modules_progress(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "explored_modules",
        GameProgress.completion_date == today_str
    ).first()
    
    return {
        "visited_modules": progress.game_data.get("visited_modules", []) if progress and progress.game_data else []
    }

@router.post("/me/progress/modules")
def update_today_modules_progress(
    request: ModulesProgressUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "explored_modules",
        GameProgress.completion_date == today_str
    ).first()
    
    if progress:
        progress.game_data = {"visited_modules": request.visited_modules}
        db.commit()
        return {"message": "Modules progress updated!"}
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="explored_modules",
        completion_date=today_str,
        score=0,
        game_data={"visited_modules": request.visited_modules}
    )
    db.add(new_progress)
    db.commit()
    
    return {"message": "Modules progress saved!"}

@router.get("/me/progress/habits")
def get_today_habits_progress(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "completed_habits",
        GameProgress.completion_date == today_str
    ).first()
    
    return {
        "completed_habits": progress.game_data.get("completed_habits", []) if progress and progress.game_data else []
    }

@router.post("/me/progress/habits")
def update_today_habits_progress(
    request: HabitsProgressUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    today_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    progress = db.query(GameProgress).filter(
        GameProgress.user_id == current_user.id,
        GameProgress.game_name == "completed_habits",
        GameProgress.completion_date == today_str
    ).first()
    
    if progress:
        progress.game_data = {"completed_habits": request.completed_habits}
        db.commit()
        return {"message": "Habits progress updated!"}
        
    new_progress = GameProgress(
        user_id=current_user.id,
        game_name="completed_habits",
        completion_date=today_str,
        score=0,
        game_data={"completed_habits": request.completed_habits}
    )
    db.add(new_progress)
    db.commit()
    
    return {"message": "Habits progress saved!"}
