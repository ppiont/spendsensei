"""Transaction schemas for API responses"""

from typing import Optional
from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    """Response schema for transaction data - Plaid-compliant"""
    id: str = Field(..., description="Unique transaction identifier")
    account_id: str = Field(..., description="Account this transaction belongs to")
    date: str = Field(..., description="Transaction date in ISO 8601 format")
    amount: int = Field(..., description="Transaction amount in cents (positive = debit, negative = credit)")
    merchant_name: Optional[str] = Field(None, description="Merchant or payee name")
    merchant_entity_id: Optional[str] = Field(None, description="Normalized merchant entity ID for recurring merchants")
    personal_finance_category_primary: str = Field(..., description="Primary category (e.g., FOOD_AND_DRINK, INCOME)")
    personal_finance_category_detailed: Optional[str] = Field(None, description="Detailed category (e.g., RESTAURANTS, GROCERIES)")
    payment_channel: Optional[str] = Field(None, description="Payment channel: 'online', 'in_store', or 'other'")
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
                    "merchant_entity_id": "whole_foods_market",
                    "personal_finance_category_primary": "FOOD_AND_DRINK",
                    "personal_finance_category_detailed": "GROCERIES",
                    "payment_channel": "in_store",
                    "pending": False
                },
                {
                    "id": "txn_12346",
                    "account_id": "acc_67890",
                    "date": "2025-11-01T09:00:00Z",
                    "amount": -300000,  # $3,000.00 income (negative)
                    "merchant_name": "Acme Corp",
                    "merchant_entity_id": None,
                    "personal_finance_category_primary": "INCOME",
                    "personal_finance_category_detailed": "INCOME",
                    "payment_channel": "other",
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
            merchant_entity_id=transaction.merchant_entity_id,
            personal_finance_category_primary=transaction.personal_finance_category_primary,
            personal_finance_category_detailed=transaction.personal_finance_category_detailed,
            payment_channel=transaction.payment_channel,
            pending=transaction.pending
        )
