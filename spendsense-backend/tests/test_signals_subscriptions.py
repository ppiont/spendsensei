"""Test suite for subscription detection

Converted from scripts/test_subscription_detection.py to pytest format.
Tests recurring merchant detection and subscription spend analysis.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.transaction import Transaction
from spendsense.features.subscriptions import detect_subscriptions


@pytest.mark.signals
@pytest.mark.integration
class TestSubscriptionDetection:
    """Test subscription detection from transaction patterns"""

    async def test_detect_recurring_merchants(self, db: AsyncSession, test_checking_account):
        """Test detection of recurring subscription merchants"""
        # Create recurring Netflix transactions (3 months)
        for i in range(3):
            txn = Transaction(
                id=f"test-netflix-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=1599,  # $15.99
                merchant_name="Netflix",
                merchant_entity_id="netflix_inc",
                personal_finance_category_primary="ENTERTAINMENT",
                personal_finance_category_detailed="MOVIES_AND_MUSIC",
                payment_channel="online",
                pending=False
            )
            db.add(txn)

        await db.commit()

        # Get all transactions for account
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Detect subscriptions
        signals = detect_subscriptions(transactions)

        # Verify recurring merchant detected
        assert signals is not None
        assert "recurring_merchant_count" in signals
        assert signals["recurring_merchant_count"] >= 1
        assert "monthly_recurring_spend" in signals
        assert signals["monthly_recurring_spend"] > 0

    async def test_multiple_subscriptions(self, db: AsyncSession, test_checking_account):
        """Test detection of multiple subscription services"""
        # Create multiple recurring subscriptions
        subscriptions = [
            ("netflix_inc", "Netflix", 1599),  # $15.99
            ("spotify_ab", "Spotify", 999),    # $9.99
            ("apple_inc", "Apple", 499),       # $4.99
        ]

        for entity_id, name, amount in subscriptions:
            for i in range(3):  # 3 months of recurring charges
                txn = Transaction(
                    id=f"test-{entity_id}-{i}",
                    account_id=test_checking_account.id,
                    date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                    amount=amount,
                    merchant_name=name,
                    merchant_entity_id=entity_id,
                    personal_finance_category_primary="ENTERTAINMENT",
                    payment_channel="online",
                    pending=False
                )
                db.add(txn)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Detect subscriptions
        signals = detect_subscriptions(transactions)

        # Verify multiple subscriptions detected
        assert signals["recurring_merchant_count"] >= 3
        assert "merchants" in signals
        assert len(signals["merchants"]) >= 3

    async def test_subscription_spend_calculation(self, db: AsyncSession, test_checking_account):
        """Test calculation of monthly subscription spend"""
        # Create known subscription pattern
        amount = 2999  # $29.99
        for i in range(3):
            txn = Transaction(
                id=f"test-sub-spend-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=amount,
                merchant_name="Test Service",
                merchant_entity_id="test_service_inc",
                personal_finance_category_primary="GENERAL_SERVICES",
                payment_channel="online",
                pending=False
            )
            db.add(txn)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Detect subscriptions
        signals = detect_subscriptions(transactions)

        # Verify spend calculated correctly
        assert signals["monthly_recurring_spend"] >= amount

    async def test_no_subscriptions(self, db: AsyncSession, test_checking_account):
        """Test detection when no recurring merchants exist"""
        # Create one-time transactions (no recurring pattern)
        for i in range(5):
            txn = Transaction(
                id=f"test-onetime-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=i),
                amount=5000 + (i * 100),  # Varying amounts
                merchant_name=f"Merchant {i}",
                merchant_entity_id=None,  # No entity ID
                personal_finance_category_primary="GENERAL_MERCHANDISE",
                payment_channel="in_store",
                pending=False
            )
            db.add(txn)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Detect subscriptions
        signals = detect_subscriptions(transactions)

        # Verify no subscriptions detected
        assert signals is None or signals["recurring_merchant_count"] == 0

    async def test_with_fixture_transactions(self, test_transactions):
        """Test using pre-created transaction fixture"""
        signals = detect_subscriptions(test_transactions)

        # test_transactions fixture includes Netflix
        if signals:
            assert "recurring_merchant_count" in signals
            assert "monthly_recurring_spend" in signals
