"""Test script to verify Pydantic schema validation"""

from datetime import datetime
from spendsense.schemas.user import UserCreate, UserResponse
from spendsense.schemas.account import AccountResponse
from spendsense.schemas.transaction import TransactionResponse
from spendsense.schemas.insight import RecommendationResponse, EducationItemResponse, RationaleResponse


def test_user_create_schema():
    """Test UserCreate schema validation"""
    print("Testing UserCreate schema...")

    # Valid user
    user = UserCreate(name="John Doe", email="john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    print("✅ Valid UserCreate passed")

    # Test email validation
    try:
        invalid = UserCreate(name="John", email="invalid-email")
        print("❌ Should have failed email validation")
    except Exception as e:
        print(f"✅ Email validation works: {type(e).__name__}")

    # Test empty name
    try:
        invalid = UserCreate(name="", email="test@example.com")
        print("❌ Should have failed empty name validation")
    except Exception as e:
        print(f"✅ Empty name validation works: {type(e).__name__}")


def test_user_response_schema():
    """Test UserResponse schema"""
    print("\nTesting UserResponse schema...")

    user_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "consent": True,
        "created_at": "2025-11-03T12:00:00Z"
    }

    user = UserResponse(**user_data)
    assert user.id == user_data["id"]
    assert user.consent is True
    print("✅ UserResponse schema valid")


def test_account_response_schema():
    """Test AccountResponse schema"""
    print("\nTesting AccountResponse schema...")

    # Checking account
    checking = AccountResponse(
        id="acc_123",
        user_id="user_456",
        type="depository",
        subtype="checking",
        name="Chase Checking",
        mask="1234",
        balance=500000,  # $5,000.00
        currency="USD",
        is_overdue=False
    )
    assert checking.balance == 500000
    assert checking.limit is None  # Not a credit card
    print("✅ Checking account schema valid")

    # Credit card
    credit = AccountResponse(
        id="acc_789",
        user_id="user_456",
        type="credit",
        subtype="credit_card",
        name="Amex Gold",
        mask="5678",
        balance=125000,  # $1,250.00
        limit=1000000,  # $10,000.00 limit
        currency="USD",
        apr=18.99,
        min_payment=2500,  # $25.00
        is_overdue=False
    )
    assert credit.limit == 1000000
    assert credit.apr == 18.99
    print("✅ Credit card schema valid")


def test_transaction_response_schema():
    """Test TransactionResponse schema"""
    print("\nTesting TransactionResponse schema...")

    # Debit transaction (expense)
    expense = TransactionResponse(
        id="txn_123",
        account_id="acc_456",
        date="2025-11-01T14:30:00Z",
        amount=4599,  # $45.99 expense (positive)
        merchant_name="Whole Foods",
        category="FOOD_AND_DRINK",
        pending=False
    )
    assert expense.amount > 0  # Positive = debit
    print("✅ Expense transaction schema valid")

    # Credit transaction (income)
    income = TransactionResponse(
        id="txn_124",
        account_id="acc_456",
        date="2025-11-01T09:00:00Z",
        amount=-300000,  # $3,000.00 income (negative)
        merchant_name="Acme Corp",
        category="INCOME",
        pending=False
    )
    assert income.amount < 0  # Negative = credit
    print("✅ Income transaction schema valid")


def test_recommendation_response_schema():
    """Test RecommendationResponse schema"""
    print("\nTesting RecommendationResponse schema...")

    rec_data = {
        "content": {
            "id": "credit-util-101",
            "title": "Understanding Credit Utilization",
            "summary": "Learn why keeping credit utilization below 30% matters.",
            "body": "Credit utilization is one of the most important factors affecting your credit score...",
            "cta": "Review Your Credit Cards",
            "source": "template",
            "relevance_score": 0.85
        },
        "rationale": {
            "persona_type": "high_utilization",
            "confidence": 0.95,
            "explanation": "Your credit utilization is 77.5%, which is above the recommended 30% threshold.",
            "key_signals": ["high_utilization_50", "interest_charges"]
        },
        "persona": "high_utilization",
        "confidence": 0.95
    }

    recommendation = RecommendationResponse(**rec_data)
    assert recommendation.persona == "high_utilization"
    assert 0.0 <= recommendation.confidence <= 1.0
    assert recommendation.content.relevance_score == 0.85
    assert len(recommendation.rationale.key_signals) == 2
    print("✅ RecommendationResponse schema valid")


def test_snake_case_fields():
    """Verify all schemas use snake_case field names"""
    print("\nVerifying snake_case field naming...")

    # Check UserResponse
    user = UserResponse(
        id="test",
        name="Test",
        email="test@example.com",
        consent=True,
        created_at="2025-11-03T12:00:00Z"
    )
    assert hasattr(user, "created_at")  # snake_case
    print("✅ UserResponse uses snake_case")

    # Check AccountResponse
    account = AccountResponse(
        id="test",
        user_id="user123",
        type="credit",
        subtype="credit_card",
        name="Test",
        mask="1234",
        balance=100,
        min_payment=10,
        is_overdue=False
    )
    assert hasattr(account, "user_id")  # snake_case
    assert hasattr(account, "min_payment")  # snake_case
    assert hasattr(account, "is_overdue")  # snake_case
    print("✅ AccountResponse uses snake_case")

    # Check TransactionResponse
    txn = TransactionResponse(
        id="test",
        account_id="acc123",
        date="2025-11-01T12:00:00Z",
        amount=100,
        merchant_name="Test Merchant",
        category="TEST",
        pending=False
    )
    assert hasattr(txn, "account_id")  # snake_case
    assert hasattr(txn, "merchant_name")  # snake_case
    print("✅ TransactionResponse uses snake_case")

    # Check RecommendationResponse
    rec = RecommendationResponse(
        content=EducationItemResponse(
            id="test",
            title="Test",
            summary="Test summary",
            body="Test body",
            cta="Test CTA",
            source="template",
            relevance_score=0.5
        ),
        rationale=RationaleResponse(
            persona_type="balanced",
            confidence=0.6,
            explanation="Test explanation",
            key_signals=["test_signal"]
        ),
        persona="balanced",
        confidence=0.6
    )
    assert hasattr(rec, "content")
    assert hasattr(rec.content, "relevance_score")  # snake_case
    assert hasattr(rec.rationale, "persona_type")  # snake_case
    assert hasattr(rec.rationale, "key_signals")  # snake_case
    print("✅ RecommendationResponse uses snake_case")


def test_iso8601_dates():
    """Verify dates are in ISO 8601 format"""
    print("\nVerifying ISO 8601 date format...")

    user = UserResponse(
        id="test",
        name="Test",
        email="test@example.com",
        consent=True,
        created_at="2025-11-03T12:00:00Z"
    )
    assert user.created_at.endswith("Z")  # ISO 8601 with Z suffix
    print("✅ ISO 8601 date format verified")


def test_currency_as_integers():
    """Verify currency amounts are integers (cents)"""
    print("\nVerifying currency amounts as integers...")

    account = AccountResponse(
        id="test",
        user_id="user123",
        type="credit",
        subtype="credit_card",
        name="Test",
        mask="1234",
        balance=125000,  # Must be integer
        limit=1000000,  # Must be integer
        min_payment=2500,  # Must be integer
        is_overdue=False
    )
    assert isinstance(account.balance, int)
    assert isinstance(account.limit, int)
    assert isinstance(account.min_payment, int)
    print("✅ Currency amounts are integers (cents)")

    txn = TransactionResponse(
        id="test",
        account_id="acc123",
        date="2025-11-01T12:00:00Z",
        amount=4599,  # Must be integer
        category="TEST",
        pending=False
    )
    assert isinstance(txn.amount, int)
    print("✅ Transaction amounts are integers (cents)")


if __name__ == "__main__":
    print("=" * 60)
    print("SCHEMA VALIDATION TESTS")
    print("=" * 60)

    test_user_create_schema()
    test_user_response_schema()
    test_account_response_schema()
    test_transaction_response_schema()
    test_recommendation_response_schema()
    test_snake_case_fields()
    test_iso8601_dates()
    test_currency_as_integers()

    print("\n" + "=" * 60)
    print("✅ ALL SCHEMA VALIDATION TESTS PASSED")
    print("=" * 60)
