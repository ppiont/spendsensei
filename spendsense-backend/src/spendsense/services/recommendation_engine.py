"""
Recommendation Engine Adapters

This module defines the abstract interface for recommendation engines and provides
multiple implementations using the adapter pattern. This allows seamless swapping
between deterministic (template-based) and AI-powered recommendation strategies.

Architecture:
- RecommendationEngine (Abstract Base): Defines the interface
- StandardRecommendationEngine: Deterministic, template-based (default)
- AIRecommendationEngine: AI-powered, dynamic (future implementation)

Key Distinction:
- ContentGenerator (existing): HOW content is generated (template vs LLM)
- RecommendationEngine (this): WHICH content to recommend and pipeline orchestration

An AI recommendation engine could:
- Dynamically decide the mix of education vs offers
- Use ML to rank content beyond signal matching
- Generate custom recommendations not in catalog
- Personalize strategy based on user behavior patterns
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from spendsense.services.personas import assign_persona
from spendsense.generators.base import ContentGenerator, EducationItem, Rationale, PartnerOffer
from spendsense.generators.template import TemplateGenerator
from spendsense.services.features import BehaviorSignals

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


class OfferRecommendation(BaseModel):
    """
    Partner offer recommendation with eligibility and rationale.

    Represents a financial product/service offer that the user is eligible for,
    with explanation of why it's relevant to their situation.
    """
    offer: PartnerOffer = Field(..., description="Partner offer details with eligibility met")
    rationale: Rationale = Field(..., description="Explainable rationale for this offer")
    persona: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona confidence score (0.0-1.0)", ge=0.0, le=1.0)


class RecommendationResult(BaseModel):
    """
    Complete recommendation result containing education and offers.

    Provides a structured response with both educational content and
    partner product offers, along with persona information.
    """
    persona_type: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona assignment confidence", ge=0.0, le=1.0)
    education_recommendations: List[Recommendation] = Field(..., description="Educational content recommendations (3-5)")
    offer_recommendations: List[OfferRecommendation] = Field(..., description="Partner offer recommendations (0-3)")
    signals_summary: Dict[str, Any] = Field(..., description="Summary of detected behavioral signals")


class RecommendationEngine(ABC):
    """
    Abstract base class for recommendation engines.

    Defines the interface that all recommendation engine implementations must follow.
    This enables flexible swapping between deterministic and AI-powered strategies.

    Implementations should orchestrate:
    1. Persona assignment
    2. Content/offer selection
    3. Rationale generation
    4. Result aggregation
    """

    @abstractmethod
    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        window_days: int = 30
    ) -> RecommendationResult:
        """
        Generate personalized recommendations for a user.

        Args:
            db: Async SQLAlchemy database session
            user_id: User identifier
            window_days: Analysis window in days (30 or 180, default: 30)

        Returns:
            RecommendationResult with education and offer recommendations

        Raises:
            ValueError: If invalid parameters provided
            Exception: For unexpected errors during generation
        """
        pass


class StandardRecommendationEngine(RecommendationEngine):
    """
    Standard deterministic recommendation engine.

    Uses template-based content generation with hardcoded logic:
    - Returns exactly 3 educational items
    - Returns up to 3 partner offers (if eligible)
    - Uses signal-based relevance scoring
    - Deterministic and reproducible

    This is the default implementation and provides transparent,
    explainable recommendations without AI dependencies.
    """

    def __init__(self, content_generator: ContentGenerator = None):
        """
        Initialize standard recommendation engine.

        Args:
            content_generator: ContentGenerator implementation (default: TemplateGenerator)
        """
        self.generator = content_generator or TemplateGenerator()
        logger.info(f"Initialized StandardRecommendationEngine with {type(self.generator).__name__}")

    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        window_days: int = 30
    ) -> RecommendationResult:
        """
        Generate recommendations using deterministic template-based approach.

        Pipeline:
        1. Assign persona from behavioral signals
        2. Generate 3 educational content items
        3. Generate up to 3 eligible partner offers
        4. Create rationales for each recommendation
        5. Package into RecommendationResult

        Args:
            db: Async SQLAlchemy database session
            user_id: User identifier
            window_days: Analysis window in days (30 or 180)

        Returns:
            RecommendationResult with 3 education + 0-3 offers
        """
        logger.info(f"[StandardEngine] Generating recommendations for user {user_id}, window: {window_days}d")

        # Validate inputs
        if not user_id:
            raise ValueError("user_id is required")
        if window_days not in [30, 180]:
            raise ValueError("window_days must be 30 or 180")

        # Step 1: Assign persona and get signals
        logger.info(f"[StandardEngine] Step 1: Assigning persona")
        persona_data = await assign_persona(db, user_id, window_days)

        persona_type = persona_data["persona_type"]
        confidence = persona_data["confidence"]
        signals = persona_data["signals"]

        logger.info(
            f"[StandardEngine] Persona: {persona_type} (confidence: {confidence:.2f}), "
            f"signals detected: {self._count_signals(signals)}"
        )

        # Step 2: Query user's accounts for offer eligibility checking
        from sqlalchemy import select
        from spendsense.models.account import Account

        stmt = select(Account).where(Account.user_id == user_id)
        result = await db.execute(stmt)
        accounts = list(result.scalars().all())
        logger.info(f"[StandardEngine] Found {len(accounts)} accounts for eligibility checking")

        # Step 3: Generate educational content (3 items)
        logger.info(f"[StandardEngine] Step 2: Generating 3 education items")
        education_items = await self.generator.generate_education(
            persona_type=persona_type,
            signals=signals,
            limit=3
        )

        if not education_items:
            logger.warning(f"[StandardEngine] No education items generated")
            education_items = []

        logger.info(f"[StandardEngine] Generated {len(education_items)} education items")

        # Step 4: Generate partner offers (up to 3 eligible)
        logger.info(f"[StandardEngine] Step 3: Generating partner offers")
        offer_items = await self.generator.generate_offers(
            persona_type=persona_type,
            signals=signals,
            accounts=accounts,
            limit=3
        )

        logger.info(f"[StandardEngine] Generated {len(offer_items)} eligible offers")

        # Step 5: Generate content-specific rationale for each education item
        logger.info(f"[StandardEngine] Step 4: Generating content-specific rationales")
        education_recommendations = []

        for content_item in education_items:
            # Use content-specific rationale generation
            rationale = await self.generator.generate_content_rationale(
                content_item=content_item,
                persona_type=persona_type,
                confidence=confidence,
                signals=signals
            )

            recommendation = Recommendation(
                content=content_item,
                rationale=rationale,
                persona=persona_type,
                confidence=confidence
            )
            education_recommendations.append(recommendation)

        # Step 6: Generate rationale for each offer
        offer_recommendations = []

        for offer_item in offer_items:
            # Offers use the same rationale as education (explains persona)
            rationale = await self.generator.generate_rationale(
                persona_type=persona_type,
                confidence=confidence,
                signals=signals
            )

            offer_rec = OfferRecommendation(
                offer=offer_item,
                rationale=rationale,
                persona=persona_type,
                confidence=confidence
            )
            offer_recommendations.append(offer_rec)

        # Step 7: Create signals summary for transparency
        signals_summary = self._create_signals_summary(signals)

        # Step 8: Package result
        result = RecommendationResult(
            persona_type=persona_type,
            confidence=confidence,
            education_recommendations=education_recommendations,
            offer_recommendations=offer_recommendations,
            signals_summary=signals_summary
        )

        logger.info(
            f"[StandardEngine] Success: {len(education_recommendations)} education + "
            f"{len(offer_recommendations)} offers for user {user_id}"
        )

        return result

    def _count_signals(self, signals: BehaviorSignals) -> int:
        """Count number of signal categories detected."""
        count = 0
        if signals.credit:
            count += 1
        if signals.income:
            count += 1
        if signals.subscriptions:
            count += 1
        if signals.savings:
            count += 1
        return count

    def _create_signals_summary(self, signals: BehaviorSignals) -> Dict[str, Any]:
        """Create human-readable summary of detected signals."""
        summary = {}

        if signals.credit:
            summary["credit"] = {
                "utilization": signals.credit.get("overall_utilization", 0.0),
                "has_interest": signals.credit.get("monthly_interest", 0) > 0
            }

        if signals.income:
            summary["income"] = {
                "frequency": signals.income.get("frequency", "unknown"),
                "stability": signals.income.get("stability", "unknown")
            }

        if signals.subscriptions:
            summary["subscriptions"] = {
                "count": signals.subscriptions.get("recurring_merchant_count", 0),
                "monthly_spend": signals.subscriptions.get("monthly_recurring_spend", 0) / 100
            }

        if signals.savings:
            summary["savings"] = {
                "emergency_fund_months": signals.savings.get("emergency_fund_months", 0.0),
                "monthly_inflow": signals.savings.get("monthly_inflow", 0) / 100
            }

        return summary


class AIRecommendationEngine(RecommendationEngine):
    """
    AI-powered recommendation engine (stub implementation).

    Future implementation will use AI to:
    - Dynamically determine optimal number of education vs offers
    - Use ML models to predict recommendation effectiveness
    - Generate custom recommendations beyond catalog
    - Personalize strategy based on user engagement patterns
    - A/B test different recommendation strategies

    SWAPPING INSTRUCTIONS:
        To swap from StandardRecommendationEngine to AIRecommendationEngine:

        Before:
            engine = StandardRecommendationEngine()

        After:
            engine = AIRecommendationEngine(
                ai_provider="anthropic",
                model="claude-3-5-sonnet-20241022"
            )

        The interface remains identical - no other code changes required.
    """

    def __init__(
        self,
        ai_provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
        content_generator: ContentGenerator = None
    ):
        """
        Initialize AI recommendation engine (stub).

        Args:
            ai_provider: AI provider ("anthropic" or "openai")
            model: Model identifier
            content_generator: ContentGenerator for content retrieval

        Raises:
            NotImplementedError: Always raised - AI engine not yet implemented
        """
        self.ai_provider = ai_provider
        self.model = model
        self.generator = content_generator or TemplateGenerator()

        # TODO: Initialize AI client when implementing
        # if ai_provider == "anthropic":
        #     import anthropic
        #     self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        logger.info(f"AIRecommendationEngine initialized (stub) - provider: {ai_provider}, model: {model}")

        raise NotImplementedError(
            "AIRecommendationEngine not yet implemented. Use StandardRecommendationEngine instead."
        )

    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        window_days: int = 30
    ) -> RecommendationResult:
        """
        Generate recommendations using AI-powered strategy (stub).

        Future implementation will:
        1. Use AI to analyze user's behavioral signals
        2. Dynamically determine optimal recommendation mix
        3. Score and rank all available content/offers with ML
        4. Optionally generate custom recommendations
        5. Learn from user engagement to improve over time

        FUTURE IMPLEMENTATION APPROACH:
            - Query all education content and offers from catalogs
            - Send user context (persona, signals, history) to AI
            - AI returns: recommended content IDs, offer IDs, custom suggestions
            - Fetch full content for recommended items
            - Generate rationales (using AI or template)
            - Return RecommendationResult

        Args:
            db: Async SQLAlchemy database session
            user_id: User identifier
            window_days: Analysis window in days

        Returns:
            RecommendationResult (when implemented)

        Raises:
            NotImplementedError: Always raised - not yet implemented
        """
        raise NotImplementedError("AIRecommendationEngine not yet implemented")
