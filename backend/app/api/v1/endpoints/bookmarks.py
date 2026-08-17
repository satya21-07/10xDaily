from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse
from app.models.core_models import Bookmark as BookmarkModel, User
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[BookmarkResponse])
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get all bookmarks for a user."""
    bookmarks = db.query(BookmarkModel).filter(
        BookmarkModel.user_id == current_user.id
    ).order_by(BookmarkModel.id.desc()).all()
    return bookmarks

@router.post("", response_model=BookmarkResponse)
def create_bookmark(
    *,
    db: Session = Depends(get_db),
    bookmark_in: BookmarkCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new bookmark."""
    # Check if already bookmarked to avoid duplicates
    existing = db.query(BookmarkModel).filter(
        BookmarkModel.user_id == current_user.id,
        BookmarkModel.title == bookmark_in.title,
        BookmarkModel.content_type == bookmark_in.content_type
    ).first()
    
    if existing:
        if bookmark_in.details is not None:
            existing.details = bookmark_in.details
        if bookmark_in.url is not None:
            existing.url = bookmark_in.url
        if bookmark_in.folder is not None:
            existing.folder = bookmark_in.folder
        if bookmark_in.reference_id is not None:
            existing.reference_id = bookmark_in.reference_id
        db.commit()
        db.refresh(existing)
        return existing
        
    bookmark_obj = BookmarkModel(
        user_id=current_user.id,
        **bookmark_in.dict()
    )
    db.add(bookmark_obj)
    db.commit()
    db.refresh(bookmark_obj)
    return bookmark_obj

@router.delete("/{bookmark_id}", response_model=BookmarkResponse)
def delete_bookmark(
    *,
    db: Session = Depends(get_db),
    bookmark_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a bookmark."""
    bookmark = db.query(BookmarkModel).filter(
        BookmarkModel.id == bookmark_id,
        BookmarkModel.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    db.delete(bookmark)
    db.commit()
    return bookmark
