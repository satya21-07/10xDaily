from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.vocabulary import VocabularyWord, VocabularyWordCreate
from app.models.vocabulary import VocabularyWord as VocabularyWordModel
from app.models.core_models import User
from app.api import deps

router = APIRouter()

@router.get("/daily", response_model=List[VocabularyWord])
def get_daily_vocabulary(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get 10 daily vocabulary words."""
    from app.services.vocabulary_service import get_or_generate_daily_words
    words = get_or_generate_daily_words(db, limit=limit)
    return words

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
    word_obj = VocabularyWordModel(**word_in.dict())
    db.add(word_obj)
    db.commit()
    db.refresh(word_obj)
    return word_obj
