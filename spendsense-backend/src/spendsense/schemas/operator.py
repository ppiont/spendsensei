"""Operator schemas for internal review and management"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class UserRecommendationSummary(BaseModel):
    """Summary of recommendations for a user in review queue"""
    user_id: str = Field(..., description="User ID")
    user_name: str = Field(..., description="User name")
    user_email: str = Field(..., description="User email")
    persona_type: str = Field(..., description="Assigned persona")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Persona confidence")
    education_count: int = Field(..., description="Number of education recommendations")
    offer_count: int = Field(..., description="Number of partner offers")
    signals_summary: Dict[str, Any] = Field(..., description="Behavioral signals")
    generated_at: str = Field(..., description="When insights were generated (ISO 8601)")


class ReviewQueueResponse(BaseModel):
    """Response schema for operator review queue"""
    pending_reviews: List[UserRecommendationSummary] = Field(..., description="Users with recommendations to review")
    total_count: int = Field(..., description="Total number of users in queue")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pending_reviews": [
                        {
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "user_name": "John Doe",
                            "user_email": "john@example.com",
                            "persona_type": "high_utilization",
                            "confidence": 0.92,
                            "education_count": 3,
                            "offer_count": 2,
                            "signals_summary": {
                                "credit": {"overall_utilization": 85.5}
                            },
                            "generated_at": "2025-11-05T12:00:00Z"
                        }
                    ],
                    "total_count": 1
                }
            ]
        }
    }


class ApprovalRequest(BaseModel):
    """Request to approve or flag a recommendation"""
    user_id: str = Field(..., description="User ID")
    recommendation_id: str = Field(..., description="Recommendation or offer ID")
    recommendation_type: str = Field(..., description="Type: 'education' or 'offer'")
    action: str = Field(..., description="Action: 'approve' or 'flag'")
    reason: Optional[str] = Field(None, description="Reason for flagging (required if action is 'flag')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "recommendation_id": "offer_balance_transfer_01",
                    "recommendation_type": "offer",
                    "action": "flag",
                    "reason": "User may not qualify based on credit history"
                }
            ]
        }
    }


class ApprovalResponse(BaseModel):
    """Response after approval/flag action"""
    status: str = Field(..., description="Action status")
    message: str = Field(..., description="Result message")
    recommendation_id: str = Field(..., description="ID of affected recommendation")


class OperatorOverrideResponse(BaseModel):
    """Response schema for operator override data"""
    id: str = Field(..., description="Unique override identifier")
    user_id: str = Field(..., description="User ID the override applies to")
    recommendation_id: str = Field(..., description="Recommendation or offer ID")
    recommendation_type: str = Field(..., description="Type of recommendation")
    action: str = Field(..., description="Action taken (approve or flag)")
    reason: Optional[str] = Field(None, description="Reason for action")
    operator_id: str = Field(..., description="Operator who made the override")
    created_at: str = Field(..., description="ISO 8601 timestamp of override creation")

    @classmethod
    def from_orm(cls, override):
        """Convert OperatorOverride ORM model to response schema"""
        return cls(
            id=override.id,
            user_id=override.user_id,
            recommendation_id=override.recommendation_id,
            recommendation_type=override.recommendation_type,
            action=override.action.value if hasattr(override.action, 'value') else override.action,
            reason=override.reason,
            operator_id=override.operator_id,
            created_at=override.created_at.isoformat() + "Z"
        )
