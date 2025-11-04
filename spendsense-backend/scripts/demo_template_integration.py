#!/usr/bin/env python3
"""
Integration Demo: Template Generator with Persona Assignment

This script demonstrates how the TemplateGenerator integrates with the
persona assignment system to provide complete personalized recommendations.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spendsense.generators.template import TemplateGenerator
from spendsense.services.features import BehaviorSignals


async def generate_full_recommendation(persona_type: str, confidence: float, signals: BehaviorSignals):
    """
    Generate complete recommendation package (education + rationale)

    This is how the API endpoint would use the TemplateGenerator.
    """
    generator = TemplateGenerator()

    # Generate personalized education content
    education_items = await generator.generate_education(
        persona_type=persona_type,
        signals=signals,
        limit=3
    )

    # Generate explainable rationale
    rationale = await generator.generate_rationale(
        persona_type=persona_type,
        confidence=confidence,
        signals=signals
    )

    return {
        "persona": {
            "type": persona_type,
            "confidence": confidence
        },
        "rationale": {
            "explanation": rationale.explanation,
            "key_signals": rationale.key_signals
        },
        "education": [
            {
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "body": item.body,
                "cta": item.cta,
                "source": item.source,
                "relevance_score": item.relevance_score
            }
            for item in education_items
        ]
    }


async def main():
    """Demo the full integration"""
    print("="*80)
    print("TEMPLATE GENERATOR INTEGRATION DEMO")
    print("="*80)

    # Simulate a user with high credit utilization
    print("\n📊 User Profile: High Credit Utilization")
    print("-" * 80)

    signals = BehaviorSignals(
        credit={
            "overall_utilization": 75.0,
            "total_balance": 750000,  # $7,500
            "total_limit": 1000000,   # $10,000
            "flags": ["interest_charges"]
        },
        income={
            "median_gap_days": 14,
            "stability": "stable",
            "average_amount": 500000,
            "buffer_months": 2.5
        },
        savings={
            "growth_rate": 0.5,
            "monthly_inflow": 10000,
            "buffer_months": 2.5
        },
        subscriptions={
            "count": 3,
            "monthly_recurring_spend": 7500
        }
    )

    # Generate recommendations
    recommendation = await generate_full_recommendation(
        persona_type="high_utilization",
        confidence=0.95,
        signals=signals
    )

    # Display results in API-like format
    print(f"\n🎯 PERSONA: {recommendation['persona']['type']}")
    print(f"   Confidence: {recommendation['persona']['confidence']:.0%}")

    print(f"\n💡 RATIONALE:")
    print(f"   {recommendation['rationale']['explanation']}")
    print(f"\n   Key Signals: {', '.join(recommendation['rationale']['key_signals'])}")

    print(f"\n📚 RECOMMENDED EDUCATION ({len(recommendation['education'])} items):")
    for i, item in enumerate(recommendation['education'], 1):
        print(f"\n   {i}. {item['title']}")
        print(f"      Relevance: {item['relevance_score']:.0%}")
        print(f"      Summary: {item['summary']}")
        print(f"      CTA: {item['cta']}")

    print("\n" + "="*80)
    print("✅ Integration demo complete!")
    print("="*80)
    print("\nThis output format can be directly returned by the API endpoint.")
    print("Users receive personalized, explainable recommendations based on")
    print("their behavioral signals - no AI API calls required!")


if __name__ == "__main__":
    asyncio.run(main())
