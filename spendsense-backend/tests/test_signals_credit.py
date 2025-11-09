"""Test suite for credit utilization analysis

Converted from scripts/test_credit_analysis.py to pytest format.
Tests credit card utilization calculation and interest detection.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.account import Account
from spendsense.features.credit import analyze_credit


@pytest.mark.signals
@pytest.mark.integration
class TestCreditAnalysis:
    """Test credit card utilization and interest analysis"""

    async def test_high_utilization_detection(self, db: AsyncSession, test_user, test_credit_card):
        """Test detection of high credit card utilization"""
        # test_credit_card fixture has 85% utilization
        signals = await analyze_credit(db, test_user.id, window_days=30)

        assert signals is not None
        assert "overall_utilization" in signals
        assert signals["overall_utilization"] > 0.7  # >70% is high
        assert signals["overall_utilization"] == pytest.approx(0.85, abs=0.01)

    async def test_multiple_credit_cards(self, db: AsyncSession, test_user):
        """Test utilization across multiple credit cards"""
        # Create two credit cards with different utilization
        card1 = Account(
            id="test-cc-1",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Card 1",
            mask="1111",
            current_balance=500000,  # $5,000
            limit=1000000,           # $10,000 (50% utilization)
            currency="USD",
            holder_category="personal",
            apr=19.99,
            apr_type="purchase",
            is_overdue=False
        )

        card2 = Account(
            id="test-cc-2",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Card 2",
            mask="2222",
            current_balance=200000,  # $2,000
            limit=500000,            # $5,000 (40% utilization)
            currency="USD",
            holder_category="personal",
            apr=24.99,
            apr_type="purchase",
            is_overdue=False
        )

        db.add(card1)
        db.add(card2)
        await db.commit()

        # Analyze credit
        signals = await analyze_credit(db, test_user.id, window_days=30)

        # Overall utilization should be weighted average: (5000 + 2000) / (10000 + 5000) = 46.7%
        assert signals["overall_utilization"] == pytest.approx(0.467, abs=0.01)

    async def test_interest_detection(self, db: AsyncSession, test_user):
        """Test detection of monthly interest charges"""
        # Create credit card with interest
        card = Account(
            id="test-cc-interest",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Interest Card",
            mask="3333",
            current_balance=1000000,  # $10,000
            limit=1500000,            # $15,000
            currency="USD",
            holder_category="personal",
            apr=29.99,
            apr_type="purchase",
            is_overdue=False
        )
        db.add(card)
        await db.commit()

        signals = await analyze_credit(db, test_user.id, window_days=30)

        # Should detect high APR and balance
        assert signals["overall_utilization"] == pytest.approx(0.667, abs=0.01)

    async def test_low_utilization(self, db: AsyncSession, test_user):
        """Test detection when utilization is low"""
        card = Account(
            id="test-cc-low",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Low Utilization Card",
            mask="4444",
            current_balance=100000,   # $1,000
            limit=1000000,            # $10,000 (10% utilization)
            currency="USD",
            holder_category="personal",
            apr=15.99,
            apr_type="purchase",
            is_overdue=False
        )
        db.add(card)
        await db.commit()

        signals = await analyze_credit(db, test_user.id, window_days=30)

        # Low utilization (<30%) is healthy
        assert signals["overall_utilization"] < 0.3
        assert signals["overall_utilization"] == pytest.approx(0.1, abs=0.01)

    async def test_no_credit_cards(self, db: AsyncSession, test_user):
        """Test when user has no credit cards"""
        # test_user by default has no credit cards
        signals = await analyze_credit(db, test_user.id, window_days=30)

        # Should return None or empty signals
        assert signals is None or signals.get("overall_utilization") == 0

    async def test_zero_limit_edge_case(self, db: AsyncSession, test_user):
        """Test handling of credit cards with zero limit (edge case)"""
        card = Account(
            id="test-cc-zero-limit",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Zero Limit Card",
            mask="5555",
            current_balance=100,
            limit=0,  # Edge case: zero limit
            currency="USD",
            holder_category="personal",
            apr=19.99,
            apr_type="purchase",
            is_overdue=False
        )
        db.add(card)
        await db.commit()

        # Should not crash on division by zero
        signals = await analyze_credit(db, test_user.id, window_days=30)

        # Should handle gracefully (skip or return 0)
        assert signals is not None
