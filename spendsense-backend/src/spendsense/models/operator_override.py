"""Operator override database model"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from spendsense.database import Base


class OverrideAction(str, enum.Enum):
    """Actions operators can take on recommendations"""
    APPROVE = "approve"
    FLAG = "flag"


class OperatorOverride(Base):
    """Operator overrides for recommendation quality control"""
    __tablename__ = "operator_overrides"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    recommendation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    recommendation_type: Mapped[str] = mapped_column(String, nullable=False)  # "education" or "offer"
    action: Mapped[str] = mapped_column(SQLEnum(OverrideAction), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    operator_id: Mapped[str] = mapped_column(String, nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<OperatorOverride(id={self.id}, action={self.action}, rec_id={self.recommendation_id})>"
