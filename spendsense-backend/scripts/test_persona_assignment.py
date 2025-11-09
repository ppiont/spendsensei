"""
Test script for persona assignment logic using synthetic data.

This script tests the persona assignment system with diverse user profiles
to ensure correct classification according to priority order.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy.ext.asyncio import AsyncSession
from spendsense.database import AsyncSessionLocal
from spendsense.personas import assign_persona, PERSONA_PRIORITY


async def test_persona_assignment():
    """Test persona assignment with synthetic users."""

    print("=" * 80)
    print("PERSONA ASSIGNMENT TEST")
    print("=" * 80)
    print()

    # Get real user IDs from database
    async with AsyncSessionLocal() as db:
        from spendsense.models.user import User
        from sqlalchemy import select

        # Fetch first 5 users
        result = await db.execute(select(User.id).limit(5))
        user_ids = [row[0] for row in result.all()]

    if not user_ids:
        print("✗ No users found in database. Please run synthetic data generator first.")
        print("  Run: python -m spendsense.services.synthetic_data --load --num-users 50")
        return

    print(f"Testing with {len(user_ids)} users from database")
    print()

    results = []

    async with AsyncSessionLocal() as db:
        for i, user_id in enumerate(user_ids, 1):
            print(f"Testing User {i}/{len(user_ids)}: {user_id[:8]}...")
            print("-" * 80)

            try:
                # Assign persona with 180-day window
                result = await assign_persona(db, user_id, window_days=180)

                persona_type = result["persona_type"]
                confidence = result["confidence"]
                signals = result["signals"]

                print(f"✓ Assigned: {persona_type} (confidence: {confidence})")
                print()

                # Show signal summary
                print("Signal Summary:")

                # Subscription signals
                if signals.subscriptions:
                    sub_count = signals.subscriptions.get("count", 0)
                    sub_spend = signals.subscriptions.get("monthly_recurring_spend", 0)
                    print(f"  Subscriptions: {sub_count} active, ${sub_spend/100:.2f}/month")

                # Credit signals
                if signals.credit:
                    utilization = signals.credit.get("overall_utilization", 0.0)
                    flags = signals.credit.get("flags", [])
                    print(f"  Credit: {utilization:.1f}% utilization, flags: {flags}")

                # Income signals
                if signals.income:
                    frequency = signals.income.get("frequency", "unknown")
                    stability = signals.income.get("stability", "unknown")
                    median_gap = signals.income.get("median_gap_days", 0)
                    buffer = signals.income.get("buffer_months", 0.0)
                    print(f"  Income: {frequency}/{stability}, gap: {median_gap} days, buffer: {buffer:.1f} months")

                # Savings signals
                if signals.savings:
                    growth = signals.savings.get("growth_rate", 0.0)
                    inflow = signals.savings.get("monthly_inflow", 0)
                    print(f"  Savings: {growth:.1f}% growth, ${inflow/100:.2f}/month inflow")

                print()

                results.append({
                    "user_id": user_id,
                    "persona": persona_type,
                    "confidence": confidence
                })

            except Exception as e:
                print(f"✗ Error: {str(e)}")
                print()

    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print("Persona Priority Order:")
    for i, persona in enumerate(PERSONA_PRIORITY, 1):
        print(f"  {i}. {persona}")
    print()

    print("Assignment Results:")
    print()

    for result in results:
        print(f"  {result['user_id'][:8]}...: {result['persona']} (confidence: {result['confidence']})")

    # Verify diversity of personas assigned
    persona_counts = {}
    for result in results:
        persona = result["persona"]
        persona_counts[persona] = persona_counts.get(persona, 0) + 1

    print("Persona Distribution:")
    for persona in PERSONA_PRIORITY:
        count = persona_counts.get(persona, 0)
        bar = "█" * count
        print(f"  {persona:20s}: {bar} ({count})")
    print()

    # Validation checks
    print("Validation Checks:")
    print()

    checks_passed = 0
    total_checks = 3

    # Check 1: All users should have a persona
    if len(results) == len(user_ids):
        print("  ✓ All users received persona assignments")
        checks_passed += 1
    else:
        print("  ✗ Some users did not receive persona assignments")

    # Check 2: No confidence scores outside valid range
    valid_confidence = all(0.60 <= r["confidence"] <= 0.95 for r in results)
    if valid_confidence:
        print("  ✓ All confidence scores in valid range (0.60-0.95)")
        checks_passed += 1
    else:
        print("  ✗ Some confidence scores outside valid range")

    # Check 3: At least 2 different personas assigned (shows diversity)
    unique_personas = len(set(r["persona"] for r in results))
    if unique_personas >= 2:
        print(f"  ✓ Diverse personas assigned ({unique_personas} different types)")
        checks_passed += 1
    else:
        print("  ✗ Not enough diversity in persona assignments")

    print()
    print(f"Checks passed: {checks_passed}/{total_checks}")
    print()

    if checks_passed == total_checks:
        print("✓ All validation checks PASSED")
    else:
        print("✗ Some validation checks FAILED")

    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_persona_assignment())
