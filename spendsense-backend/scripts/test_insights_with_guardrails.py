"""Integration test for insights endpoint with guardrails."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select
from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.recommend.legacy import generate_recommendations
from spendsense.generators.template import TemplateGenerator
from spendsense.schemas.insight import InsightsResponse, RecommendationResponse


async def test_insights_integration():
    """Test full insights pipeline with guardrails."""
    print("=" * 60)
    print("INSIGHTS INTEGRATION TEST WITH GUARDRAILS")
    print("=" * 60)

    # Get database session
    async with AsyncSessionLocal() as db:
        # Get first test user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("✗ No users found in database")
            return False

        print(f"\n✓ Testing with user: {user.name} ({user.id})")

        # Initialize generator
        generator = TemplateGenerator()

        # Generate recommendations
        print("\nGenerating recommendations...")
        recommendations = await generate_recommendations(
            db=db,
            user_id=user.id,
            generator=generator,
            window_days=30
        )

        if not recommendations:
            print("✗ No recommendations generated")
            return False

        print(f"✓ Generated {len(recommendations)} recommendations")

        # Check each recommendation for tone violations
        print("\nChecking recommendations for tone violations...")
        all_clean = True

        for i, rec in enumerate(recommendations, 1):
            explanation = rec.rationale.explanation
            print(f"\n  Recommendation {i}:")
            print(f"    Persona: {rec.persona}")
            print(f"    Content: {rec.content.title}")
            print(f"    Explanation length: {len(explanation)} chars")

            # Check for shaming language
            from spendsense.guardrails import check_tone
            is_valid, violations = check_tone(explanation)

            if is_valid:
                print(f"    ✓ Tone check: PASS (no violations)")
            else:
                print(f"    ✗ Tone check: FAIL (violations: {violations})")
                all_clean = False

        # Test InsightsResponse wrapper with disclaimer
        print("\n" + "=" * 60)
        print("Testing InsightsResponse with disclaimer")
        print("=" * 60)

        recommendation_responses = [
            RecommendationResponse.from_recommendation(rec)
            for rec in recommendations
        ]

        insights_response = InsightsResponse(recommendations=recommendation_responses)

        print(f"\n✓ InsightsResponse created successfully")
        print(f"  Recommendations count: {len(insights_response.recommendations)}")
        print(f"  Disclaimer length: {len(insights_response.disclaimer)} chars")
        print(f"\n  Disclaimer text:")
        print(f"  {insights_response.disclaimer}")

        # Verify disclaimer is present and contains key terms
        from spendsense.guardrails import DISCLAIMER

        if insights_response.disclaimer == DISCLAIMER:
            print("\n✓ Disclaimer matches DISCLAIMER constant")
        else:
            print("\n✗ Disclaimer does not match DISCLAIMER constant")
            return False

        required_terms = ["educational", "financial advice", "professional"]
        for term in required_terms:
            if term.lower() in insights_response.disclaimer.lower():
                print(f"  ✓ Contains '{term}'")
            else:
                print(f"  ✗ Missing '{term}'")
                return False

        print("\n" + "=" * 60)
        if all_clean:
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TONE VIOLATIONS FOUND")
        print("=" * 60)

        return all_clean


def main():
    """Run integration test."""
    try:
        result = asyncio.run(test_insights_integration())
        return 0 if result else 1
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
