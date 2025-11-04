#!/usr/bin/env python3
"""
Demo: Complete Recommendation Pipeline

This demo shows the end-to-end recommendation system that orchestrates:
1. Signal computation from raw transaction data
2. Persona assignment based on behavioral patterns
3. Content selection using relevance scoring
4. Rationale generation with explainability

The demo demonstrates full traceability from transactions → signals → persona → recommendations.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy.ext.asyncio import AsyncSession
from spendsense.database import AsyncSessionLocal
from spendsense.services.recommendations import generate_recommendations
import json


async def demo_recommendation_pipeline():
    """Demonstrate complete recommendation pipeline with one user."""

    print("=" * 80)
    print("RECOMMENDATION PIPELINE DEMO")
    print("=" * 80)
    print()
    print("This demo shows the complete recommendation pipeline:")
    print("  1. Transaction Data → Behavioral Signals")
    print("  2. Signals → Persona Assignment")
    print("  3. Persona + Signals → Content Selection")
    print("  4. Content + Signals → Rationale Generation")
    print("  5. Complete → Personalized Recommendations")
    print()
    print("=" * 80)
    print()

    # Get a real user from database
    async with AsyncSessionLocal() as db:
        from spendsense.models.user import User
        from sqlalchemy import select

        # Fetch first user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("No users found in database. Please run synthetic data generator first.")
            print("Run: python -m spendsense.services.synthetic_data --load --num-users 50")
            return

        print(f"Demo User: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print()

        # Generate recommendations
        print("Generating recommendations...")
        print()

        recommendations = await generate_recommendations(
            db=db,
            user_id=user.id,
            window_days=30
        )

        if not recommendations:
            print("No recommendations generated.")
            return

        print(f"✓ Generated {len(recommendations)} personalized recommendations")
        print()
        print("=" * 80)
        print()

        # Display each recommendation in detail
        for idx, rec in enumerate(recommendations, 1):
            print(f"RECOMMENDATION {idx}")
            print("=" * 80)
            print()

            print("PERSONA ASSIGNMENT")
            print("-" * 80)
            print(f"Assigned Persona: {rec.persona}")
            print(f"Confidence Score: {rec.confidence:.2%}")
            print(f"Key Behavioral Signals Detected: {', '.join(rec.rationale.key_signals)}")
            print()

            print("WHY THIS MATTERS (Rationale)")
            print("-" * 80)
            print(rec.rationale.explanation)
            print()

            print("RECOMMENDED CONTENT")
            print("-" * 80)
            print(f"Title: {rec.content.title}")
            print(f"Relevance Score: {rec.content.relevance_score:.2%}")
            print()
            print(f"Summary: {rec.content.summary}")
            print()
            print(f"What to do: {rec.content.cta}")
            print()
            print(f"Source: {rec.content.source}")
            print()

            print("CONTENT PREVIEW")
            print("-" * 80)
            # Show first 300 characters of body
            print(rec.content.body[:300] + "...")
            print()
            print("=" * 80)
            print()

        # Show complete recommendation data structure
        print("COMPLETE DATA STRUCTURE")
        print("=" * 80)
        print()
        print("First recommendation as JSON:")
        print()
        print(json.dumps(recommendations[0].model_dump(), indent=2, default=str))
        print()
        print("=" * 80)
        print()

        # Summary
        print("PIPELINE SUMMARY")
        print("=" * 80)
        print()
        print(f"✓ User profiled: {user.name} ({user.id[:8]}...)")
        print(f"✓ Persona identified: {recommendations[0].persona}")
        print(f"✓ Signals analyzed: {len(recommendations[0].rationale.key_signals)} behavioral patterns")
        print(f"✓ Content selected: {len(recommendations)} relevant education items")
        print(f"✓ Rationales generated: Full explainability for all recommendations")
        print()
        print("The system provides:")
        print("  - Transparent persona assignment based on objective signals")
        print("  - Personalized content matching user's financial situation")
        print("  - Clear explanations with concrete data points")
        print("  - Actionable guidance tailored to individual needs")
        print()
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_recommendation_pipeline())
