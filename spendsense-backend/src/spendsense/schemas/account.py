"""Account schemas for API responses"""

from typing import Optional
from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """Response schema for account data"""
    id: str = Field(..., description="Unique account identifier")
    user_id: str = Field(..., description="User who owns this account")
    type: str = Field(..., description="Account type: 'depository' or 'credit'")
    subtype: str = Field(..., description="Account subtype: 'checking', 'savings', or 'credit_card'")
    name: str = Field(..., description="Account name/institution")
    mask: str = Field(..., description="Last 4 digits of account number")
    balance: int = Field(..., description="Current balance in cents")
    limit: Optional[int] = Field(None, description="Credit limit in cents (credit cards only)")
    currency: str = Field(default="USD", description="Currency code")
    apr: Optional[float] = Field(None, description="Annual percentage rate (credit cards only)")
    min_payment: Optional[int] = Field(None, description="Minimum payment in cents (credit cards only)")
    is_overdue: bool = Field(default=False, description="Whether account has overdue payments")

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
                    "balance": 125000,  # $1,250.00
                    "limit": 1000000,  # $10,000.00
                    "currency": "USD",
                    "apr": 18.99,
                    "min_payment": 2500,  # $25.00
                    "is_overdue": False
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
            balance=account.balance,
            limit=account.limit,
            currency=account.currency,
            apr=account.apr,
            min_payment=account.min_payment,
            is_overdue=account.is_overdue
        )
