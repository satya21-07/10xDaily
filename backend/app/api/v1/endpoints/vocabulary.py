from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
import json
from app.schemas.vocabulary import VocabularyWord, VocabularyWordCreate, DailyVocabularyResponse
from app.models.vocabulary import VocabularyWord as VocabularyWordModel
from app.models.core_models import User
from app.api import deps

router = APIRouter()

@router.get("/daily", response_model=DailyVocabularyResponse)
def get_daily_vocabulary(
    db: Session = Depends(get_db),
    limit: int = 10
) -> Any:
    """Get 10 daily vocabulary words."""
    from app.services.vocabulary_service import get_or_generate_daily_words, get_today_date_in_india
    from app.core.cache import get_cache, set_cache
    
    today_str = str(get_today_date_in_india())
    cache_key = f"vocabulary:today:{today_str}"
    
    # 1. Check Cache
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
            
    words = get_or_generate_daily_words(db, limit=limit)
    
    # Format the response
    response_data = {
        "date": today_str,
        "total": len(words),
        "words": [VocabularyWord.model_validate(w).model_dump(mode="json") for w in words]
    }
    
    # Cache to Redis
    if len(words) == limit:
        set_cache(cache_key, response_data, expire=86400) # Cache for 24h
            
    return response_data

@router.post("", response_model=VocabularyWord)
def create_vocabulary_word(
    *,
    db: Session = Depends(get_db),
    word_in: VocabularyWordCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Create a new vocabulary word."""
    word = db.query(VocabularyWordModel).filter(VocabularyWordModel.word == word_in.word).first()
    if word:
        raise HTTPException(
            status_code=400,
            detail="The word already exists.",
        )
    word_data = word_in.model_dump(exclude={'bookmarked', 'learned'})
    word_obj = VocabularyWordModel(**word_data)
    db.add(word_obj)
    db.commit()
    db.refresh(word_obj)
    return word_obj
