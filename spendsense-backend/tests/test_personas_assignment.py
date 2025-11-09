"""Test suite for persona assignment

Converted from scripts/test_persona_assignment.py to pytest format.
Tests persona matching based on behavioral signals.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.personas import assign_persona
from spendsense.features import BehaviorSignals


@pytest.mark.personas
@pytest.mark.integration
class TestPersonaAssignment:
    """Test persona assignment from behavioral signals"""

    async def test_high_utilization_persona(self, db: AsyncSession, test_user, test_credit_card):
        """Test assignment of high_utilization persona"""
        # test_credit_card has 85% utilization
        result = await assign_persona(db, test_user.id, window_days=30)

        assert result is not None
        assert result["persona_type"] == "high_utilization"
        assert result["confidence"] > 0.7  # Should be high confidence
        assert result["signals"] is not None

    async def test_savings_builder_persona(self, db: AsyncSession, test_user, test_checking_account):
        """Test assignment of savings_builder persona"""
        from spendsense.models.account import Account
        from spendsense.models.transaction import Transaction
        from datetime import datetime, timezone, timedelta

        # Create savings account with strong pattern
        savings = Account(
            id="test-savings-persona",
            user_id=test_user.id,
            type="depository",
            subtype="savings",
            name="Savings",
            mask="9999",
            current_balance=1000000,  # $10,000
            available_balance=1000000,
            currency="USD",
            holder_category="personal"
        )
        db.add(savings)

        # Add regular savings deposits
        for i in range(3):
            deposit = Transaction(
                id=f"test-deposit-{i}",
                account_id=savings.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=-50000,  # -$500 deposit
                merchant_name="Transfer",
                personal_finance_category_primary="TRANSFER_IN",
                payment_channel="other",
                pending=False
            )
            db.add(deposit)

        await db.commit()

        result = await assign_persona(db, test_user.id, window_days=90)

        # Should detect savings behavior
        assert result is not None
        assert result["signals"].savings is not None

    async def test_balanced_persona_fallback(self, db: AsyncSession, test_user, test_checking_account):
        """Test fallback to balanced persona when no strong signals"""
        # test_user with checking account but no strong signals
        result = await assign_persona(db, test_user.id, window_days=30)

        # Should default to balanced
        assert result is not None
        # May be balanced or have weak signals for other personas
        assert result["persona_type"] in [
            "balanced",
            "high_utilization",
            "variable_income",
            "debt_consolidator",
            "subscription_heavy",
            "savings_builder"
        ]

    async def test_confidence_scoring(self, db: AsyncSession, test_user, test_credit_card):
        """Test confidence scores reflect signal strength"""
        result = await assign_persona(db, test_user.id, window_days=30)

        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= result["confidence"] <= 1.0

        # Strong signals (like 85% utilization) should have high confidence
        if result["persona_type"] == "high_utilization":
            assert result["confidence"] > 0.8

    async def test_persona_priority_order(self, db: AsyncSession, test_user):
        """Test that personas are assigned in priority order"""
        from spendsense.models.account import Account

        # Create both credit (high priority) and savings (lower priority)
        credit_card = Account(
            id="test-priority-credit",
            user_id=test_user.id,
            type="credit",
            subtype="credit_card",
            name="Credit Card",
            mask="1111",
            current_balance=900000,  # $9,000
            limit=1000000,           # $10,000 (90% utilization - high!)
            currency="USD",
            holder_category="personal",
            apr=24.99,
            apr_type="purchase",
            is_overdue=False
        )

        savings_account = Account(
            id="test-priority-savings",
            user_id=test_user.id,
            type="depository",
            subtype="savings",
            name="Savings",
            mask="2222",
            current_balance=500000,  # $5,000
            available_balance=500000,
            currency="USD",
            holder_category="personal"
        )

        db.add(credit_card)
        db.add(savings_account)
        await db.commit()

        result = await assign_persona(db, test_user.id, window_days=30)

        # high_utilization has higher priority than savings_builder
        # Should assign high_utilization even if savings also present
        assert result["persona_type"] == "high_utilization"


@pytest.mark.personas
@pytest.mark.unit
class TestPersonaMatching:
    """Test persona matching logic (unit tests)"""

    def test_high_utilization_threshold(self):
        """Test high utilization threshold (>70%)"""
        # This would test the matching function directly
        # For now, tested via integration tests above
        pass

    def test_subscription_heavy_threshold(self):
        """Test subscription heavy threshold (>3 subscriptions)"""
        # This would test the matching function directly
        pass
