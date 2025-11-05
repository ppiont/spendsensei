"""Feedback schemas for API requests and responses"""

from typing import Optional
from pydantic import BaseModel, Field

from spendsense.models.feedback import FeedbackType


class FeedbackCreate(BaseModel):
    """Request schema for creating feedback"""
    user_id: str = Field(..., description="User providing feedback")
    recommendation_id: str = Field(..., description="ID of recommendation being rated")
    recommendation_type: str = Field(..., description="Type of recommendation (education or offer)")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "recommendation_id": "edu_emergency_fund_01",
                    "recommendation_type": "education",
                    "feedback_type": "helpful",
                    "comment": "This tip helped me understand emergency funds better!"
                }
            ]
        }
    }


class FeedbackResponse(BaseModel):
    """Response schema for feedback data"""
    id: str = Field(..., description="Unique feedback identifier")
    user_id: str = Field(..., description="User who provided feedback")
    recommendation_id: str = Field(..., description="ID of recommendation rated")
    recommendation_type: str = Field(..., description="Type of recommendation")
    feedback_type: str = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, description="Optional comment")
    created_at: str = Field(..., description="ISO 8601 timestamp of feedback creation")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "fb_123456",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "recommendation_id": "edu_emergency_fund_01",
                    "recommendation_type": "education",
                    "feedback_type": "helpful",
                    "comment": "This tip helped me understand emergency funds better!",
                    "created_at": "2025-11-05T12:00:00Z"
                }
            ]
        }
    }

    @classmethod
    def from_orm(cls, feedback):
        """Convert Feedback ORM model to response schema"""
        return cls(
            id=feedback.id,
            user_id=feedback.user_id,
            recommendation_id=feedback.recommendation_id,
            recommendation_type=feedback.recommendation_type,
            feedback_type=feedback.feedback_type.value if hasattr(feedback.feedback_type, 'value') else feedback.feedback_type,
            comment=feedback.comment,
            created_at=feedback.created_at.isoformat() + "Z"
        )
