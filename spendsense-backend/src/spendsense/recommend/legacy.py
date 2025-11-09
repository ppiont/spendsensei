"""
Recommendation Engine Module (Legacy Compatibility Layer)

DEPRECATION NOTICE: This module is maintained for backward compatibility.
New code should use recommendation_engine.py with the adapter pattern.

This module provides a legacy function `generate_recommendations()` that wraps
the new StandardRecommendationEngine for backward compatibility. It returns
only educational recommendations (not offers) to match the old interface.

For new code, use:
    from spendsense.recommend.engine import StandardRecommendationEngine
    engine = StandardRecommendationEngine()
    result = await engine.generate_recommendations(db, user_id, window_days)
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from spendsense.recommend.engine import StandardRecommendationEngine
from spendsense.recommend.types import ContentGenerator, EducationItem, Rationale

# Set up logging
logger = logging.getLogger(__name__)


class Recommendation(BaseModel):
    """
    Complete personalized recommendation with content and rationale.

    Combines educational content with explainable reasoning to provide
    transparent, actionable financial guidance.

    NOTE: This model is for backward compatibility. New code should use
    recommendation_engine.Recommendation and recommendation_engine.OfferRecommendation.
    """
    content: EducationItem = Field(..., description="Educational content item from catalog")
    rationale: Rationale = Field(..., description="Explainable rationale for this recommendation")
    persona: str = Field(..., description="Assigned persona type (e.g., 'high_utilization')")
    confidence: float = Field(..., description="Confidence score for persona assignment (0.0-1.0)", ge=0.0, le=1.0)


async def generate_recommendations(
    db: AsyncSession,
    user_id: str,
    generator: ContentGenerator = None,
    window_days: int = 30
) -> List[Recommendation]:
    """
    Generate personalized recommendations for a user (Legacy).

    DEPRECATION NOTICE: This function is maintained for backward compatibility.
    It wraps the new StandardRecommendationEngine but only returns educational
    recommendations (not partner offers) to match the old interface.

    New code should use:
        from spendsense.recommend.engine import StandardRecommendationEngine
        engine = StandardRecommendationEngine()
        result = await engine.generate_recommendations(db, user_id, window_days)

    Args:
        db: Async SQLAlchemy database session
        user_id: User identifier
        generator: ContentGenerator implementation (ignored - uses StandardRecommendationEngine)
        window_days: Analysis window in days (30 or 180, default: 30)

    Returns:
        List of Recommendation objects (education only, no offers)

    Raises:
        ValueError: If invalid parameters provided
        Exception: For unexpected errors during recommendation generation
    """
    logger.warning(
        f"[DEPRECATED] generate_recommendations() called for user {user_id}. "
        "Consider migrating to StandardRecommendationEngine for offers support."
    )

    # Use the new StandardRecommendationEngine
    if generator is not None:
        engine = StandardRecommendationEngine(content_generator=generator)
    else:
        engine = StandardRecommendationEngine()

    try:
        # Generate using new engine
        result = await engine.generate_recommendations(
            db=db,
            user_id=user_id,
            window_days=window_days
        )

        # Convert new Recommendation format to legacy format (education only)
        legacy_recommendations = []
        for rec in result.education_recommendations:
            legacy_rec = Recommendation(
                content=rec.content,
                rationale=rec.rationale,
                persona=rec.persona,
                confidence=rec.confidence
            )
            legacy_recommendations.append(legacy_rec)

        logger.info(
            f"[DEPRECATED] Returning {len(legacy_recommendations)} education recommendations "
            f"(offers not included in legacy format)"
        )

        return legacy_recommendations

    except Exception as e:
        logger.error(
            f"Error in legacy generate_recommendations for user {user_id}: {str(e)}",
            exc_info=True
        )
        raise
