"""
Recommend Module - Recommendation Engine

This module provides the recommendation generation pipeline including:
- Content selection from educational catalog
- Partner offer matching
- Rationale generation
- LLM-powered content generation (optional)

Main entry point: StandardRecommendationEngine
"""

from spendsense.recommend.types import (
    EducationItem,
    PartnerOffer,
    Rationale,
    EligibilityRules,
    ContentGenerator,
)
from spendsense.recommend.engine import (
    Recommendation,
    OfferRecommendation,
    RecommendationResult,
    RecommendationEngine,
    StandardRecommendationEngine,
    AIRecommendationEngine,
)
from spendsense.recommend.content_selection import TemplateGenerator
from spendsense.recommend.llm_generation import LLMGenerator

# Backward compatibility aliases
TemplateContentGenerator = TemplateGenerator
LLMContentGenerator = LLMGenerator

# Legacy compatibility
from spendsense.recommend.legacy import (
    generate_recommendations,
    Recommendation as LegacyRecommendation,
)

__all__ = [
    # Types
    "EducationItem",
    "PartnerOffer",
    "Rationale",
    "EligibilityRules",
    "ContentGenerator",
    # Engine
    "Recommendation",
    "OfferRecommendation",
    "RecommendationResult",
    "RecommendationEngine",
    "StandardRecommendationEngine",
    "AIRecommendationEngine",
    # Content generators
    "TemplateContentGenerator",
    "LLMContentGenerator",
    # Legacy
    "generate_recommendations",
    "LegacyRecommendation",
]
