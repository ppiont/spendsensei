"""Operator endpoints for internal review and management"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.models.operator_override import OperatorOverride
from spendsense.schemas.operator import (
    ReviewQueueResponse,
    UserRecommendationSummary,
    ApprovalRequest,
    ApprovalResponse,
    OperatorOverrideResponse
)
from spendsense.services.recommendation_engine import StandardRecommendationEngine

router = APIRouter(prefix="/operator", tags=["operator"])

# Initialize recommendation engine
engine = StandardRecommendationEngine()


@router.get("/review", response_model=ReviewQueueResponse)
async def get_review_queue(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get queue of user recommendations pending operator review.

    This endpoint provides operators with a view of recent recommendations
    generated for users, including persona assignments, signal summaries,
    and recommendation counts for quality assurance.

    Args:
        limit: Maximum number of users to include (default 10)
        db: Database session

    Returns:
        ReviewQueueResponse: List of users with recommendation summaries

    Raises:
        HTTPException: 500 if error occurs
    """
    try:
        # Get all users with consent
        result = await db.execute(
            select(User)
            .where(User.consent == True)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        users = result.scalars().all()

        # Generate recommendation summaries for each user
        pending_reviews = []

        for user in users:
            try:
                # Generate recommendations using the engine
                rec_result = await engine.generate_recommendations(
                    db=db,
                    user_id=user.id,
                    window_days=30
                )

                # Create summary
                summary = UserRecommendationSummary(
                    user_id=user.id,
                    user_name=user.name,
                    user_email=user.email,
                    persona_type=rec_result.persona_type,
                    confidence=rec_result.confidence,
                    education_count=len(rec_result.education_recommendations),
                    offer_count=len(rec_result.offer_recommendations),
                    signals_summary=rec_result.signals_summary,
                    generated_at=datetime.now(timezone.utc).isoformat() + "Z"
                )

                pending_reviews.append(summary)

            except Exception as e:
                # Skip users with errors (e.g., no transactions)
                continue

        return ReviewQueueResponse(
            pending_reviews=pending_reviews,
            total_count=len(pending_reviews)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch review queue: {str(e)}"
        )


@router.post("/approve", response_model=OperatorOverrideResponse, status_code=201)
async def approve_recommendation(
    request: ApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a recommendation for a user.

    Creates an operator override record marking the recommendation as approved.
    The insights endpoint will respect this override when filtering recommendations.

    Args:
        request: Approval request with user_id, recommendation_id, and action
        db: Database session

    Returns:
        OperatorOverrideResponse: Created override record

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if action is not 'approve'
        HTTPException: 500 if database error occurs
    """
    try:
        # Validate action
        if request.action != "approve":
            raise HTTPException(
                status_code=400,
                detail="This endpoint is for approvals only. Use /operator/flag for flagging."
            )

        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {request.user_id} not found"
            )

        # Generate UUID for override
        override_id = f"ov_{uuid.uuid4().hex[:12]}"

        # Create override record
        new_override = OperatorOverride(
            id=override_id,
            user_id=request.user_id,
            recommendation_id=request.recommendation_id,
            recommendation_type=request.recommendation_type,
            action="approve",
            reason=None,  # Approvals don't need a reason
            operator_id="system",  # TODO: Use authenticated operator ID
            created_at=datetime.now(timezone.utc)
        )

        # Add to database
        db.add(new_override)
        await db.commit()
        await db.refresh(new_override)

        # Return response
        return OperatorOverrideResponse.from_orm(new_override)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create approval: {str(e)}"
        )


@router.post("/flag", response_model=OperatorOverrideResponse, status_code=201)
async def flag_recommendation(
    request: ApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Flag a recommendation for quality issues.

    Creates an operator override record marking the recommendation as flagged.
    The insights endpoint will filter out flagged recommendations.

    Args:
        request: Flag request with user_id, recommendation_id, action, and reason
        db: Database session

    Returns:
        OperatorOverrideResponse: Created override record

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if action is not 'flag' or reason is missing
        HTTPException: 500 if database error occurs
    """
    try:
        # Validate action
        if request.action != "flag":
            raise HTTPException(
                status_code=400,
                detail="This endpoint is for flagging only. Use /operator/approve for approvals."
            )

        # Validate reason is provided
        if not request.reason:
            raise HTTPException(
                status_code=400,
                detail="Reason is required when flagging a recommendation"
            )

        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {request.user_id} not found"
            )

        # Generate UUID for override
        override_id = f"ov_{uuid.uuid4().hex[:12]}"

        # Create override record
        new_override = OperatorOverride(
            id=override_id,
            user_id=request.user_id,
            recommendation_id=request.recommendation_id,
            recommendation_type=request.recommendation_type,
            action="flag",
            reason=request.reason,
            operator_id="system",  # TODO: Use authenticated operator ID
            created_at=datetime.now(timezone.utc)
        )

        # Add to database
        db.add(new_override)
        await db.commit()
        await db.refresh(new_override)

        # Return response
        return OperatorOverrideResponse.from_orm(new_override)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create flag: {str(e)}"
        )
