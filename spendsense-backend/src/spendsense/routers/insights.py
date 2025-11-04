"""Insights and recommendations endpoints"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.schemas.insight import RecommendationResponse
from spendsense.services.recommendations import generate_recommendations
from spendsense.generators.template import TemplateGenerator

# Set up logging
logger = logging.getLogger(__name__)

# Initialize TemplateGenerator as module-level singleton
# This is created once when the module loads, avoiding repeated initialization
generator = TemplateGenerator()

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{user_id}", response_model=list[RecommendationResponse])
async def get_user_insights(
    user_id: str,
    window: int = Query(30, ge=1, le=365, description="Analysis window in days (1-365, default 30)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized financial insights and recommendations for a user.

    This endpoint orchestrates the complete recommendation pipeline:
    1. Assigns a persona based on behavioral signals
    2. Generates relevant educational content
    3. Creates explainable rationales

    Args:
        user_id: User ID to generate insights for
        window: Analysis window in days (default 30, options: 30, 90, 180)
        db: Database session

    Returns:
        list[RecommendationResponse]: List of personalized recommendations (usually 3)

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if recommendation generation fails
    """
    try:
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        logger.info(f"Generating insights for user {user_id} with {window}-day window")

        # Generate recommendations using the complete pipeline
        recommendations = await generate_recommendations(
            db=db,
            user_id=user_id,
            generator=generator,
            window_days=window
        )

        logger.info(
            f"Generated {len(recommendations)} recommendations for user {user_id} "
            f"(persona: {recommendations[0].persona if recommendations else 'none'})"
        )

        # Convert to API response schemas
        return [
            RecommendationResponse.from_recommendation(rec)
            for rec in recommendations
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to generate insights for user {user_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )
