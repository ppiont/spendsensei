"""Test suite for income stability analysis

Converted from scripts/test_income_analysis.py to pytest format.
Tests income frequency detection and stability calculation.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.transaction import Transaction
from spendsense.features.income import analyze_income


@pytest.mark.signals
@pytest.mark.integration
class TestIncomeAnalysis:
    """Test income pattern detection and stability analysis"""

    async def test_biweekly_income_detection(self, db: AsyncSession, test_checking_account):
        """Test detection of biweekly income pattern"""
        # Create biweekly income transactions (every 14 days)
        for i in range(6):  # 3 months of biweekly payments
            income = Transaction(
                id=f"test-biweekly-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=14 * i),
                amount=-250000,  # -$2,500
                merchant_name="Employer Inc",
                personal_finance_category_primary="INCOME",
                personal_finance_category_detailed="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Analyze income
        signals = await analyze_income(transactions, window_days=90)

        # Should detect biweekly pattern
        assert signals is not None
        assert "frequency" in signals
        assert signals["frequency"] in ["biweekly", "regular"]

    async def test_monthly_income_detection(self, db: AsyncSession, test_checking_account):
        """Test detection of monthly income pattern"""
        # Create monthly income transactions
        for i in range(3):
            income = Transaction(
                id=f"test-monthly-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=-400000,  # -$4,000
                merchant_name="Employer Corp",
                personal_finance_category_primary="INCOME",
                personal_finance_category_detailed="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Analyze income
        signals = await analyze_income(transactions, window_days=90)

        # Should detect monthly pattern
        assert signals is not None
        assert "frequency" in signals
        assert signals["frequency"] in ["monthly", "regular"]

    async def test_irregular_income_detection(self, db: AsyncSession, test_checking_account):
        """Test detection of irregular/variable income"""
        # Create irregular income pattern
        irregular_days = [5, 18, 45, 67, 82]  # Irregular intervals
        irregular_amounts = [300000, 450000, 200000, 550000, 280000]  # Variable amounts

        for i, (days, amount) in enumerate(zip(irregular_days, irregular_amounts)):
            income = Transaction(
                id=f"test-irregular-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=days),
                amount=-amount,
                merchant_name="Freelance Client",
                personal_finance_category_primary="INCOME",
                personal_finance_category_detailed="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Analyze income
        signals = await analyze_income(transactions, window_days=90)

        # Should detect irregular pattern
        assert signals is not None
        assert "frequency" in signals
        assert signals["frequency"] in ["irregular", "variable"]
        assert "stability" in signals
        assert signals["stability"] in ["low", "variable"]

    async def test_stable_income(self, db: AsyncSession, test_checking_account):
        """Test detection of stable, consistent income"""
        # Create very consistent income
        for i in range(6):
            income = Transaction(
                id=f"test-stable-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=14 * i),
                amount=-300000,  # Exactly -$3,000 every time
                merchant_name="Employer LLC",
                personal_finance_category_primary="INCOME",
                personal_finance_category_detailed="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Analyze income
        signals = await analyze_income(transactions, window_days=90)

        # Should detect high stability
        assert signals is not None
        assert "stability" in signals
        assert signals["stability"] in ["high", "stable"]

    async def test_no_income_transactions(self, db: AsyncSession, test_checking_account):
        """Test when no income transactions exist"""
        # Create only expense transactions
        expense = Transaction(
            id="test-expense-only",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=5000,  # Positive amount = expense
            merchant_name="Store",
            personal_finance_category_primary="GENERAL_MERCHANDISE",
            payment_channel="in_store",
            pending=False
        )
        db.add(expense)
        await db.commit()

        # Get transactions
        from sqlalchemy import select
        result = await db.execute(
            select(Transaction).where(Transaction.account_id == test_checking_account.id)
        )
        transactions = result.scalars().all()

        # Analyze income
        signals = await analyze_income(transactions, window_days=30)

        # Should return None or indicate no income
        assert signals is None or signals.get("frequency") == "none"

    async def test_with_fixture_transactions(self, test_transactions):
        """Test using pre-created transaction fixture"""
        # test_transactions includes income
        signals = await analyze_income(test_transactions, window_days=30)

        # Should detect some income pattern
        if signals:
            assert "frequency" in signals
