"""
Unit tests for persona matching functions.

Tests each persona matching function with synthetic signals to verify
correct threshold detection.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spendsense.features import BehaviorSignals
from spendsense.personas import (
    matches_high_utilization,
    matches_variable_income,
    matches_subscription_heavy,
    matches_savings_builder,
    PERSONA_PRIORITY,
    CONFIDENCE_SCORES
)


def test_high_utilization():
    """Test high utilization matching."""
    print("Testing matches_high_utilization()...")
    print("-" * 80)

    # Test case 1: High utilization (>=50%)
    signals = BehaviorSignals(
        credit={"overall_utilization": 60.0, "flags": []}
    )
    assert matches_high_utilization(signals) == True, "Should match on 60% utilization"
    print("  ✓ Matches on 60% utilization")

    # Test case 2: Exactly 50% utilization
    signals = BehaviorSignals(
        credit={"overall_utilization": 50.0, "flags": []}
    )
    assert matches_high_utilization(signals) == True, "Should match on 50% utilization"
    print("  ✓ Matches on 50% utilization (threshold)")

    # Test case 3: Interest charges flag
    signals = BehaviorSignals(
        credit={"overall_utilization": 20.0, "flags": ["interest_charges"]}
    )
    assert matches_high_utilization(signals) == True, "Should match on interest charges"
    print("  ✓ Matches on interest charges flag")

    # Test case 4: Overdue flag
    signals = BehaviorSignals(
        credit={"overall_utilization": 10.0, "flags": ["overdue"]}
    )
    assert matches_high_utilization(signals) == True, "Should match on overdue"
    print("  ✓ Matches on overdue flag")

    # Test case 5: Below threshold, no flags
    signals = BehaviorSignals(
        credit={"overall_utilization": 30.0, "flags": []}
    )
    assert matches_high_utilization(signals) == False, "Should not match on 30% utilization"
    print("  ✓ Does not match on 30% utilization")

    print()


def test_variable_income():
    """Test variable income matching."""
    print("Testing matches_variable_income()...")
    print("-" * 80)

    # Test case 1: Gap >45 days AND buffer <1 month
    signals = BehaviorSignals(
        income={"median_gap_days": 50, "buffer_months": 0.8}
    )
    assert matches_variable_income(signals) == True, "Should match on 50 day gap + 0.8 month buffer"
    print("  ✓ Matches on 50 day gap + 0.8 month buffer")

    # Test case 2: Gap exactly 46 days (just over threshold)
    signals = BehaviorSignals(
        income={"median_gap_days": 46, "buffer_months": 0.5}
    )
    assert matches_variable_income(signals) == True, "Should match on 46 day gap"
    print("  ✓ Matches on 46 day gap (threshold)")

    # Test case 3: Gap >45 but buffer >=1 month
    signals = BehaviorSignals(
        income={"median_gap_days": 60, "buffer_months": 1.5}
    )
    assert matches_variable_income(signals) == False, "Should not match with 1.5 month buffer"
    print("  ✓ Does not match with sufficient buffer")

    # Test case 4: Gap <=45 days
    signals = BehaviorSignals(
        income={"median_gap_days": 30, "buffer_months": 0.5}
    )
    assert matches_variable_income(signals) == False, "Should not match on 30 day gap"
    print("  ✓ Does not match on regular income frequency")

    print()


def test_subscription_heavy():
    """Test subscription heavy matching."""
    print("Testing matches_subscription_heavy()...")
    print("-" * 80)

    # Test case 1: 3+ subscriptions AND spend >=$50
    signals = BehaviorSignals(
        subscriptions={"count": 3, "monthly_recurring_spend": 5000, "percentage_of_spending": 5.0}
    )
    assert matches_subscription_heavy(signals) == True, "Should match on 3 subs + $50 spend"
    print("  ✓ Matches on 3 subscriptions + $50 monthly spend")

    # Test case 2: 3+ subscriptions AND percentage >=10%
    signals = BehaviorSignals(
        subscriptions={"count": 4, "monthly_recurring_spend": 3000, "percentage_of_spending": 12.0}
    )
    assert matches_subscription_heavy(signals) == True, "Should match on 4 subs + 12% of spending"
    print("  ✓ Matches on 4 subscriptions + 12% of spending")

    # Test case 3: Exactly 3 subscriptions + exactly $50 (5000 cents)
    signals = BehaviorSignals(
        subscriptions={"count": 3, "monthly_recurring_spend": 5000, "percentage_of_spending": 8.0}
    )
    assert matches_subscription_heavy(signals) == True, "Should match on threshold values"
    print("  ✓ Matches on threshold values")

    # Test case 4: <3 subscriptions
    signals = BehaviorSignals(
        subscriptions={"count": 2, "monthly_recurring_spend": 10000, "percentage_of_spending": 15.0}
    )
    assert matches_subscription_heavy(signals) == False, "Should not match on 2 subscriptions"
    print("  ✓ Does not match on insufficient subscription count")

    # Test case 5: 3+ subscriptions but low spend and percentage
    signals = BehaviorSignals(
        subscriptions={"count": 3, "monthly_recurring_spend": 2000, "percentage_of_spending": 5.0}
    )
    assert matches_subscription_heavy(signals) == False, "Should not match on low spend"
    print("  ✓ Does not match on low subscription spend")

    print()


def test_savings_builder():
    """Test savings builder matching."""
    print("Testing matches_savings_builder()...")
    print("-" * 80)

    # Test case 1: Growth >=2% AND utilization <30%
    signals = BehaviorSignals(
        savings={"growth_rate": 3.0, "monthly_inflow": 10000},
        credit={"overall_utilization": 20.0}
    )
    assert matches_savings_builder(signals) == True, "Should match on 3% growth + 20% utilization"
    print("  ✓ Matches on 3% growth + 20% utilization")

    # Test case 2: Inflow >=$200 AND utilization <30%
    signals = BehaviorSignals(
        savings={"growth_rate": 1.0, "monthly_inflow": 20000},  # $200 = 20000 cents
        credit={"overall_utilization": 15.0}
    )
    assert matches_savings_builder(signals) == True, "Should match on $200 inflow + 15% utilization"
    print("  ✓ Matches on $200 monthly inflow + 15% utilization")

    # Test case 3: Exactly 2% growth (threshold)
    signals = BehaviorSignals(
        savings={"growth_rate": 2.0, "monthly_inflow": 5000},
        credit={"overall_utilization": 10.0}
    )
    assert matches_savings_builder(signals) == True, "Should match on 2% growth threshold"
    print("  ✓ Matches on 2% growth threshold")

    # Test case 4: Good savings but high utilization
    signals = BehaviorSignals(
        savings={"growth_rate": 5.0, "monthly_inflow": 50000},
        credit={"overall_utilization": 40.0}
    )
    assert matches_savings_builder(signals) == False, "Should not match with high utilization"
    print("  ✓ Does not match with high credit utilization")

    # Test case 5: Low growth and low inflow
    signals = BehaviorSignals(
        savings={"growth_rate": 1.0, "monthly_inflow": 10000},
        credit={"overall_utilization": 10.0}
    )
    assert matches_savings_builder(signals) == False, "Should not match on insufficient savings"
    print("  ✓ Does not match on insufficient savings")

    # Test case 6: Good savings, no credit account
    signals = BehaviorSignals(
        savings={"growth_rate": 3.0, "monthly_inflow": 25000},
        credit=None
    )
    assert matches_savings_builder(signals) == True, "Should match with no credit account"
    print("  ✓ Matches with no credit account (assumes 0% utilization)")

    print()


def test_priority_order():
    """Test that personas are checked in correct priority order."""
    print("Testing persona priority order...")
    print("-" * 80)

    expected_order = ["high_utilization", "variable_income", "subscription_heavy", "savings_builder", "balanced"]
    assert PERSONA_PRIORITY == expected_order, "Priority order should match expected"
    print(f"  ✓ Priority order correct: {' > '.join(PERSONA_PRIORITY)}")
    print()


def test_confidence_scores():
    """Test that confidence scores are defined for all personas."""
    print("Testing confidence scores...")
    print("-" * 80)

    expected_scores = {
        "high_utilization": 0.95,
        "variable_income": 0.90,
        "subscription_heavy": 0.85,
        "savings_builder": 0.80,
        "balanced": 0.60
    }

    for persona, expected_confidence in expected_scores.items():
        actual_confidence = CONFIDENCE_SCORES.get(persona)
        assert actual_confidence == expected_confidence, f"{persona} confidence should be {expected_confidence}"
        print(f"  ✓ {persona}: {actual_confidence}")

    print()


def main():
    """Run all unit tests."""
    print("=" * 80)
    print("PERSONA MATCHING UNIT TESTS")
    print("=" * 80)
    print()

    tests = [
        test_high_utilization,
        test_variable_income,
        test_subscription_heavy,
        test_savings_builder,
        test_priority_order,
        test_confidence_scores
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✓ All unit tests PASSED")
    else:
        print("✗ Some unit tests FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()
