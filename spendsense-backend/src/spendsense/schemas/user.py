"""User schemas for API requests and responses"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request schema for creating a new user"""
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response schema for user data"""
    id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    consent: bool = Field(..., description="Whether user has given consent")
    created_at: str = Field(..., description="ISO 8601 timestamp of user creation")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "consent": True,
                    "created_at": "2025-11-03T12:00:00Z"
                }
            ]
        }
    }

    @classmethod
    def from_orm(cls, user):
        """Convert User ORM model to response schema"""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            consent=user.consent,
            created_at=user.created_at.isoformat() + "Z"  # ISO 8601 format
        )


class AccountSummary(BaseModel):
    """Summary of user accounts for profile"""
    total_accounts: int = Field(..., description="Total number of accounts")
    depository_accounts: int = Field(..., description="Number of depository accounts")
    credit_accounts: int = Field(..., description="Number of credit accounts")
    total_balance_cents: int = Field(..., description="Total balance across all accounts (in cents)")
    total_available_cents: int = Field(..., description="Total available balance (in cents)")


class PersonaSummary(BaseModel):
    """Summary of user's assigned persona"""
    persona_type: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for persona assignment")
    assigned_at: Optional[str] = Field(None, description="When persona was assigned (ISO 8601)")


class ProfileResponse(BaseModel):
    """Comprehensive user profile response"""
    user: UserResponse = Field(..., description="User information")
    accounts: AccountSummary = Field(..., description="Account summary")
    persona: Optional[PersonaSummary] = Field(None, description="Current persona assignment")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "consent": True,
                        "created_at": "2025-11-03T12:00:00Z"
                    },
                    "accounts": {
                        "total_accounts": 3,
                        "depository_accounts": 2,
                        "credit_accounts": 1,
                        "total_balance_cents": 150000,
                        "total_available_cents": 148500
                    },
                    "persona": {
                        "persona_type": "savings_builder",
                        "confidence": 0.85,
                        "assigned_at": "2025-11-05T10:00:00Z"
                    }
                }
            ]
        }
    }
