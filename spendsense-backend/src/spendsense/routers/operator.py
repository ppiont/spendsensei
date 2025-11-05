"""Operator endpoints for internal review and management"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.schemas.operator import ReviewQueueResponse, UserRecommendationSummary
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
