import zoneinfo
from datetime import timedelta, datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.schemas.token import Token
from app.models.core_models import User

router = APIRouter()

def update_user_streak(db: Session, user: User) -> int:
    now = datetime.now(timezone.utc)
    ist_tz = zoneinfo.ZoneInfo("Asia/Kolkata")
    now_ist = now.astimezone(ist_tz)
    
    if not user.last_login_at:
        user.current_streak = 1
    else:
        if user.last_login_at.tzinfo is None:
            last_login_utc = user.last_login_at.replace(tzinfo=timezone.utc)
        else:
            last_login_utc = user.last_login_at
            
        last_login_ist = last_login_utc.astimezone(ist_tz)
        
        now_date = now_ist.date()
        last_date = last_login_ist.date()
        delta = (now_date - last_date).days
        
        if delta == 1:
            user.current_streak += 1
        elif delta > 1:
            user.current_streak = 1
    
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
        
    user.last_login_at = now
    db.commit()
    db.refresh(user)
    return user.current_streak

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    current_streak = update_user_streak(db, user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "streak": current_streak,
            "xp": user.xp,
            "words_learned": user.words_learned,
            "quiz_correct_answers": user.quiz_correct_answers,
            "quiz_total_answers": user.quiz_total_answers,
            "modules_completed": user.modules_completed,
            "total_time_spent_seconds": user.total_time_spent_seconds
        }
    }

from app.schemas.user import UserCreate, User as UserSchema
from pydantic import BaseModel

class GoogleToken(BaseModel):
    token: str

@router.post("/register", response_model=Token)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Create new user without the need to be logged in."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    current_streak = update_user_streak(db, user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "streak": current_streak,
            "xp": user.xp,
            "words_learned": user.words_learned,
            "quiz_correct_answers": user.quiz_correct_answers,
            "quiz_total_answers": user.quiz_total_answers,
            "modules_completed": user.modules_completed,
            "total_time_spent_seconds": user.total_time_spent_seconds
        }
    }

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@router.post("/google", response_model=Token)
def google_auth(
    *,
    db: Session = Depends(get_db),
    token_in: GoogleToken,
) -> Any:
    """Authenticate with Google ID token."""
    try:
        # Note: in a production app, verify the client ID. We accept any for now or check against settings.
        idinfo = id_token.verify_oauth2_token(
            token_in.token, 
            google_requests.Request(),
            audience=settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        email = idinfo['email']
        name = idinfo.get('name', '')
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create user
            user = User(
                email=email,
                hashed_password=security.get_password_hash("google_sso_random_pw_placeholder"),
                full_name=name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        current_streak = update_user_streak(db, user)
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "streak": current_streak,
                "xp": user.xp,
                "words_learned": user.words_learned,
                "quiz_correct_answers": user.quiz_correct_answers,
                "quiz_total_answers": user.quiz_total_answers,
                "modules_completed": user.modules_completed,
                "total_time_spent_seconds": user.total_time_spent_seconds
            }
        }
    except ValueError as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid token")
