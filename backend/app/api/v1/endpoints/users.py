from typing import Any, List, Optional
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

from pydantic import BaseModel

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

from app.core import security

@router.post("/me/password", response_model=User)
def update_user_password(
    *,
    db: Session = Depends(deps.get_db),
    password_in: UserPasswordUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Update user password."""
    if not security.verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = security.get_password_hash(password_in.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

import pyotp
import qrcode
import base64
from io import BytesIO

class TwoFactorVerify(BaseModel):
    code: str
    secret: Optional[str] = None

@router.post("/me/2fa/setup")
def setup_2fa(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Generate 2FA secret and QR code."""
    secret = pyotp.random_base32()
    # Provide an otpauth URI
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="10xDaily")
    
    # Generate QR Code image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_b64}"
    }

@router.post("/me/2fa/verify")
def verify_2fa(
    request: TwoFactorVerify,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Verify 2FA code and enable if successful."""
    # If enabling for the first time, secret is passed in request. 
    secret_to_use = request.secret if request.secret else current_user.two_factor_secret
    
    if not secret_to_use:
        raise HTTPException(status_code=400, detail="No secret provided or found.")
        
    totp = pyotp.TOTP(secret_to_use)
    if not totp.verify(request.code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code.")
        
    # If successful and secret was passed, enable it
    if request.secret:
        current_user.two_factor_secret = request.secret
        current_user.is_two_factor_enabled = True
        db.add(current_user)
        db.commit()
        
    return {"message": "2FA verified successfully."}

@router.post("/me/2fa/disable")
def disable_2fa(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """Disable 2FA."""
    current_user.is_two_factor_enabled = False
    current_user.two_factor_secret = None
    db.add(current_user)
    db.commit()
    return {"message": "2FA disabled successfully."}

from app.models.games import GameProgress
from datetime import datetime, timezone, timedelta

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

