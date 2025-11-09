"""Persona model for SpendSense"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from spendsense.database import Base

if TYPE_CHECKING:
    from spendsense.models.user import User


class PersonaType(str, Enum):
    """Financial persona types based on behavioral signals"""

    HIGH_UTILIZATION = "high_utilization"  # Credit card usage ≥50%
    VARIABLE_INCOME = "variable_income"  # Irregular payroll patterns
    SUBSCRIPTION_HEAVY = "subscription_heavy"  # Multiple recurring merchants
    SAVINGS_BUILDER = "savings_builder"  # Growing savings accounts
    DEBT_CONSOLIDATOR = "debt_consolidator"  # Multiple cards with moderate utilization (5th custom persona)
    BALANCED = "balanced"  # Default, no specific patterns


class Persona(Base):
    """Persona assignment record with confidence scoring"""

    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
    )
    window: Mapped[str] = mapped_column(String(10), nullable=False)  # '30d' or '180d'
    persona_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PersonaType enum values
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="personas")

    def __repr__(self) -> str:
        return f"<Persona(id={self.id}, user_id={self.user_id}, persona_type={self.persona_type}, confidence={self.confidence})>"


# Create index on user_id for faster queries
Index("ix_personas_user_id", Persona.user_id)
