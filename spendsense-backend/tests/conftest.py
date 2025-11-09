"""Pytest fixtures for SpendSense test suite

This module provides reusable test fixtures for database access,
test data generation, and common test utilities.
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, List
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import AsyncSessionLocal, engine
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from spendsense.models.operator_override import OperatorOverride


# ============================================================================
# Session and Event Loop Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for tests.

    Automatically rolls back changes after each test to ensure isolation.
    This fixture creates a fresh session for each test function.

    Usage:
        async def test_user_creation(db):
            user = User(id="test-123", name="Test", email="test@example.com")
            db.add(user)
            await db.commit()
    """
    async with AsyncSessionLocal() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest_asyncio.fixture
async def clean_db(db: AsyncSession) -> AsyncSession:
    """
    Provide a clean database by removing all test data.

    This fixture clears all tables before yielding the session.
    Use this when you need a completely clean database state.

    Usage:
        async def test_with_clean_db(clean_db):
            # Database is empty at start
            result = await clean_db.execute(select(User))
            assert len(result.scalars().all()) == 0
    """
    # Clean all tables (in dependency order)
    await db.execute(delete(OperatorOverride))
    await db.execute(delete(Transaction))
    await db.execute(delete(Account))
    await db.execute(delete(User))
    await db.commit()

    yield db


# ============================================================================
# Test User Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """
    Create a test user with consent.

    Returns:
        User object with id="test-user-001"

    Usage:
        async def test_user_exists(test_user, db):
            assert test_user.id == "test-user-001"
            assert test_user.consent is True
    """
    user = User(
        id="test-user-001",
        name="Test User",
        email="test@example.com",
        consent=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_no_consent(db: AsyncSession) -> User:
    """
    Create a test user without consent.

    Returns:
        User object with id="test-user-no-consent" and consent=False

    Usage:
        async def test_consent_required(test_user_no_consent):
            assert test_user_no_consent.consent is False
    """
    user = User(
        id="test-user-no-consent",
        name="No Consent User",
        email="noconsent@example.com",
        consent=False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def multiple_test_users(db: AsyncSession) -> List[User]:
    """
    Create multiple test users for batch testing.

    Returns:
        List of 3 User objects

    Usage:
        async def test_multiple_users(multiple_test_users):
            assert len(multiple_test_users) == 3
    """
    users = [
        User(
            id=f"test-user-{i:03d}",
            name=f"Test User {i}",
            email=f"test{i}@example.com",
            consent=True,
            created_at=datetime.now(timezone.utc)
        )
        for i in range(1, 4)
    ]

    for user in users:
        db.add(user)

    await db.commit()

    for user in users:
        await db.refresh(user)

    return users


# ============================================================================
# Test Account Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_checking_account(db: AsyncSession, test_user: User) -> Account:
    """
    Create a test checking account.

    Returns:
        Account object (depository/checking) with $5,000 balance

    Usage:
        async def test_account(test_checking_account):
            assert test_checking_account.subtype == "checking"
            assert test_checking_account.current_balance == 500000  # cents
    """
    account = Account(
        id="test-account-checking",
        user_id=test_user.id,
        type="depository",
        subtype="checking",
        name="Test Checking Account",
        mask="1234",
        current_balance=500000,  # $5,000 in cents
        available_balance=500000,
        currency="USD",
        holder_category="personal"
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_credit_card(db: AsyncSession, test_user: User) -> Account:
    """
    Create a test credit card account with high utilization.

    Returns:
        Account object (credit/credit_card) with 85% utilization

    Usage:
        async def test_credit(test_credit_card):
            assert test_credit_card.subtype == "credit_card"
            assert test_credit_card.current_balance == 8500  # 85% of $10k limit
    """
    account = Account(
        id="test-account-credit",
        user_id=test_user.id,
        type="credit",
        subtype="credit_card",
        name="Test Credit Card",
        mask="5678",
        current_balance=850000,  # $8,500 in cents (85% utilization)
        available_balance=150000,  # $1,500 available
        limit=1000000,  # $10,000 limit
        currency="USD",
        holder_category="personal",
        apr=24.99,
        apr_type="purchase",
        min_payment=25500,  # $255 (3%)
        is_overdue=False,
        last_payment_amount=50000,
        last_payment_date=datetime.now(timezone.utc),
        next_payment_due_date=datetime.now(timezone.utc)
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_accounts(db: AsyncSession, test_user: User) -> List[Account]:
    """
    Create multiple test accounts (checking + credit card).

    Returns:
        List of 2 Account objects

    Usage:
        async def test_multiple_accounts(test_accounts):
            assert len(test_accounts) == 2
            assert test_accounts[0].subtype == "checking"
            assert test_accounts[1].subtype == "credit_card"
    """
    checking = Account(
        id="test-account-multi-checking",
        user_id=test_user.id,
        type="depository",
        subtype="checking",
        name="Test Checking",
        mask="1111",
        current_balance=300000,
        available_balance=300000,
        currency="USD",
        holder_category="personal"
    )

    credit = Account(
        id="test-account-multi-credit",
        user_id=test_user.id,
        type="credit",
        subtype="credit_card",
        name="Test Credit",
        mask="2222",
        current_balance=500000,
        available_balance=500000,
        limit=1000000,
        currency="USD",
        holder_category="personal",
        apr=19.99,
        apr_type="purchase",
        min_payment=15000,
        is_overdue=False
    )

    db.add(checking)
    db.add(credit)
    await db.commit()
    await db.refresh(checking)
    await db.refresh(credit)

    return [checking, credit]


# ============================================================================
# Test Transaction Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_transactions(db: AsyncSession, test_checking_account: Account) -> List[Transaction]:
    """
    Create test transactions for behavioral signal detection.

    Returns:
        List of 5 Transaction objects with various categories

    Usage:
        async def test_signals(test_transactions):
            assert len(test_transactions) == 5
            # Contains income, expenses, subscriptions, etc.
    """
    transactions = [
        # Income transaction
        Transaction(
            id="test-txn-001",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=-300000,  # -$3,000 (credit to account)
            merchant_name="Employer Inc",
            personal_finance_category_primary="INCOME",
            personal_finance_category_detailed="INCOME",
            payment_channel="other",
            pending=False
        ),
        # Recurring subscription (Netflix)
        Transaction(
            id="test-txn-002",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=1599,  # $15.99
            merchant_name="Netflix",
            merchant_entity_id="netflix_inc",
            personal_finance_category_primary="ENTERTAINMENT",
            personal_finance_category_detailed="MOVIES_AND_MUSIC",
            payment_channel="online",
            pending=False
        ),
        # Groceries
        Transaction(
            id="test-txn-003",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=8750,  # $87.50
            merchant_name="Whole Foods",
            merchant_entity_id="whole_foods_market",
            personal_finance_category_primary="FOOD_AND_DRINK",
            personal_finance_category_detailed="GROCERIES",
            payment_channel="in_store",
            pending=False
        ),
        # Gas
        Transaction(
            id="test-txn-004",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=4500,  # $45.00
            merchant_name="Shell",
            merchant_entity_id="shell_oil",
            personal_finance_category_primary="TRANSPORTATION",
            personal_finance_category_detailed="GAS",
            payment_channel="in_store",
            pending=False
        ),
        # Restaurant
        Transaction(
            id="test-txn-005",
            account_id=test_checking_account.id,
            date=datetime.now(timezone.utc),
            amount=3250,  # $32.50
            merchant_name="Local Restaurant",
            personal_finance_category_primary="FOOD_AND_DRINK",
            personal_finance_category_detailed="RESTAURANTS",
            payment_channel="in_store",
            pending=False
        ),
    ]

    for txn in transactions:
        db.add(txn)

    await db.commit()

    for txn in transactions:
        await db.refresh(txn)

    return transactions


# ============================================================================
# Test Data Helpers
# ============================================================================

@pytest.fixture
def sample_user_data() -> dict:
    """
    Provide sample user data for eligibility checking.

    Returns:
        Dict with user financial data (income, accounts, etc.)

    Usage:
        def test_eligibility(sample_user_data):
            assert sample_user_data["annual_income"] == 5000000  # $50k
    """
    return {
        "annual_income": 5000000,  # $50,000 in cents
        "accounts": [
            {"subtype": "checking", "balance": 500000},
            {"subtype": "credit_card", "limit": 1000000, "balance": 300000}
        ]
    }


@pytest.fixture
def sample_partner_offer() -> dict:
    """
    Provide sample partner offer data.

    Returns:
        Dict with partner offer details

    Usage:
        def test_offer(sample_partner_offer):
            assert sample_partner_offer["min_income"] == 3000000  # $30k
    """
    return {
        "id": "offer_test_001",
        "title": "Test Balance Transfer Card",
        "provider": "Test Bank",
        "offer_type": "credit_card",
        "min_income": 3000000,  # $30,000
        "account_type": "credit_card",
        "apr": 15.99,
        "persona_tags": ["high_utilization", "debt_consolidator"]
    }
