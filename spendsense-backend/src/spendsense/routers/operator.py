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
    OperatorOverrideResponse,
    InspectUserResponse
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


@router.get("/inspect/{user_id}", response_model=InspectUserResponse)
async def inspect_user(
    user_id: str,
    window: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """
    Inspect user data for operator debugging (no consent checks).

    This endpoint provides comprehensive user data for internal review
    and debugging purposes. Unlike the /insights endpoint, this endpoint
    does NOT check consent and returns all available data.

    Args:
        user_id: User ID to inspect
        window: Analysis window in days (default 30)
        db: Database session

    Returns:
        InspectUserResponse: Comprehensive user data including signals and recommendations

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if error occurs
    """
    from spendsense.models.account import Account
    from spendsense.models.transaction import Transaction

    try:
        # Get user (no consent check)
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Get account count
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()
        account_count = len(accounts)

        # Get transaction count
        transactions_result = await db.execute(
            select(Transaction).where(Transaction.account_id.in_([a.id for a in accounts]))
        )
        transactions = transactions_result.scalars().all()
        transaction_count = len(transactions)

        # If user has consented, generate recommendations
        persona_type = None
        confidence = None
        signals_summary = {}
        education_recommendations = []
        offer_recommendations = []

        if user.consent:
            try:
                # Generate recommendations using engine
                rec_result = await engine.generate_recommendations(
                    db=db,
                    user_id=user_id,
                    window_days=window
                )

                persona_type = rec_result.persona_type
                confidence = rec_result.confidence
                signals_summary = rec_result.signals_summary
                education_recommendations = [
                    {
                        "id": rec.content.id,
                        "title": rec.content.title,
                        "summary": rec.content.summary,
                        "relevance_score": rec.content.relevance_score
                    }
                    for rec in rec_result.education_recommendations
                ]
                offer_recommendations = [
                    {
                        "id": rec.offer.id,
                        "title": rec.offer.title,
                        "provider": rec.offer.provider,
                        "eligibility_met": rec.offer.eligibility_met
                    }
                    for rec in rec_result.offer_recommendations
                ]
            except Exception as e:
                # Log error but continue
                signals_summary = {"error": str(e)}

        return InspectUserResponse(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            consent_status=user.consent,
            persona_type=persona_type,
            confidence=confidence,
            signals_summary=signals_summary,
            education_recommendations=education_recommendations,
            offer_recommendations=offer_recommendations,
            account_count=account_count,
            transaction_count=transaction_count,
            window_days=window
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inspect user: {str(e)}"
        )
