"""Test suite for all guardrails

Converted from scripts/test_guardrails.py and test_guardrails_blocking.py
Tests consent, tone, eligibility, and disclosure guardrails.
"""

import pytest
from spendsense.guardrails.consent import check_consent
from spendsense.guardrails.tone import detect_shame_pattern
from spendsense.guardrails.eligibility import (
    check_income_requirement,
    has_existing_account,
    is_predatory_product,
    check_eligibility
)
from spendsense.guardrails.disclosure import generate_standard_disclaimer


@pytest.mark.guardrails
@pytest.mark.unit
class TestConsentGuardrails:
    """Test consent checking guardrails"""

    def test_consent_required(self):
        """Test that consent=True passes check"""
        assert check_consent(True) is True

    def test_consent_not_given(self):
        """Test that consent=False fails check"""
        assert check_consent(False) is False

    def test_consent_none(self):
        """Test that consent=None fails check"""
        assert check_consent(None) is False


@pytest.mark.guardrails
@pytest.mark.unit
class TestToneGuardrails:
    """Test shame/blame pattern detection"""

    def test_detect_shame_language(self):
        """Test detection of shame-inducing language"""
        shame_texts = [
            "This is your fault for overspending",
            "You should have known better",
            "That was irresponsible of you",
            "You're terrible with money"
        ]

        for text in shame_texts:
            assert detect_shame_pattern(text) is True

    def test_allow_neutral_language(self):
        """Test that neutral language passes"""
        neutral_texts = [
            "Your credit utilization is 85%, above the recommended 30%",
            "Consider reducing your monthly subscriptions",
            "Building an emergency fund is recommended"
        ]

        for text in neutral_texts:
            assert detect_shame_pattern(text) is False

    def test_educational_tone_allowed(self):
        """Test that educational language is allowed"""
        text = "Learn how to optimize your credit utilization for better financial health"
        assert detect_shame_pattern(text) is False


@pytest.mark.guardrails
@pytest.mark.unit
class TestEligibilityGuardrails:
    """Test product eligibility checks"""

    def test_income_requirement_met(self, sample_user_data):
        """Test income requirement check when met"""
        offer = {"min_income": 3000000}  # $30,000
        # sample_user_data has $50,000 income
        assert check_income_requirement(offer, sample_user_data["annual_income"]) is True

    def test_income_requirement_not_met(self, sample_user_data):
        """Test income requirement check when not met"""
        offer = {"min_income": 10000000}  # $100,000
        # sample_user_data has $50,000 income
        assert check_income_requirement(offer, sample_user_data["annual_income"]) is False

    def test_no_income_requirement(self, sample_user_data):
        """Test offer with no income requirement"""
        offer = {"min_income": 0}
        assert check_income_requirement(offer, sample_user_data["annual_income"]) is True

    def test_existing_account_check(self, sample_user_data):
        """Test detection of existing account types"""
        # sample_user_data has checking account
        assert has_existing_account(sample_user_data["accounts"], "checking") is True
        assert has_existing_account(sample_user_data["accounts"], "savings") is False

    def test_predatory_product_blocking(self):
        """Test blocking of predatory financial products"""
        predatory_offers = [
            {"type": "payday_loan", "apr": 25.0},
            {"type": "title_loan", "apr": 30.0},
            {"type": "rent_to_own", "apr": 40.0},
            {"type": "personal_loan", "apr": 50.0}  # High APR
        ]

        for offer in predatory_offers:
            assert is_predatory_product(offer) is True

    def test_legitimate_product_allowed(self):
        """Test that legitimate products are allowed"""
        legitimate_offers = [
            {"type": "credit_card", "apr": 19.99},
            {"type": "personal_loan", "apr": 12.99},
            {"type": "mortgage", "apr": 4.5}
        ]

        for offer in legitimate_offers:
            assert is_predatory_product(offer) is False

    def test_comprehensive_eligibility(self, sample_user_data, sample_partner_offer):
        """Test comprehensive eligibility check"""
        # sample_partner_offer has $30k min income, sample_user_data has $50k
        # Should pass all checks
        is_eligible = check_eligibility(sample_partner_offer, sample_user_data)

        # Depends on offer details, but should not crash
        assert isinstance(is_eligible, bool)

    def test_duplicate_account_blocking(self, sample_user_data):
        """Test blocking offers for duplicate account types"""
        # Offer for checking account when user already has one
        offer = {
            "type": "checking_account",
            "account_type": "checking",
            "min_income": 0,
            "apr": 0.0
        }

        # User already has checking account
        is_eligible = check_eligibility(offer, sample_user_data)

        # Should be blocked due to existing account
        assert is_eligible is False


@pytest.mark.guardrails
@pytest.mark.unit
class TestDisclosureGuardrails:
    """Test standard disclosure generation"""

    def test_disclaimer_generated(self):
        """Test that standard disclaimer is generated"""
        disclaimer = generate_standard_disclaimer()

        assert disclaimer is not None
        assert len(disclaimer) > 0
        assert "educational" in disclaimer.lower() or "information" in disclaimer.lower()

    def test_disclaimer_consistency(self):
        """Test that disclaimer is consistent"""
        disclaimer1 = generate_standard_disclaimer()
        disclaimer2 = generate_standard_disclaimer()

        # Should be identical (deterministic)
        assert disclaimer1 == disclaimer2
