"""Test suite for recommendation engine

Converted from scripts/test_recommendation_engine.py to pytest format.
Tests end-to-end recommendation generation.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.recommend.engine import StandardRecommendationEngine


@pytest.mark.recommendations
@pytest.mark.integration
class TestRecommendationEngine:
    """Test StandardRecommendationEngine end-to-end"""

    async def test_generate_recommendations(self, db: AsyncSession, test_user, test_credit_card):
        """Test basic recommendation generation"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Should return complete result
        assert result is not None
        assert result.persona_type is not None
        assert result.confidence > 0.0
        assert len(result.education_recommendations) > 0
        assert result.signals_summary is not None

    async def test_education_recommendations_count(self, db: AsyncSession, test_user, test_credit_card):
        """Test that 3 education items are returned"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Should return exactly 3 education items
        assert len(result.education_recommendations) == 3

    async def test_offer_recommendations(self, db: AsyncSession, test_user, test_credit_card):
        """Test partner offer generation with eligibility"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Should return 0-3 offers
        assert len(result.offer_recommendations) <= 3

        # All offers should meet eligibility
        for offer_rec in result.offer_recommendations:
            assert offer_rec.offer.eligibility_met is True

    async def test_rationales_present(self, db: AsyncSession, test_user, test_credit_card):
        """Test that all recommendations have rationales"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Every education item should have rationale
        for rec in result.education_recommendations:
            assert rec.rationale is not None
            assert rec.rationale.explanation
            assert len(rec.rationale.key_signals) > 0

        # Every offer should have rationale
        for rec in result.offer_recommendations:
            assert rec.rationale is not None

    async def test_relevance_scoring(self, db: AsyncSession, test_user, test_credit_card):
        """Test that recommendations have 1-5 relevance scores"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # All education items should have 1-5 score
        for rec in result.education_recommendations:
            assert 1 <= rec.content.relevance_score <= 5

        # All offers should have 1-5 score
        for rec in result.offer_recommendations:
            assert 1 <= rec.offer.relevance_score <= 5

    async def test_multi_window_analysis(self, db: AsyncSession, test_user, test_credit_card):
        """Test recommendations with different time windows"""
        engine = StandardRecommendationEngine()

        # Generate for 30-day window
        result_30d = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Generate for 180-day window
        result_180d = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=180
        )

        # Both should return results
        assert result_30d is not None
        assert result_180d is not None

        # Personas might differ based on window
        # (short-term vs long-term behavior)

    async def test_signals_summary_structure(self, db: AsyncSession, test_user, test_credit_card):
        """Test signals summary is properly formatted"""
        engine = StandardRecommendationEngine()

        result = await engine.generate_recommendations(
            db=db,
            user_id=test_user.id,
            window_days=30
        )

        # Should have signals summary
        assert result.signals_summary is not None
        assert isinstance(result.signals_summary, dict)

        # Should include credit signals for test_credit_card
        if "credit" in result.signals_summary:
            assert "utilization" in result.signals_summary["credit"]


@pytest.mark.recommendations
@pytest.mark.unit
class TestRecommendationEngineValidation:
    """Test recommendation engine input validation"""

    async def test_invalid_window_days(self, db: AsyncSession, test_user):
        """Test that invalid window_days raises error"""
        engine = StandardRecommendationEngine()

        # window_days must be 30 or 180
        with pytest.raises(ValueError, match="window_days must be 30 or 180"):
            await engine.generate_recommendations(
                db=db,
                user_id=test_user.id,
                window_days=45  # Invalid
            )

    async def test_missing_user_id(self, db: AsyncSession):
        """Test that missing user_id raises error"""
        engine = StandardRecommendationEngine()

        with pytest.raises(ValueError, match="user_id is required"):
            await engine.generate_recommendations(
                db=db,
                user_id="",
                window_days=30
            )
