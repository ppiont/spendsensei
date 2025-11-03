"""Transaction model for SpendSense"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from spendsense.database import Base

if TYPE_CHECKING:
    from spendsense.models.account import Account


class Transaction(Base):
    """Transaction entity with indexed queries for performance"""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    account_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("accounts.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # In cents, positive = debit
    merchant_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., FOOD_AND_DRINK, INCOME
    pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, account_id={self.account_id}, date={self.date}, amount={self.amount})>"


# Critical indexes for query performance
Index("ix_transactions_account_id", Transaction.account_id)
Index("ix_transactions_date", Transaction.date)
Index("ix_txn_account_date", Transaction.account_id, Transaction.date)  # Composite index
