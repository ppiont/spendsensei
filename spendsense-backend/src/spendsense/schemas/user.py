"""User schemas for API requests and responses"""

from datetime import datetime
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
