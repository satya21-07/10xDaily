from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Feedback(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255), nullable=True)
    feedback_type = Column(String(50), nullable=False, default="general")  # bug_report, feature_request, content_issue, general
    category = Column(String(100), nullable=True, default="General")      # module / area
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)                               # 1 to 5 stars
    device_info = Column(Text, nullable=True)                            # platform, browser, os, etc.
    status = Column(String(50), nullable=False, default="pending")        # pending, in_review, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Optional relationship to User
    user = relationship("User", backref="feedbacks", foreign_keys=[user_id])
