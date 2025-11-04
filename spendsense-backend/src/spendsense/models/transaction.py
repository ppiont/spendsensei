"""Transaction model for SpendSense"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from spendsense.database import Base

if TYPE_CHECKING:
    from spendsense.models.account import Account


class Transaction(Base):
    """Transaction entity with indexed queries for performance - Plaid-compliant schema"""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    account_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("accounts.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # In cents, positive = debit

    # Plaid merchant fields
    merchant_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    merchant_entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Normalized merchant ID

    # Plaid category fields (two-level hierarchy)
    personal_finance_category_primary: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., FOOD_AND_DRINK, INCOME
    personal_finance_category_detailed: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # e.g., RESTAURANTS, FAST_FOOD

    # Plaid payment channel
    payment_channel: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 'online', 'in_store', 'other'

    # Plaid pending status
    pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, account_id={self.account_id}, date={self.date}, amount={self.amount})>"


# Critical indexes for query performance
Index("ix_transactions_account_id", Transaction.account_id)
Index("ix_transactions_date", Transaction.date)
Index("ix_txn_account_date", Transaction.account_id, Transaction.date)  # Composite index
