from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.api import deps
from app.models.core_models import User, Bookmark

router = APIRouter()

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Get statistics for the admin dashboard."""
    total_users = db.query(User).count()
    
    # Calculate active today
    today_start = datetime.now(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0)
    active_today = db.query(User).filter(
        User.last_login_at >= today_start
    ).count()

    # Total content items (using bookmarks as a proxy)
    total_content = db.query(Bookmark).count()
    
    return {
        "users": total_users,
        "activeToday": active_today,
        "totalContent": total_content
    }

