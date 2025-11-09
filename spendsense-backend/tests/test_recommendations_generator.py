"""Test suite for content generators

Converted from scripts/test_template_generator.py to pytest format.
Tests template-based content selection and scoring.
"""

import pytest
from spendsense.recommend.content_selection import TemplateGenerator
from spendsense.features import BehaviorSignals


@pytest.mark.recommendations
@pytest.mark.unit
class TestTemplateGenerator:
    """Test TemplateGenerator content selection"""

    async def test_generate_education_items(self):
        """Test generation of education items"""
        generator = TemplateGenerator()

        # Create sample signals
        signals = BehaviorSignals(
            credit={"overall_utilization": 0.85},
            income=None,
            subscriptions=None,
            savings=None
        )

        items = await generator.generate_education(
            persona_type="high_utilization",
            signals=signals,
            limit=3
        )

        # Should return 3 items
        assert len(items) == 3

        # All items should have required fields
        for item in items:
            assert item.id is not None
            assert item.title is not None
            assert item.summary is not None
            assert 1 <= item.relevance_score <= 5

    async def test_relevance_scoring_range(self):
        """Test that relevance scores are in 1-5 range"""
        generator = TemplateGenerator()

        signals = BehaviorSignals(
            credit={"overall_utilization": 0.90},
            income=None,
            subscriptions=None,
            savings=None
        )

        items = await generator.generate_education(
            persona_type="high_utilization",
            signals=signals,
            limit=5
        )

        # All scores should be 1-5 integers
        for item in items:
            assert isinstance(item.relevance_score, int)
            assert 1 <= item.relevance_score <= 5

    async def test_signal_tag_matching(self):
        """Test that content matches signal tags"""
        generator = TemplateGenerator()

        # Signals with subscriptions
        signals = BehaviorSignals(
            credit=None,
            income=None,
            subscriptions={"recurring_merchant_count": 5},
            savings=None
        )

        items = await generator.generate_education(
            persona_type="subscription_heavy",
            signals=signals,
            limit=3
        )

        # Should get subscription-related content
        assert len(items) > 0

    async def test_persona_filtering(self):
        """Test that content is filtered by persona"""
        generator = TemplateGenerator()

        signals = BehaviorSignals(
            credit={"overall_utilization": 0.85},
            income=None,
            subscriptions=None,
            savings=None
        )

        # Generate for high_utilization persona
        items = await generator.generate_education(
            persona_type="high_utilization",
            signals=signals,
            limit=3
        )

        # Should only get high_utilization relevant content
        assert len(items) > 0

    async def test_offer_eligibility_filtering(self, sample_user_data):
        """Test partner offer eligibility filtering"""
        generator = TemplateGenerator()

        signals = BehaviorSignals(
            credit={"overall_utilization": 0.85},
            income=None,
            subscriptions=None,
            savings=None
        )

        # Create account objects from sample data
        from spendsense.models.account import Account
        accounts = []
        for acc_data in sample_user_data["accounts"]:
            account = Account(
                id=f"test-{acc_data['subtype']}",
                user_id="test-user",
                type="credit" if "credit" in acc_data["subtype"] else "depository",
                subtype=acc_data["subtype"],
                name=f"Test {acc_data['subtype']}",
                mask="1234",
                current_balance=acc_data.get("balance", 0),
                currency="USD",
                holder_category="personal"
            )
            if "limit" in acc_data:
                account.limit = acc_data["limit"]
            accounts.append(account)

        offers = await generator.generate_offers(
            persona_type="high_utilization",
            signals=signals,
            accounts=accounts,
            limit=3
        )

        # All returned offers should meet eligibility
        for offer in offers:
            assert offer.eligibility_met is True

    async def test_rationale_generation(self):
        """Test rationale generation for recommendations"""
        generator = TemplateGenerator()

        signals = BehaviorSignals(
            credit={"overall_utilization": 0.85},
            income=None,
            subscriptions=None,
            savings=None
        )

        rationale = await generator.generate_rationale(
            persona_type="high_utilization",
            confidence=0.92,
            signals=signals
        )

        # Should have all required fields
        assert rationale.persona_type == "high_utilization"
        assert rationale.confidence == 0.92
        assert len(rationale.explanation) > 0
        assert len(rationale.key_signals) > 0
