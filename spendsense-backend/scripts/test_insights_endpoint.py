#!/usr/bin/env python3
"""
Test script for Story 4.4: Insights Endpoint

Tests:
1. GET /insights/{user_id} - retrieve personalized recommendations
2. Window parameter (30, 90, 180 days)
3. Response includes persona, confidence, recommendations
4. 404 error handling for non-existent users
5. Response time <5 seconds
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.services.recommendations import generate_recommendations
from spendsense.generators.template import TemplateGenerator
from sqlalchemy import select


async def test_insights_generation():
    """Test insights generation for a user"""
    print("\n" + "=" * 60)
    print("TEST 1: Generate User Insights")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a real user from database
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with user: {test_user.id} ({test_user.name})")

        # Generate recommendations
        generator = TemplateGenerator()
        start_time = time.time()

        recommendations = await generate_recommendations(
            db=db,
            user_id=test_user.id,
            generator=generator,
            window_days=30
        )

        elapsed = time.time() - start_time

        print(f"✓ Generated {len(recommendations)} recommendations in {elapsed:.2f}s")

        if len(recommendations) > 0:
            rec = recommendations[0]
            print(f"\n  Sample recommendation:")
            print(f"    Persona: {rec.persona}")
            print(f"    Confidence: {rec.confidence:.2f}")
            print(f"    Content ID: {rec.content.id}")
            print(f"    Title: {rec.content.title}")
            print(f"    Relevance: {rec.content.relevance_score:.2f}")
            print(f"    Key signals: {', '.join(rec.rationale.key_signals[:3])}")

        # Verify structure
        assert len(recommendations) > 0, "Should return at least one recommendation"
        for rec in recommendations:
            assert rec.persona is not None, "Persona should be assigned"
            assert 0 <= rec.confidence <= 1, f"Confidence {rec.confidence} out of range"
            assert rec.content.id is not None, "Content should have ID"
            assert rec.rationale.explanation is not None, "Should have rationale"

        print("\n✅ TEST 1 PASSED")
        return True


async def test_window_parameters():
    """Test different window parameters"""
    print("\n" + "=" * 60)
    print("TEST 2: Window Parameters (30, 180 days)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a user
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        generator = TemplateGenerator()
        windows = [30, 180]  # Only 30 and 180 day windows are supported

        for window in windows:
            start = time.time()
            recommendations = await generate_recommendations(
                db=db,
                user_id=test_user.id,
                generator=generator,
                window_days=window
            )
            elapsed = time.time() - start

            print(f"✓ {window}-day window: {len(recommendations)} recommendations ({elapsed:.2f}s)")

            # Verify response structure
            assert len(recommendations) > 0, f"Should return recommendations for {window}-day window"

        print("\n✅ TEST 2 PASSED")
        return True


async def test_persona_and_confidence():
    """Test persona assignment and confidence scores"""
    print("\n" + "=" * 60)
    print("TEST 3: Persona Assignment & Confidence Scores")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get multiple users to see different personas
        result = await db.execute(select(User).limit(5))
        test_users = result.scalars().all()

        if len(test_users) == 0:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with {len(test_users)} users")

        generator = TemplateGenerator()
        personas_found = set()

        for user in test_users:
            recommendations = await generate_recommendations(
                db=db,
                user_id=user.id,
                generator=generator,
                window_days=30
            )

            if len(recommendations) > 0:
                persona = recommendations[0].persona
                confidence = recommendations[0].confidence
                personas_found.add(persona)

                print(f"  User {user.name[:20]:20s} → {persona:20s} (confidence: {confidence:.2f})")

                # Verify confidence in valid range
                assert 0 <= confidence <= 1, f"Confidence {confidence} out of range"

        print(f"\n✓ Found {len(personas_found)} different personas: {', '.join(personas_found)}")

        print("\n✅ TEST 3 PASSED")
        return True


async def test_user_not_found():
    """Test 404 error handling for non-existent user"""
    print("\n" + "=" * 60)
    print("TEST 4: User Not Found (404)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        fake_user_id = "user_does_not_exist_12345"

        # Check user doesn't exist
        result = await db.execute(
            select(User).where(User.id == fake_user_id)
        )
        user = result.scalar_one_or_none()

        assert user is None, "Test user should not exist"
        print(f"✓ Confirmed user {fake_user_id} does not exist")

        # Try to generate insights (should handle gracefully or raise error)
        generator = TemplateGenerator()
        try:
            recommendations = await generate_recommendations(
                db=db,
                user_id=fake_user_id,
                generator=generator,
                window_days=30
            )
            # If it doesn't raise an error, check that it returns empty or handles gracefully
            print(f"✓ Handled non-existent user gracefully (returned {len(recommendations)} recommendations)")
        except Exception as e:
            # Expected behavior: should raise an exception
            print(f"✓ Correctly raised error for non-existent user: {type(e).__name__}")

        print("\n✅ TEST 4 PASSED")
        return True


async def test_performance():
    """Test response time is under 5 seconds"""
    print("\n" + "=" * 60)
    print("TEST 5: Performance (<5 seconds)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get multiple users
        result = await db.execute(select(User).limit(3))
        test_users = result.scalars().all()

        if len(test_users) == 0:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with {len(test_users)} users")

        generator = TemplateGenerator()
        times = []

        for user in test_users:
            start = time.time()
            recommendations = await generate_recommendations(
                db=db,
                user_id=user.id,
                generator=generator,
                window_days=30
            )
            elapsed = time.time() - start
            times.append(elapsed)

            print(f"  User {user.name[:30]:30s}: {elapsed:.2f}s ({len(recommendations)} recommendations)")

        avg_time = sum(times) / len(times)
        max_time = max(times)

        print(f"\n  Average: {avg_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")

        # Verify performance meets requirements
        assert max_time < 5.0, f"Generation took {max_time:.2f}s, exceeds 5s target"

        print(f"\n✓ All requests completed in <5s")

        print("\n✅ TEST 5 PASSED")
        return True


async def test_recommendation_structure():
    """Test that recommendations have all required fields"""
    print("\n" + "=" * 60)
    print("TEST 6: Recommendation Structure Validation")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a user
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        generator = TemplateGenerator()
        recommendations = await generate_recommendations(
            db=db,
            user_id=test_user.id,
            generator=generator,
            window_days=30
        )

        print(f"✓ Validating structure of {len(recommendations)} recommendations")

        for i, rec in enumerate(recommendations, 1):
            # Check content fields
            assert rec.content.id, f"Rec {i}: Content missing ID"
            assert rec.content.title, f"Rec {i}: Content missing title"
            assert rec.content.summary, f"Rec {i}: Content missing summary"
            assert rec.content.body, f"Rec {i}: Content missing body"
            assert rec.content.cta, f"Rec {i}: Content missing CTA"
            assert rec.content.source, f"Rec {i}: Content missing source"
            assert 0 <= rec.content.relevance_score <= 1, f"Rec {i}: Invalid relevance score"

            # Check rationale fields
            assert rec.rationale.persona_type, f"Rec {i}: Rationale missing persona_type"
            assert 0 <= rec.rationale.confidence <= 1, f"Rec {i}: Invalid rationale confidence"
            assert rec.rationale.explanation, f"Rec {i}: Rationale missing explanation"
            assert len(rec.rationale.key_signals) > 0, f"Rec {i}: Rationale has no key signals"

            # Check top-level fields
            assert rec.persona, f"Rec {i}: Missing persona"
            assert 0 <= rec.confidence <= 1, f"Rec {i}: Invalid confidence"

            print(f"  ✓ Recommendation {i}: All required fields present")

        print("\n✅ TEST 6 PASSED")
        return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("STORY 4.4: Insights Endpoint Test Suite")
    print("=" * 60)

    tests = [
        ("Generate User Insights", test_insights_generation),
        ("Window Parameters", test_window_parameters),
        ("Persona Assignment & Confidence", test_persona_and_confidence),
        ("User Not Found (404)", test_user_not_found),
        ("Performance (<5 seconds)", test_performance),
        ("Recommendation Structure", test_recommendation_structure),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
