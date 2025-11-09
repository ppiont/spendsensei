#!/usr/bin/env python3
"""
Test script for Template-Based Content Generator

Tests the TemplateGenerator with various synthetic user scenarios to verify:
1. Content catalog loading
2. Education item selection based on persona and signals
3. Rationale generation with concrete data points
4. Relevance scoring algorithm
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spendsense.generators.template import TemplateGenerator
from spendsense.features import BehaviorSignals


async def test_high_utilization_persona():
    """Test content generation for high utilization persona"""
    print("\n" + "="*80)
    print("TEST 1: High Utilization Persona")
    print("="*80)

    # Create synthetic signals for high utilization user
    signals = BehaviorSignals(
        credit={
            "overall_utilization": 85.0,
            "total_balance": 850000,  # $8,500 in cents
            "total_limit": 1000000,   # $10,000 in cents
            "flags": ["interest_charges", "overdue"]
        },
        subscriptions={"count": 2, "monthly_recurring_spend": 3000},
        savings={"growth_rate": 0.5, "monthly_inflow": 5000},
        income={"median_gap_days": 14, "stability": "stable", "average_amount": 350000, "buffer_months": 2.0}
    )

    generator = TemplateGenerator()

    # Generate education content
    print("\n📚 Generating Education Content...")
    education_items = await generator.generate_education(
        persona_type="high_utilization",
        signals=signals,
        limit=3
    )

    print(f"\nFound {len(education_items)} relevant education items:")
    for i, item in enumerate(education_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   ID: {item.id}")
        print(f"   Relevance Score: {item.relevance_score:.2f}")
        print(f"   Summary: {item.summary[:100]}...")

    # Generate rationale
    print("\n💡 Generating Rationale...")
    rationale = await generator.generate_rationale(
        persona_type="high_utilization",
        confidence=0.95,
        signals=signals
    )

    print(f"\nPersona: {rationale.persona_type}")
    print(f"Confidence: {rationale.confidence:.2f}")
    print(f"Key Signals: {', '.join(rationale.key_signals)}")
    print(f"\nExplanation:\n{rationale.explanation}")

    # Assertions
    assert len(education_items) > 0, "Should return education items"
    assert education_items[0].relevance_score > 0.5, "Top item should have high relevance"
    assert "high_utilization" in rationale.key_signals or "interest_charges" in rationale.key_signals
    assert "85.0%" in rationale.explanation, "Should include concrete utilization percentage"
    assert "$8,500" in rationale.explanation, "Should include concrete balance amount"

    print("\n✅ High Utilization Persona Test PASSED")


async def test_variable_income_persona():
    """Test content generation for variable income persona"""
    print("\n" + "="*80)
    print("TEST 2: Variable Income Persona")
    print("="*80)

    # Create synthetic signals for variable income user
    signals = BehaviorSignals(
        income={
            "median_gap_days": 60,
            "stability": "variable",
            "average_amount": 450000,  # $4,500
            "buffer_months": 0.8,
            "coefficient_variation": 0.45
        },
        credit={"overall_utilization": 25.0, "total_balance": 250000, "total_limit": 1000000, "flags": []},
        subscriptions={"count": 2, "monthly_recurring_spend": 4000},
        savings={"growth_rate": 1.0, "monthly_inflow": 10000}
    )

    generator = TemplateGenerator()

    # Generate education content
    print("\n📚 Generating Education Content...")
    education_items = await generator.generate_education(
        persona_type="variable_income",
        signals=signals,
        limit=3
    )

    print(f"\nFound {len(education_items)} relevant education items:")
    for i, item in enumerate(education_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Relevance Score: {item.relevance_score:.2f}")

    # Generate rationale
    print("\n💡 Generating Rationale...")
    rationale = await generator.generate_rationale(
        persona_type="variable_income",
        confidence=0.90,
        signals=signals
    )

    print(f"\nPersona: {rationale.persona_type}")
    print(f"Key Signals: {', '.join(rationale.key_signals)}")
    print(f"\nExplanation:\n{rationale.explanation}")

    # Assertions
    assert len(education_items) > 0, "Should return education items"
    assert "variable_income" in rationale.key_signals
    assert "60 days" in rationale.explanation, "Should mention median gap"
    assert "0.8 months" in rationale.explanation, "Should mention buffer months"

    print("\n✅ Variable Income Persona Test PASSED")


async def test_subscription_heavy_persona():
    """Test content generation for subscription heavy persona"""
    print("\n" + "="*80)
    print("TEST 3: Subscription Heavy Persona")
    print("="*80)

    # Create synthetic signals for subscription heavy user
    signals = BehaviorSignals(
        subscriptions={
            "count": 8,
            "monthly_recurring_spend": 15000,  # $150
            "percentage_of_spending": 15.0
        },
        credit={"overall_utilization": 20.0, "total_balance": 200000, "total_limit": 1000000, "flags": []},
        income={"median_gap_days": 14, "stability": "stable", "average_amount": 500000, "buffer_months": 3.0},
        savings={"growth_rate": 2.5, "monthly_inflow": 20000}
    )

    generator = TemplateGenerator()

    # Generate education content
    print("\n📚 Generating Education Content...")
    education_items = await generator.generate_education(
        persona_type="subscription_heavy",
        signals=signals,
        limit=3
    )

    print(f"\nFound {len(education_items)} relevant education items:")
    for i, item in enumerate(education_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Relevance Score: {item.relevance_score:.2f}")

    # Generate rationale
    print("\n💡 Generating Rationale...")
    rationale = await generator.generate_rationale(
        persona_type="subscription_heavy",
        confidence=0.85,
        signals=signals
    )

    print(f"\nPersona: {rationale.persona_type}")
    print(f"Key Signals: {', '.join(rationale.key_signals)}")
    print(f"\nExplanation:\n{rationale.explanation}")

    # Assertions
    assert len(education_items) > 0, "Should return education items"
    assert "subscription_heavy" in rationale.key_signals
    assert "8 active" in rationale.explanation, "Should mention subscription count"
    assert "$150" in rationale.explanation, "Should mention monthly spend"

    print("\n✅ Subscription Heavy Persona Test PASSED")


async def test_savings_builder_persona():
    """Test content generation for savings builder persona"""
    print("\n" + "="*80)
    print("TEST 4: Savings Builder Persona")
    print("="*80)

    # Create synthetic signals for savings builder user
    signals = BehaviorSignals(
        savings={
            "growth_rate": 5.0,
            "monthly_inflow": 50000,  # $500
            "buffer_months": 4.5
        },
        credit={"overall_utilization": 15.0, "total_balance": 150000, "total_limit": 1000000, "flags": []},
        income={"median_gap_days": 14, "stability": "stable", "average_amount": 600000, "buffer_months": 4.5},
        subscriptions={"count": 2, "monthly_recurring_spend": 3000}
    )

    generator = TemplateGenerator()

    # Generate education content
    print("\n📚 Generating Education Content...")
    education_items = await generator.generate_education(
        persona_type="savings_builder",
        signals=signals,
        limit=3
    )

    print(f"\nFound {len(education_items)} relevant education items:")
    for i, item in enumerate(education_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Relevance Score: {item.relevance_score:.2f}")

    # Generate rationale
    print("\n💡 Generating Rationale...")
    rationale = await generator.generate_rationale(
        persona_type="savings_builder",
        confidence=0.80,
        signals=signals
    )

    print(f"\nPersona: {rationale.persona_type}")
    print(f"Key Signals: {', '.join(rationale.key_signals)}")
    print(f"\nExplanation:\n{rationale.explanation}")

    # Assertions
    assert len(education_items) > 0, "Should return education items"
    assert "positive_savings" in rationale.key_signals
    assert "5.0%" in rationale.explanation, "Should mention growth rate"
    assert "$500" in rationale.explanation, "Should mention monthly inflow"

    print("\n✅ Savings Builder Persona Test PASSED")


async def test_balanced_persona():
    """Test content generation for balanced persona"""
    print("\n" + "="*80)
    print("TEST 5: Balanced Persona")
    print("="*80)

    # Create synthetic signals for balanced user
    signals = BehaviorSignals(
        credit={"overall_utilization": 20.0, "total_balance": 200000, "total_limit": 1000000, "flags": []},
        income={"median_gap_days": 14, "stability": "stable", "average_amount": 500000, "buffer_months": 3.5},
        savings={"growth_rate": 1.5, "monthly_inflow": 15000, "buffer_months": 3.5},
        subscriptions={"count": 2, "monthly_recurring_spend": 4000}
    )

    generator = TemplateGenerator()

    # Generate education content
    print("\n📚 Generating Education Content...")
    education_items = await generator.generate_education(
        persona_type="balanced",
        signals=signals,
        limit=3
    )

    print(f"\nFound {len(education_items)} relevant education items:")
    for i, item in enumerate(education_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Relevance Score: {item.relevance_score:.2f}")

    # Generate rationale
    print("\n💡 Generating Rationale...")
    rationale = await generator.generate_rationale(
        persona_type="balanced",
        confidence=0.60,
        signals=signals
    )

    print(f"\nPersona: {rationale.persona_type}")
    print(f"Key Signals: {', '.join(rationale.key_signals)}")
    print(f"\nExplanation:\n{rationale.explanation}")

    # Assertions
    assert len(education_items) > 0, "Should return education items"
    assert "stable_income" in rationale.key_signals or "positive_savings" in rationale.key_signals
    assert "healthy" in rationale.explanation.lower(), "Should mention healthy financial habits"

    print("\n✅ Balanced Persona Test PASSED")


async def test_relevance_scoring():
    """Test that relevance scoring works correctly"""
    print("\n" + "="*80)
    print("TEST 6: Relevance Scoring Algorithm")
    print("="*80)

    # Create signals with multiple tags
    signals = BehaviorSignals(
        credit={
            "overall_utilization": 85.0,
            "total_balance": 850000,
            "total_limit": 1000000,
            "flags": ["interest_charges", "overdue"]
        },
        subscriptions={"count": 5, "monthly_recurring_spend": 10000},
        savings={"growth_rate": 0.5, "monthly_inflow": 5000},
        income={"median_gap_days": 14, "stability": "stable"}
    )

    generator = TemplateGenerator()

    # Generate education content
    education_items = await generator.generate_education(
        persona_type="high_utilization",
        signals=signals,
        limit=5
    )

    print(f"\nGenerated {len(education_items)} items with relevance scores:")
    for item in education_items:
        print(f"  - {item.title}: {item.relevance_score:.2f}")

    # Verify scores are sorted correctly
    scores = [item.relevance_score for item in education_items]
    assert scores == sorted(scores, reverse=True), "Items should be sorted by relevance"

    # Verify top item has high score
    assert education_items[0].relevance_score >= 0.5, "Top item should have high relevance"

    # Verify all scores are in valid range
    for item in education_items:
        assert 0.0 <= item.relevance_score <= 1.0, f"Score {item.relevance_score} out of range"

    print("\n✅ Relevance Scoring Test PASSED")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TEMPLATE GENERATOR TEST SUITE")
    print("="*80)

    try:
        await test_high_utilization_persona()
        await test_variable_income_persona()
        await test_subscription_heavy_persona()
        await test_savings_builder_persona()
        await test_balanced_persona()
        await test_relevance_scoring()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nTemplate-based content generator is working correctly:")
        print("  ✓ Content catalog loading")
        print("  ✓ Education item selection and filtering")
        print("  ✓ Relevance scoring algorithm")
        print("  ✓ Rationale generation with concrete data")
        print("  ✓ All persona types covered")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
