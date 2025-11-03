"""Account model for SpendSense"""

from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from spendsense.database import Base

if TYPE_CHECKING:
    from spendsense.models.user import User
    from spendsense.models.transaction import Transaction


class Account(Base):
    """Account entity (checking, savings, credit cards)"""

    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'depository', 'credit'
    subtype: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'checking', 'savings', 'credit_card'
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    mask: Mapped[str] = mapped_column(String(4), nullable=False)  # Last 4 digits
    balance: Mapped[int] = mapped_column(Integer, nullable=False)  # In cents
    limit: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Credit cards only
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    apr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Credit cards only
    min_payment: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, user_id={self.user_id}, type={self.type}, subtype={self.subtype})>"


# Create index on user_id for faster queries
Index("ix_accounts_user_id", Account.user_id)
