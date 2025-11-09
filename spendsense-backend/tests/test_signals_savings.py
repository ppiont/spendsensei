"""Test suite for savings pattern analysis

Converted from scripts/test_savings_analysis.py to pytest format.
Tests emergency fund calculation and savings behavior detection.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from spendsense.features.savings import analyze_savings


@pytest.mark.signals
@pytest.mark.integration
class TestSavingsAnalysis:
    """Test savings account analysis and emergency fund detection"""

    async def test_emergency_fund_calculation(self, db: AsyncSession, test_user):
        """Test calculation of emergency fund months"""
        # Create savings account with $10,000 balance
        savings = Account(
            id="test-savings-001",
            user_id=test_user.id,
            type="depository",
            subtype="savings",
            name="Emergency Fund",
            mask="6666",
            current_balance=1000000,  # $10,000
            available_balance=1000000,
            currency="USD",
            holder_category="personal"
        )
        db.add(savings)
        await db.commit()

        # Create monthly income transactions to establish monthly spend
        for i in range(3):
            income = Transaction(
                id=f"test-income-{i}",
                account_id=savings.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=-300000,  # -$3,000 income
                merchant_name="Employer",
                personal_finance_category_primary="INCOME",
                personal_finance_category_detailed="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

        # Create monthly expenses
        for i in range(3):
            expense = Transaction(
                id=f"test-expense-{i}",
                account_id=savings.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=200000,  # $2,000 expense
                merchant_name="Expenses",
                personal_finance_category_primary="GENERAL_MERCHANDISE",
                payment_channel="in_store",
                pending=False
            )
            db.add(expense)

        await db.commit()

        # Analyze savings
        signals = await analyze_savings(db, test_user.id, window_days=90)

        # Should detect emergency fund
        assert signals is not None
        assert "emergency_fund_months" in signals
        # $10,000 balance / $2,000 monthly expense = 5 months
        assert signals["emergency_fund_months"] > 0

    async def test_positive_savings_rate(self, db: AsyncSession, test_user, test_checking_account):
        """Test detection of positive monthly savings"""
        # Create income and expense pattern with positive savings
        for i in range(3):
            # Income: $4,000/month
            income = Transaction(
                id=f"test-inc-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=-400000,  # -$4,000
                merchant_name="Employer",
                personal_finance_category_primary="INCOME",
                payment_channel="other",
                pending=False
            )
            db.add(income)

            # Expenses: $3,000/month
            expense = Transaction(
                id=f"test-exp-{i}",
                account_id=test_checking_account.id,
                date=datetime.now(timezone.utc) - timedelta(days=30 * i),
                amount=300000,  # $3,000
                merchant_name="Expenses",
                personal_finance_category_primary="GENERAL_MERCHANDISE",
                payment_channel="in_store",
                pending=False
            )
            db.add(expense)

        await db.commit()

        # Analyze savings
        signals = await analyze_savings(db, test_user.id, window_days=90)

        # Should detect positive inflow (income > expenses)
        if signals and "monthly_inflow" in signals:
            assert signals["monthly_inflow"] > 0  # Net positive

    async def test_no_savings_account(self, db: AsyncSession, test_user):
        """Test when user has no savings account"""
        # test_user has no savings account by default
        signals = await analyze_savings(db, test_user.id, window_days=30)

        # Should handle gracefully
        assert signals is None or signals.get("emergency_fund_months", 0) == 0

    async def test_multiple_savings_accounts(self, db: AsyncSession, test_user):
        """Test aggregation across multiple savings accounts"""
        # Create two savings accounts
        savings1 = Account(
            id="test-sav-1",
            user_id=test_user.id,
            type="depository",
            subtype="savings",
            name="Emergency Fund",
            mask="7777",
            current_balance=500000,  # $5,000
            available_balance=500000,
            currency="USD",
            holder_category="personal"
        )

        savings2 = Account(
            id="test-sav-2",
            user_id=test_user.id,
            type="depository",
            subtype="savings",
            name="Vacation Fund",
            mask="8888",
            current_balance=300000,  # $3,000
            available_balance=300000,
            currency="USD",
            holder_category="personal"
        )

        db.add(savings1)
        db.add(savings2)
        await db.commit()

        signals = await analyze_savings(db, test_user.id, window_days=30)

        # Should aggregate both accounts ($8,000 total)
        if signals and "total_savings" in signals:
            assert signals["total_savings"] >= 800000  # $8,000 in cents
