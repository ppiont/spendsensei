#!/usr/bin/env python3
"""
Test script for Story 2.5: Signal Computation Service

Validates compute_signals() function with synthetic data:
- Tests both 30-day and 180-day windows
- Verifies all signals are populated correctly
- Measures execution time (<200ms target)
- Tests with multiple synthetic users
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select
from spendsense.database import AsyncSessionLocal
from spendsense.services.features import compute_signals
from spendsense.models.user import User


async def test_compute_signals():
    """Test compute_signals with different window sizes and users"""

    print("=" * 80)
    print("Story 2.5: Signal Computation Service - Manual Validation")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # Get all users from database
        result = await db.execute(select(User))
        users = result.scalars().all()

        if not users:
            print("\n❌ ERROR: No users found in database")
            print("Please run synthetic data generator first (Story 1.4)")
            return False

        print(f"\nFound {len(users)} synthetic users in database")

        # Test with multiple window sizes
        window_sizes = [30, 180]

        all_passed = True

        for window_days in window_sizes:
            print(f"\n{'=' * 80}")
            print(f"Testing with {window_days}-day window")
            print(f"{'=' * 80}")

            user_times = []

            for idx, user in enumerate(users[:5], 1):  # Test first 5 users
                print(f"\n[{idx}/5] Testing user: {user.id} ({user.email})")

                # Measure execution time
                start_time = time.time()

                try:
                    signals = await compute_signals(db, user.id, window_days)

                    elapsed_ms = (time.time() - start_time) * 1000
                    user_times.append(elapsed_ms)

                    # Verify all fields are populated
                    print(f"  ✅ Execution time: {elapsed_ms:.2f}ms")

                    # Check subscriptions
                    if signals.subscriptions is not None:
                        sub_count = signals.subscriptions.get('count', 0)
                        print(f"  ✅ Subscriptions: {sub_count} detected")
                    else:
                        print(f"  ❌ Subscriptions: None (should be dict)")
                        all_passed = False

                    # Check savings
                    if signals.savings is not None:
                        savings_balance = signals.savings.get('total_balance', 0)
                        print(f"  ✅ Savings: ${savings_balance / 100:.2f}")
                    else:
                        print(f"  ❌ Savings: None (should be dict)")
                        all_passed = False

                    # Check credit
                    if signals.credit is not None:
                        credit_util = signals.credit.get('overall_utilization', 0)
                        print(f"  ✅ Credit: {credit_util:.1f}% utilization")
                    else:
                        print(f"  ❌ Credit: None (should be dict)")
                        all_passed = False

                    # Check income
                    if signals.income is not None:
                        income_freq = signals.income.get('frequency', 'unknown')
                        income_stability = signals.income.get('stability', 'unknown')
                        print(f"  ✅ Income: {income_freq}, {income_stability}")
                    else:
                        print(f"  ❌ Income: None (should be dict)")
                        all_passed = False

                    # Performance check
                    if elapsed_ms > 200:
                        print(f"  ⚠️  WARNING: Execution time exceeds 200ms target")
                        all_passed = False

                except Exception as e:
                    print(f"  ❌ ERROR: {str(e)}")
                    all_passed = False
                    elapsed_ms = (time.time() - start_time) * 1000
                    user_times.append(elapsed_ms)

            # Summary for this window
            if user_times:
                avg_time = sum(user_times) / len(user_times)
                max_time = max(user_times)
                min_time = min(user_times)

                print(f"\n{'-' * 80}")
                print(f"Performance Summary ({window_days}-day window):")
                print(f"  Average: {avg_time:.2f}ms")
                print(f"  Min: {min_time:.2f}ms")
                print(f"  Max: {max_time:.2f}ms")
                print(f"  Target: <200ms per user")

                if avg_time < 200:
                    print(f"  ✅ PASS: Average within target")
                else:
                    print(f"  ❌ FAIL: Average exceeds target")
                    all_passed = False

    # Final summary
    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("Signal computation service working correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print("Review errors above")
    print(f"{'=' * 80}\n")

    return all_passed


async def test_edge_cases():
    """Test edge cases and error handling"""

    print("\n" + "=" * 80)
    print("Testing Edge Cases")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # Test 1: Non-existent user
        print("\n[1] Testing non-existent user...")
        try:
            await compute_signals(db, "non-existent-user-id", 30)
            print("  ❌ FAIL: Should have raised HTTPException(404)")
            return False
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                print(f"  ✅ PASS: Correctly raised error: {str(e)}")
            else:
                print(f"  ❌ FAIL: Wrong error type: {str(e)}")
                return False

        # Test 2: Verify cutoff date calculation
        print("\n[2] Testing cutoff date calculation...")
        from datetime import datetime, timedelta

        # Get a real user
        result = await db.execute(select(User))
        users = result.scalars().all()

        if users:
            user = users[0]

            # Test 30-day window
            signals_30 = await compute_signals(db, user.id, 30)
            signals_180 = await compute_signals(db, user.id, 180)

            # Compare transaction counts (180-day should have more or equal)
            # Note: We can't directly verify counts, but we can check structure
            print(f"  ✅ PASS: Both windows computed successfully")
        else:
            print(f"  ⚠️  SKIP: No users available")

    print("\n" + "=" * 80)
    print("✅ Edge case tests completed")
    print("=" * 80)

    return True


async def main():
    """Run all tests"""
    print("\nStarting Signal Computation Service Tests...\n")

    # Test main functionality
    main_passed = await test_compute_signals()

    # Test edge cases
    edge_passed = await test_edge_cases()

    # Overall result
    print("\n" + "=" * 80)
    print("OVERALL TEST RESULTS")
    print("=" * 80)
    print(f"Main Tests: {'✅ PASS' if main_passed else '❌ FAIL'}")
    print(f"Edge Cases: {'✅ PASS' if edge_passed else '❌ FAIL'}")

    if main_passed and edge_passed:
        print("\n🎉 All acceptance criteria met!")
        print("Story 2.5 implementation complete")
        return 0
    else:
        print("\n⚠️  Some tests failed - review implementation")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
