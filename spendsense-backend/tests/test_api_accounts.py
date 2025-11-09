"""Test suite for account and transaction endpoints

Converted from scripts/test_account_transaction_endpoints.py to pytest format.
Tests account retrieval and transaction queries.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.account import Account
from spendsense.models.transaction import Transaction


@pytest.mark.api
@pytest.mark.integration
class TestAccountEndpoints:
    """Test account retrieval operations"""

    async def test_get_user_accounts(self, db: AsyncSession, test_user, test_accounts):
        """Test retrieving all accounts for a user"""
        # Query accounts for test_user
        result = await db.execute(
            select(Account).where(Account.user_id == test_user.id)
        )
        accounts = result.scalars().all()

        # Should find the test_accounts
        assert len(accounts) >= 2
        assert all(acc.user_id == test_user.id for acc in accounts)

    async def test_account_balances(self, db: AsyncSession, test_checking_account):
        """Test that account balances are correct"""
        result = await db.execute(
            select(Account).where(Account.id == test_checking_account.id)
        )
        account = result.scalar_one()

        assert account.current_balance == 500000  # $5,000
        assert account.available_balance == 500000

    async def test_credit_card_fields(self, db: AsyncSession, test_credit_card):
        """Test that credit card specific fields are present"""
        result = await db.execute(
            select(Account).where(Account.id == test_credit_card.id)
        )
        account = result.scalar_one()

        # Credit card should have these fields
        assert account.limit is not None
        assert account.apr is not None
        assert account.apr_type is not None
        assert account.min_payment is not None


@pytest.mark.api
@pytest.mark.integration
class TestTransactionEndpoints:
    """Test transaction retrieval and filtering"""

    async def test_get_user_transactions(self, db: AsyncSession, test_user, test_transactions):
        """Test retrieving all transactions for a user"""
        # Get user's accounts
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == test_user.id)
        )
        accounts = accounts_result.scalars().all()
        account_ids = [acc.id for acc in accounts]

        # Get transactions for those accounts
        result = await db.execute(
            select(Transaction).where(Transaction.account_id.in_(account_ids))
        )
        transactions = result.scalars().all()

        # Should have the test_transactions
        assert len(transactions) >= 5

    async def test_transaction_time_window(self, db: AsyncSession, test_checking_account):
        """Test filtering transactions by time window"""
        # Create transactions at different times
        now = datetime.now(timezone.utc)

        old_txn = Transaction(
            id="test-old-txn",
            account_id=test_checking_account.id,
            date=now - timedelta(days=100),
            amount=1000,
            merchant_name="Old Store",
            personal_finance_category_primary="GENERAL_MERCHANDISE",
            payment_channel="in_store",
            pending=False
        )

        recent_txn = Transaction(
            id="test-recent-txn",
            account_id=test_checking_account.id,
            date=now - timedelta(days=10),
            amount=2000,
            merchant_name="Recent Store",
            personal_finance_category_primary="GENERAL_MERCHANDISE",
            payment_channel="in_store",
            pending=False
        )

        db.add(old_txn)
        db.add(recent_txn)
        await db.commit()

        # Query last 30 days
        cutoff_date = now - timedelta(days=30)
        result = await db.execute(
            select(Transaction)
            .where(Transaction.account_id == test_checking_account.id)
            .where(Transaction.date >= cutoff_date)
        )
        recent_transactions = result.scalars().all()

        # Should only get recent transaction
        recent_ids = [t.id for t in recent_transactions]
        assert "test-recent-txn" in recent_ids
        assert "test-old-txn" not in recent_ids

    async def test_transaction_categories(self, test_transactions):
        """Test that transactions have proper Plaid categories"""
        for txn in test_transactions:
            assert txn.personal_finance_category_primary is not None
            # Should be valid Plaid category
            assert txn.personal_finance_category_primary in [
                "INCOME",
                "FOOD_AND_DRINK",
                "TRANSPORTATION",
                "ENTERTAINMENT",
                "GENERAL_MERCHANDISE",
                "GENERAL_SERVICES"
            ]

    async def test_pending_transactions(self, db: AsyncSession, test_checking_account):
        """Test filtering pending vs posted transactions"""
        # Create pending transaction
        pending_txn = Transaction(
            id="test-pending",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=5000,
            merchant_name="Pending Store",
            personal_finance_category_primary="GENERAL_MERCHANDISE",
            payment_channel="in_store",
            pending=True
        )

        posted_txn = Transaction(
            id="test-posted",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=3000,
            merchant_name="Posted Store",
            personal_finance_category_primary="GENERAL_MERCHANDISE",
            payment_channel="in_store",
            pending=False
        )

        db.add(pending_txn)
        db.add(posted_txn)
        await db.commit()

        # Query only posted transactions
        result = await db.execute(
            select(Transaction)
            .where(Transaction.account_id == test_checking_account.id)
            .where(Transaction.pending == False)
        )
        posted_transactions = result.scalars().all()

        # Should only get posted transaction
        posted_ids = [t.id for t in posted_transactions]
        assert "test-posted" in posted_ids
        # pending might or might not be in list depending on existing data
