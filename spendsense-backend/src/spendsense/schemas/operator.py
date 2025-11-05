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
    action: str = Field(..., description="Action: 'approve' or 'flag'")
    reason: Optional[str] = Field(None, description="Reason for flagging (required if action is 'flag')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "recommendation_id": "offer_balance_transfer_01",
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
