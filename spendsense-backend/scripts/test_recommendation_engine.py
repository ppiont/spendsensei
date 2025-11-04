#!/usr/bin/env python3
"""
Test script for recommendation engine using synthetic data.

This script tests the complete recommendation pipeline:
1. Persona assignment (from behavioral signals)
2. Content generation (educational items)
3. Rationale generation (explainability)
4. Complete recommendation assembly

Tests both 30d and 180d windows and measures performance.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy.ext.asyncio import AsyncSession
from spendsense.database import AsyncSessionLocal
from spendsense.services.recommendations import generate_recommendations
from spendsense.generators.template import TemplateGenerator


async def test_recommendation_engine():
    """Test recommendation engine with synthetic users."""

    print("=" * 80)
    print("RECOMMENDATION ENGINE TEST")
    print("=" * 80)
    print()

    # Get real user IDs from database
    async with AsyncSessionLocal() as db:
        from spendsense.models.user import User
        from sqlalchemy import select

        # Fetch first 5 users for testing
        result = await db.execute(select(User.id).limit(5))
        user_ids = [row[0] for row in result.all()]

    if not user_ids:
        print("✗ No users found in database. Please run synthetic data generator first.")
        print("  Run: python -m spendsense.services.synthetic_data --load --num-users 50")
        return

    print(f"Testing with {len(user_ids)} users from database")
    print()

    # Test both 30-day and 180-day windows
    windows = [30, 180]
    all_results = []

    for window_days in windows:
        print("=" * 80)
        print(f"TESTING WITH {window_days}-DAY WINDOW")
        print("=" * 80)
        print()

        results = []
        total_time = 0

        async with AsyncSessionLocal() as db:
            for i, user_id in enumerate(user_ids, 1):
                print(f"Testing User {i}/{len(user_ids)}: {user_id[:8]}...")
                print("-" * 80)

                try:
                    # Measure performance
                    start_time = time.time()

                    # Generate recommendations with default TemplateGenerator
                    recommendations = await generate_recommendations(
                        db=db,
                        user_id=user_id,
                        window_days=window_days
                    )

                    elapsed_ms = (time.time() - start_time) * 1000
                    total_time += elapsed_ms

                    print(f"✓ Generated {len(recommendations)} recommendations in {elapsed_ms:.0f}ms")
                    print()

                    # Display recommendations
                    for idx, rec in enumerate(recommendations, 1):
                        print(f"Recommendation {idx}:")
                        print(f"  Content ID: {rec.content.id}")
                        print(f"  Title: {rec.content.title}")
                        print(f"  Relevance: {rec.content.relevance_score:.2f}")
                        print(f"  Persona: {rec.persona} (confidence: {rec.confidence:.2f})")
                        print(f"  Key Signals: {', '.join(rec.rationale.key_signals[:3])}...")
                        print(f"  Rationale (first 150 chars): {rec.rationale.explanation[:150]}...")
                        print()

                    results.append({
                        "user_id": user_id,
                        "window_days": window_days,
                        "num_recommendations": len(recommendations),
                        "elapsed_ms": elapsed_ms,
                        "persona": recommendations[0].persona if recommendations else None,
                        "confidence": recommendations[0].confidence if recommendations else None
                    })

                except Exception as e:
                    print(f"✗ Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    print()

        # Window summary
        print("=" * 80)
        print(f"SUMMARY: {window_days}-DAY WINDOW")
        print("=" * 80)
        print()

        if results:
            avg_time = total_time / len(results)
            print(f"Average generation time: {avg_time:.0f}ms")
            print(f"Total time: {total_time:.0f}ms")
            print()

            print("User Results:")
            for result in results:
                status = "✓" if result["num_recommendations"] > 0 else "✗"
                print(
                    f"  {status} {result['user_id'][:8]}...: "
                    f"{result['num_recommendations']} recommendations in {result['elapsed_ms']:.0f}ms "
                    f"(persona: {result['persona']}, confidence: {result['confidence']:.2f})"
                )
            print()

        all_results.extend(results)

    # Overall validation checks
    print("=" * 80)
    print("OVERALL VALIDATION CHECKS")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 6

    # Check 1: All users received recommendations
    total_users_tested = len(user_ids) * len(windows)
    successful_results = [r for r in all_results if r["num_recommendations"] > 0]
    if len(successful_results) == total_users_tested:
        print("  ✓ All users received recommendations for all windows")
        checks_passed += 1
    else:
        print(f"  ✗ Some users did not receive recommendations ({len(successful_results)}/{total_users_tested})")

    # Check 2: Each user gets exactly 3 recommendations (default limit)
    correct_count = all(r["num_recommendations"] == 3 for r in all_results if r["num_recommendations"] > 0)
    if correct_count:
        print("  ✓ All users received exactly 3 recommendations")
        checks_passed += 1
    else:
        print("  ✗ Some users received incorrect number of recommendations")

    # Check 3: Performance target (<500ms)
    avg_time_overall = sum(r["elapsed_ms"] for r in all_results) / len(all_results) if all_results else 0
    if avg_time_overall < 500:
        print(f"  ✓ Average generation time under 500ms ({avg_time_overall:.0f}ms)")
        checks_passed += 1
    else:
        print(f"  ✗ Average generation time exceeds 500ms ({avg_time_overall:.0f}ms)")

    # Check 4: All confidence scores in valid range
    valid_confidence = all(
        0.60 <= r["confidence"] <= 0.95
        for r in all_results
        if r["confidence"] is not None
    )
    if valid_confidence:
        print("  ✓ All confidence scores in valid range (0.60-0.95)")
        checks_passed += 1
    else:
        print("  ✗ Some confidence scores outside valid range")

    # Check 5: Both window sizes work correctly
    windows_tested = set(r["window_days"] for r in all_results)
    if windows_tested == {30, 180}:
        print("  ✓ Both 30-day and 180-day windows tested successfully")
        checks_passed += 1
    else:
        print(f"  ✗ Not all window sizes tested ({windows_tested})")

    # Check 6: Persona diversity (at least 2 different personas)
    unique_personas = len(set(r["persona"] for r in all_results if r["persona"]))
    if unique_personas >= 2:
        print(f"  ✓ Diverse personas in recommendations ({unique_personas} different types)")
        checks_passed += 1
    else:
        print("  ✗ Not enough diversity in personas")

    print()
    print(f"Checks passed: {checks_passed}/{total_checks}")
    print()

    if checks_passed == total_checks:
        print("✓ All validation checks PASSED")
    else:
        print("✗ Some validation checks FAILED")

    print()

    # Detailed recommendation analysis
    print("=" * 80)
    print("DETAILED RECOMMENDATION ANALYSIS")
    print("=" * 80)
    print()

    # Show one complete recommendation example
    if all_results:
        print("Example Complete Recommendation (User 1, 30d window):")
        print()

        async with AsyncSessionLocal() as db:
            try:
                recommendations = await generate_recommendations(
                    db=db,
                    user_id=user_ids[0],
                    window_days=30
                )

                if recommendations:
                    rec = recommendations[0]
                    print(f"Persona: {rec.persona} (confidence: {rec.confidence:.2f})")
                    print()
                    print("Content:")
                    print(f"  ID: {rec.content.id}")
                    print(f"  Title: {rec.content.title}")
                    print(f"  Summary: {rec.content.summary}")
                    print(f"  Relevance Score: {rec.content.relevance_score:.2f}")
                    print(f"  CTA: {rec.content.cta}")
                    print(f"  Source: {rec.content.source}")
                    print()
                    print("Rationale:")
                    print(f"  Persona Type: {rec.rationale.persona_type}")
                    print(f"  Confidence: {rec.rationale.confidence:.2f}")
                    print(f"  Key Signals: {', '.join(rec.rationale.key_signals)}")
                    print(f"  Explanation:")
                    print(f"    {rec.rationale.explanation}")
                    print()
                    print("Full Recommendation Object:")
                    print(f"  {rec.model_dump_json(indent=2)[:500]}...")
                    print()

            except Exception as e:
                print(f"✗ Error generating example: {str(e)}")
                print()

    # Performance breakdown
    print("=" * 80)
    print("PERFORMANCE BREAKDOWN")
    print("=" * 80)
    print()

    for window in windows:
        window_results = [r for r in all_results if r["window_days"] == window]
        if window_results:
            times = [r["elapsed_ms"] for r in window_results]
            avg = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"{window}-day window:")
            print(f"  Average: {avg:.0f}ms")
            print(f"  Min: {min_time:.0f}ms")
            print(f"  Max: {max_time:.0f}ms")
            print(f"  Target: <500ms → {'✓ PASS' if avg < 500 else '✗ FAIL'}")
            print()

    print("=" * 80)
    print()

    # Final status
    if checks_passed == total_checks and avg_time_overall < 500:
        print("🎉 RECOMMENDATION ENGINE TEST PASSED")
    else:
        print("⚠️  RECOMMENDATION ENGINE TEST FAILED")

    print()
    print("=" * 80)


async def test_error_handling():
    """Test error handling for edge cases."""

    print()
    print("=" * 80)
    print("ERROR HANDLING TESTS")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as db:
        # Test 1: Invalid user ID
        print("Test 1: Invalid user ID")
        try:
            recommendations = await generate_recommendations(
                db=db,
                user_id="invalid_user_id_12345",
                window_days=30
            )
            print("  ✗ Should have raised an error for invalid user")
        except Exception as e:
            print(f"  ✓ Correctly raised error: {type(e).__name__}")
        print()

        # Test 2: Invalid window_days
        print("Test 2: Invalid window_days")
        try:
            recommendations = await generate_recommendations(
                db=db,
                user_id="test_user",
                window_days=999  # Invalid window
            )
            print("  ✗ Should have raised ValueError for invalid window")
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError: {str(e)}")
        print()

        # Test 3: Empty user_id
        print("Test 3: Empty user_id")
        try:
            recommendations = await generate_recommendations(
                db=db,
                user_id="",
                window_days=30
            )
            print("  ✗ Should have raised ValueError for empty user_id")
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError: {str(e)}")
        print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(test_recommendation_engine())
    asyncio.run(test_error_handling())
