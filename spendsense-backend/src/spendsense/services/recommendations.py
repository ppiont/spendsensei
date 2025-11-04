"""
Recommendation Engine Module

This module orchestrates the complete recommendation pipeline by combining:
1. Persona assignment (from personas.py)
2. Educational content generation (from generators)
3. Rationale generation (from generators)

The result is a list of personalized recommendations with full explainability
and traceability from raw signals through to final content.
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from spendsense.services.personas import assign_persona
from spendsense.generators.base import ContentGenerator, EducationItem, Rationale
from spendsense.generators.template import TemplateGenerator

# Set up logging
logger = logging.getLogger(__name__)


class Recommendation(BaseModel):
    """
    Complete personalized recommendation with content and rationale.

    Combines educational content with explainable reasoning to provide
    transparent, actionable financial guidance.
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
    Generate personalized recommendations for a user.

    This is the main orchestration function that ties together the entire
    recommendation pipeline:

    1. Assign persona based on behavioral signals
    2. Generate top 3 educational content items
    3. For each item, generate explainable rationale
    4. Build complete Recommendation objects

    The function provides full traceability from raw transaction data through
    signal computation, persona assignment, content selection, and rationale
    generation.

    Args:
        db: Async SQLAlchemy database session
        user_id: User identifier
        generator: ContentGenerator implementation (default: TemplateGenerator)
        window_days: Analysis window in days (30 or 180, default: 30)

    Returns:
        List of Recommendation objects (typically 3) with content and rationales

    Raises:
        HTTPException: If user not found or signal computation fails
        ValueError: If invalid parameters provided
        Exception: For unexpected errors during recommendation generation

    Examples:
        >>> # Using default TemplateGenerator
        >>> recommendations = await generate_recommendations(db, "user_123")
        >>>
        >>> # Using custom generator with 180-day window
        >>> llm_gen = LLMGenerator(api_key="...")
        >>> recommendations = await generate_recommendations(
        ...     db, "user_123", generator=llm_gen, window_days=180
        ... )
        >>>
        >>> # Access recommendation data
        >>> for rec in recommendations:
        ...     print(f"Title: {rec.content.title}")
        ...     print(f"Rationale: {rec.rationale.explanation}")
        ...     print(f"Persona: {rec.persona} (confidence: {rec.confidence})")
    """
    logger.info(f"Generating recommendations for user {user_id}, window: {window_days} days")

    # Validate inputs
    if not user_id:
        raise ValueError("user_id is required")
    if window_days not in [30, 180]:
        raise ValueError("window_days must be 30 or 180")

    # Use default TemplateGenerator if none provided
    if generator is None:
        logger.debug("No generator provided, using default TemplateGenerator")
        generator = TemplateGenerator()

    try:
        # Step 1: Assign persona and get signals
        logger.info(f"Step 1: Assigning persona for user {user_id}")
        persona_data = await assign_persona(db, user_id, window_days)

        persona_type = persona_data["persona_type"]
        confidence = persona_data["confidence"]
        signals = persona_data["signals"]

        logger.info(
            f"Persona assigned: {persona_type} (confidence: {confidence:.2f}), "
            f"signals: credit={bool(signals.credit)}, income={bool(signals.income)}, "
            f"subscriptions={bool(signals.subscriptions)}, savings={bool(signals.savings)}"
        )

        # Step 2: Generate top 3 educational content items
        logger.info(f"Step 2: Generating education content for persona '{persona_type}'")
        education_items = await generator.generate_education(
            persona_type=persona_type,
            signals=signals,
            limit=3
        )

        if not education_items:
            logger.warning(f"No education items generated for persona {persona_type}")
            return []

        logger.info(
            f"Generated {len(education_items)} education items: "
            f"{[item.id for item in education_items]}"
        )

        # Step 3: For each content item, generate rationale and build recommendation
        logger.info(f"Step 3: Generating rationales for {len(education_items)} items")
        recommendations = []

        for idx, content_item in enumerate(education_items, 1):
            logger.debug(f"Generating rationale {idx}/{len(education_items)} for content '{content_item.id}'")

            # Generate explainable rationale
            rationale = await generator.generate_rationale(
                persona_type=persona_type,
                confidence=confidence,
                signals=signals
            )

            # Build complete recommendation
            recommendation = Recommendation(
                content=content_item,
                rationale=rationale,
                persona=persona_type,
                confidence=confidence
            )

            recommendations.append(recommendation)

            logger.debug(
                f"Built recommendation {idx}: content_id={content_item.id}, "
                f"relevance={content_item.relevance_score:.2f}, "
                f"signals={len(rationale.key_signals)}"
            )

        logger.info(
            f"Successfully generated {len(recommendations)} recommendations for user {user_id} "
            f"(persona: {persona_type}, confidence: {confidence:.2f})"
        )

        return recommendations

    except Exception as e:
        logger.error(
            f"Error generating recommendations for user {user_id}: {str(e)}",
            exc_info=True
        )
        raise
