"""Insights and recommendations endpoints"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.models.operator_override import OperatorOverride
from spendsense.schemas.insight import (
    RecommendationResponse,
    OfferRecommendationResponse,
    InsightsResponse,
    EducationItemResponse,
    PartnerOfferResponse,
    RationaleResponse
)
from spendsense.recommend.engine import StandardRecommendationEngine
from spendsense.guardrails import check_consent

# Set up logging
logger = logging.getLogger(__name__)

# Initialize StandardRecommendationEngine as module-level singleton
# This is created once when the module loads, avoiding repeated initialization
# To swap to AI engine: engine = AIRecommendationEngine(ai_provider="anthropic")
engine = StandardRecommendationEngine()

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{user_id}", response_model=InsightsResponse)
async def get_user_insights(
    user_id: str,
    window: int = Query(30, ge=1, le=365, description="Analysis window in days (1-365, default 30)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized financial insights and recommendations for a user.

    This endpoint orchestrates the complete recommendation pipeline:
    1. Assigns a persona based on behavioral signals
    2. Generates relevant educational content (3 items)
    3. Generates relevant partner offers (0-3 eligible items)
    4. Creates explainable rationales for each recommendation

    The response includes both educational content and partner product offers
    that match the user's financial persona and eligibility criteria.

    Args:
        user_id: User ID to generate insights for
        window: Analysis window in days (default 30, options: 30, 90, 180)
        db: Database session

    Returns:
        InsightsResponse: Personalized recommendations (education + offers) with disclaimer

    Raises:
        HTTPException: 403 if user has not provided consent
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

        # Check user consent - if not consented, return empty response instead of 403
        if not check_consent(user.consent):
            logger.warning(f"User {user_id} has not provided consent - returning empty insights")
            return InsightsResponse(
                persona_type="consent_required",
                confidence=0.0,
                education_recommendations=[],
                offer_recommendations=[],
                signals_summary={},
                consent_required=True
            )

        logger.info(f"Generating insights for user {user_id} with {window}-day window")

        # Generate recommendations using the recommendation engine (adapter pattern)
        result = await engine.generate_recommendations(
            db=db,
            user_id=user_id,
            window_days=window
        )

        logger.info(
            f"Generated insights for user {user_id}: persona={result.persona_type}, "
            f"education={len(result.education_recommendations)}, offers={len(result.offer_recommendations)}"
        )

        # Get operator overrides for this user to filter flagged recommendations
        overrides_result = await db.execute(
            select(OperatorOverride)
            .where(OperatorOverride.user_id == user_id)
            .where(OperatorOverride.action == "flag")
        )
        overrides = overrides_result.scalars().all()

        # Create set of flagged recommendation IDs for efficient lookup
        flagged_ids = {override.recommendation_id for override in overrides}

        logger.info(f"Found {len(flagged_ids)} flagged recommendations for user {user_id}")

        # Filter out flagged recommendations
        filtered_education = [
            rec for rec in result.education_recommendations
            if rec.content.id not in flagged_ids
        ]

        filtered_offers = [
            rec for rec in result.offer_recommendations
            if rec.offer.id not in flagged_ids
        ]

        logger.info(
            f"After filtering: education={len(filtered_education)}, offers={len(filtered_offers)}"
        )

        # Convert to API response schemas
        education_responses = [
            _convert_education_recommendation(rec)
            for rec in filtered_education
        ]

        offer_responses = [
            _convert_offer_recommendation(rec)
            for rec in filtered_offers
        ]

        return InsightsResponse(
            persona_type=result.persona_type,
            confidence=result.confidence,
            education_recommendations=education_responses,
            offer_recommendations=offer_responses,
            signals_summary=result.signals_summary,
            consent_required=False
        )

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


def _convert_education_recommendation(rec) -> RecommendationResponse:
    """Convert Recommendation to RecommendationResponse schema."""
    return RecommendationResponse(
        content=EducationItemResponse(
            id=rec.content.id,
            title=rec.content.title,
            summary=rec.content.summary,
            body=rec.content.body,
            cta=rec.content.cta,
            source=rec.content.source,
            relevance_score=rec.content.relevance_score
        ),
        rationale=RationaleResponse(
            persona_type=rec.rationale.persona_type,
            confidence=rec.rationale.confidence,
            explanation=rec.rationale.explanation,
            key_signals=rec.rationale.key_signals
        ),
        persona=rec.persona,
        confidence=rec.confidence
    )


def _convert_offer_recommendation(rec) -> OfferRecommendationResponse:
    """Convert OfferRecommendation to OfferRecommendationResponse schema."""
    return OfferRecommendationResponse(
        offer=PartnerOfferResponse(
            id=rec.offer.id,
            title=rec.offer.title,
            provider=rec.offer.provider,
            offer_type=rec.offer.offer_type,
            summary=rec.offer.summary,
            benefits=rec.offer.benefits,
            eligibility_explanation=rec.offer.eligibility_explanation,
            cta=rec.offer.cta,
            cta_url=rec.offer.cta_url,
            disclaimer=rec.offer.disclaimer,
            relevance_score=rec.offer.relevance_score,
            eligibility_met=rec.offer.eligibility_met
        ),
        rationale=RationaleResponse(
            persona_type=rec.rationale.persona_type,
            confidence=rec.rationale.confidence,
            explanation=rec.rationale.explanation,
            key_signals=rec.rationale.key_signals
        ),
        persona=rec.persona,
        confidence=rec.confidence
    )
