"""Test suite for database models and Pydantic schemas

Converted from scripts/test_schemas.py to pytest format.
Tests model validation and schema serialization.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.schemas.insight import (
    EducationItemResponse,
    PartnerOfferResponse,
    RationaleResponse,
    RecommendationResponse
)


@pytest.mark.unit
class TestUserModel:
    """Test User model validation"""

    def test_user_creation(self):
        """Test creating a valid user"""
        user = User(
            id="test-123",
            name="Test User",
            email="test@example.com",
            consent=True,
            created_at=datetime.now(timezone.utc)
        )

        assert user.id == "test-123"
        assert user.name == "Test User"
        assert user.consent is True

    def test_user_consent_default(self):
        """Test that consent defaults to False"""
        user = User(
            id="test-456",
            name="Test",
            email="test@example.com",
            created_at=datetime.now(timezone.utc)
        )

        # Consent should default to False
        assert user.consent is False


@pytest.mark.unit
class TestAccountModel:
    """Test Account model validation"""

    def test_checking_account_creation(self):
        """Test creating a checking account"""
        account = Account(
            id="acc-123",
            user_id="user-123",
            type="depository",
            subtype="checking",
            name="Checking",
            mask="1234",
            current_balance=10000,
            available_balance=10000,
            currency="USD",
            holder_category="personal"
        )

        assert account.type == "depository"
        assert account.subtype == "checking"
        assert account.current_balance == 10000

    def test_credit_card_with_apr_type(self):
        """Test credit card with apr_type field"""
        account = Account(
            id="acc-456",
            user_id="user-123",
            type="credit",
            subtype="credit_card",
            name="Credit Card",
            mask="5678",
            current_balance=500000,
            limit=1000000,
            currency="USD",
            holder_category="personal",
            apr=19.99,
            apr_type="purchase",  # New field from Phase 1
            is_overdue=False
        )

        assert account.apr_type == "purchase"
        assert account.apr == 19.99
        assert account.limit == 1000000


@pytest.mark.unit
class TestPydanticSchemas:
    """Test Pydantic schema validation and serialization"""

    def test_education_item_response(self):
        """Test EducationItemResponse schema"""
        item = EducationItemResponse(
            id="edu-123",
            title="Test Education",
            summary="Test summary",
            body="Test body",
            cta="Learn more",
            source="test",
            relevance_score=5
        )

        assert item.id == "edu-123"
        assert 1 <= item.relevance_score <= 5

    def test_relevance_score_validation(self):
        """Test that relevance_score must be 1-5"""
        # Valid score (should pass)
        item = EducationItemResponse(
            id="edu-456",
            title="Test",
            summary="Summary",
            body="Body",
            cta="CTA",
            source="test",
            relevance_score=3
        )
        assert item.relevance_score == 3

        # Invalid score (should fail)
        with pytest.raises(ValidationError):
            EducationItemResponse(
                id="edu-789",
                title="Test",
                summary="Summary",
                body="Body",
                cta="CTA",
                source="test",
                relevance_score=6  # Out of range
            )

    def test_rationale_response(self):
        """Test RationaleResponse schema"""
        rationale = RationaleResponse(
            persona_type="high_utilization",
            confidence=0.92,
            explanation="Test explanation",
            key_signals=["signal1", "signal2"]
        )

        assert rationale.persona_type == "high_utilization"
        assert 0.0 <= rationale.confidence <= 1.0
        assert len(rationale.key_signals) == 2

    def test_confidence_validation(self):
        """Test that confidence must be 0.0-1.0"""
        # Valid confidence
        rationale = RationaleResponse(
            persona_type="balanced",
            confidence=0.75,
            explanation="Test",
            key_signals=["sig1"]
        )
        assert rationale.confidence == 0.75

        # Invalid confidence (should fail)
        with pytest.raises(ValidationError):
            RationaleResponse(
                persona_type="balanced",
                confidence=1.5,  # Out of range
                explanation="Test",
                key_signals=["sig1"]
            )

    def test_partner_offer_response(self):
        """Test PartnerOfferResponse schema"""
        offer = PartnerOfferResponse(
            id="offer-123",
            title="Test Offer",
            provider="Test Bank",
            offer_type="credit_card",
            summary="Test summary",
            benefits=["Benefit 1", "Benefit 2"],
            eligibility_explanation="Test eligibility",
            cta="Apply now",
            cta_url="https://example.com",
            disclaimer="Test disclaimer",
            relevance_score=4,
            eligibility_met=True
        )

        assert offer.id == "offer-123"
        assert offer.eligibility_met is True
        assert 1 <= offer.relevance_score <= 5
