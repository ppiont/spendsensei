"""Transaction schemas for API responses"""

from typing import Optional
from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    """Response schema for transaction data"""
    id: str = Field(..., description="Unique transaction identifier")
    account_id: str = Field(..., description="Account this transaction belongs to")
    date: str = Field(..., description="Transaction date in ISO 8601 format")
    amount: int = Field(..., description="Transaction amount in cents (positive = debit, negative = credit)")
    merchant_name: Optional[str] = Field(None, description="Merchant or payee name")
    category: str = Field(..., description="Transaction category (e.g., FOOD_AND_DRINK, INCOME)")
    pending: bool = Field(default=False, description="Whether transaction is still pending")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "txn_12345",
                    "account_id": "acc_67890",
                    "date": "2025-11-01T14:30:00Z",
                    "amount": 4599,  # $45.99 expense
                    "merchant_name": "Whole Foods",
                    "category": "FOOD_AND_DRINK",
                    "pending": False
                },
                {
                    "id": "txn_12346",
                    "account_id": "acc_67890",
                    "date": "2025-11-01T09:00:00Z",
                    "amount": -300000,  # $3,000.00 income (negative)
                    "merchant_name": "Acme Corp",
                    "category": "INCOME",
                    "pending": False
                }
            ]
        }
    }

    @classmethod
    def from_orm(cls, transaction):
        """Convert Transaction ORM model to response schema"""
        return cls(
            id=transaction.id,
            account_id=transaction.account_id,
            date=transaction.date.isoformat() + "Z",  # ISO 8601 format
            amount=transaction.amount,
            merchant_name=transaction.merchant_name,
            category=transaction.category,
            pending=transaction.pending
        )
