"""Content generators for personalized financial insights.

This module provides different strategies for generating educational content
and rationales for financial recommendations.
"""

from spendsense.recommend.types import ContentGenerator, EducationItem, Rationale
from spendsense.recommend.llm_generation import LLMGenerator

__all__ = ["ContentGenerator", "EducationItem", "Rationale", "LLMGenerator"]
