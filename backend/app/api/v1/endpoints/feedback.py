from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.core_models import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStatusUpdate
from app.services.email_service import EmailService

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_in: FeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Submit user feedback or issue report.
    Automatically enqueues an email notification to the team.
    """
    user_id = current_user.id if current_user else None
    user_email = feedback_in.user_email or (current_user.email if current_user else None)
    user_name = feedback_in.user_name or (current_user.full_name if current_user else None)

    if not user_email:
        raise HTTPException(
            status_code=400,
            detail="A contact email address is required to submit feedback."
        )

    feedback = Feedback(
        user_id=user_id,
        user_email=str(user_email),
        user_name=user_name,
        feedback_type=feedback_in.feedback_type or "general",
        category=feedback_in.category or "General",
        subject=feedback_in.subject,
        message=feedback_in.message,
        rating=feedback_in.rating,
        device_info=feedback_in.device_info,
        status="pending"
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Queue email sending in background task
    background_tasks.add_task(EmailService.send_feedback_email, feedback)

    return feedback

@router.get("/my-feedback", response_model=List[FeedbackResponse])
def get_my_feedback(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20
) -> Any:
    """
    Retrieve feedback submissions created by the current user.
    """
    feedbacks = db.query(Feedback).filter(
        (Feedback.user_id == current_user.id) | (Feedback.user_email == current_user.email)
    ).order_by(Feedback.created_at.desc(), Feedback.id.desc()).offset(skip).limit(limit).all()
    
    return feedbacks

@router.get("/", response_model=List[FeedbackResponse])
def get_all_feedback(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    status: Optional[str] = Query(None, description="Filter by status: pending, in_review, resolved"),
    feedback_type: Optional[str] = Query(None, description="Filter by type"),
    skip: int = 0,
    limit: int = 50
) -> Any:
    """
    Admin only: Retrieve all user feedback submissions with optional filters.
    """
    query = db.query(Feedback)
    if status:
        query = query.filter(Feedback.status == status)
    if feedback_type:
        query = query.filter(Feedback.feedback_type == feedback_type)

    feedbacks = query.order_by(Feedback.created_at.desc(), Feedback.id.desc()).offset(skip).limit(limit).all()
    return feedbacks


@router.patch("/{feedback_id}/status", response_model=FeedbackResponse)
def update_feedback_status(
    feedback_id: int,
    status_update: FeedbackStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Admin only: Update the review/resolution status of a feedback item.
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback.status = status_update.status
    db.commit()
    db.refresh(feedback)
    return feedback
