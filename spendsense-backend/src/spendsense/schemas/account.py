"""Account schemas for API responses"""

from typing import Optional
from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """Response schema for account data - Plaid-compliant"""
    id: str = Field(..., description="Unique account identifier")
    user_id: str = Field(..., description="User who owns this account")
    type: str = Field(..., description="Account type: 'depository' or 'credit'")
    subtype: str = Field(..., description="Account subtype: 'checking', 'savings', or 'credit_card'")
    name: str = Field(..., description="Account name/institution")
    mask: str = Field(..., description="Last 4 digits of account number")
    current_balance: int = Field(..., description="Current balance in cents")
    available_balance: Optional[int] = Field(None, description="Available balance in cents")
    limit: Optional[int] = Field(None, description="Credit limit in cents (credit cards only)")
    currency: str = Field(default="USD", description="Currency code")
    holder_category: str = Field(..., description="Account holder category: 'personal' or 'business'")
    apr: Optional[float] = Field(None, description="Annual percentage rate (credit cards only)")
    min_payment: Optional[int] = Field(None, description="Minimum payment in cents (credit cards only)")
    is_overdue: bool = Field(default=False, description="Whether account has overdue payments")
    last_payment_amount: Optional[int] = Field(None, description="Last payment amount in cents (credit cards only)")
    last_payment_date: Optional[str] = Field(None, description="Last payment date in ISO 8601 format (credit cards only)")
    next_payment_due_date: Optional[str] = Field(None, description="Next payment due date in ISO 8601 format (credit cards only)")
    last_statement_balance: Optional[int] = Field(None, description="Last statement balance in cents (credit cards only)")
    last_statement_date: Optional[str] = Field(None, description="Last statement date in ISO 8601 format (credit cards only)")
    interest_rate: Optional[float] = Field(None, description="Interest rate (loans only)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "acc_12345",
                    "user_id": "user_67890",
                    "type": "credit",
                    "subtype": "credit_card",
                    "name": "Chase Sapphire Reserve",
                    "mask": "1234",
                    "current_balance": 125000,  # $1,250.00
                    "available_balance": 875000,  # $8,750.00 available credit
                    "limit": 1000000,  # $10,000.00
                    "currency": "USD",
                    "holder_category": "personal",
                    "apr": 18.99,
                    "min_payment": 2500,  # $25.00
                    "is_overdue": False,
                    "last_payment_amount": 50000,  # $500.00
                    "last_payment_date": "2025-10-15T00:00:00Z",
                    "next_payment_due_date": "2025-11-15T00:00:00Z",
                    "last_statement_balance": 150000,  # $1,500.00
                    "last_statement_date": "2025-10-01T00:00:00Z",
                    "interest_rate": None
                }
            ]
        }
    }

    @classmethod
    def from_orm(cls, account):
        """Convert Account ORM model to response schema"""
        return cls(
            id=account.id,
            user_id=account.user_id,
            type=account.type,
            subtype=account.subtype,
            name=account.name,
            mask=account.mask,
            current_balance=account.current_balance,
            available_balance=account.available_balance,
            limit=account.limit,
            currency=account.currency,
            holder_category=account.holder_category,
            apr=account.apr,
            min_payment=account.min_payment,
            is_overdue=account.is_overdue,
            last_payment_amount=account.last_payment_amount,
            last_payment_date=account.last_payment_date.isoformat() + "Z" if account.last_payment_date else None,
            next_payment_due_date=account.next_payment_due_date.isoformat() + "Z" if account.next_payment_due_date else None,
            last_statement_balance=account.last_statement_balance,
            last_statement_date=account.last_statement_date.isoformat() + "Z" if account.last_statement_date else None,
            interest_rate=account.interest_rate
        )
