"""Feedback database model"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from spendsense.database import Base


class FeedbackType(str, enum.Enum):
    """Types of feedback users can provide"""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    INACCURATE = "inaccurate"
    IRRELEVANT = "irrelevant"
    OTHER = "other"


class Feedback(Base):
    """User feedback on recommendations and offers"""
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    recommendation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    recommendation_type: Mapped[str] = mapped_column(String, nullable=False)  # "education" or "offer"
    feedback_type: Mapped[str] = mapped_column(SQLEnum(FeedbackType), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user_id={self.user_id}, feedback_type={self.feedback_type})>"
