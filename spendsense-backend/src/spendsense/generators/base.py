"""
Abstract Base Class for Content Generators

This module defines the abstract interface for content generators that provide
personalized educational content and rationales based on user behavioral signals.

The abstract design allows for future implementations (e.g., LLM-based generators)
while maintaining a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, Field

from spendsense.services.features import BehaviorSignals


class EducationItem(BaseModel):
    """
    Educational content item selected for a user.

    Represents a single piece of curated financial education content
    from the content catalog, enriched with relevance metadata.
    """
    id: str = Field(..., description="Unique identifier from content catalog (e.g., 'edu_credit_101')")
    title: str = Field(..., description="Title of the educational content")
    summary: str = Field(..., description="Brief summary of the content")
    body: str = Field(..., description="Full text content with detailed information")
    cta: str = Field(..., description="Call-to-action text for user engagement")
    source: str = Field(..., description="Source attribution for the content")
    relevance_score: float = Field(..., description="Computed relevance score (0.0-1.0) for this user", ge=0.0, le=1.0)


class Rationale(BaseModel):
    """
    Explainable rationale for why content was selected.

    Provides transparent reasoning with concrete data points to help users
    understand why specific content is relevant to their situation.
    """
    persona_type: str = Field(..., description="Assigned persona (e.g., 'high_utilization')")
    confidence: float = Field(..., description="Confidence score for persona assignment (0.0-1.0)", ge=0.0, le=1.0)
    explanation: str = Field(..., description="Human-readable explanation with concrete data points")
    key_signals: List[str] = Field(default_factory=list, description="List of triggered signal tags (e.g., ['high_utilization_80'])")


class ContentGenerator(ABC):
    """
    Abstract base class for content generation implementations.

    Defines the interface that all content generators must implement,
    allowing for flexible swap between template-based and LLM-based approaches.
    """

    @abstractmethod
    async def generate_education(
        self,
        persona_type: str,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> List[EducationItem]:
        """
        Generate personalized educational content items.

        Implementations should:
        1. Filter content by persona match
        2. Score content by signal relevance
        3. Return top N most relevant items

        Args:
            persona_type: User's assigned persona (e.g., 'high_utilization')
            signals: BehaviorSignals object with computed user data
            limit: Maximum number of education items to return (default: 3)

        Returns:
            List of EducationItem objects, sorted by relevance (highest first)

        Raises:
            ValueError: If persona_type is invalid or signals are missing
        """
        pass

    @abstractmethod
    async def generate_rationale(
        self,
        persona_type: str,
        confidence: float,
        signals: BehaviorSignals
    ) -> Rationale:
        """
        Generate explainable rationale for persona assignment.

        Implementations should:
        1. Format concrete data points from signals
        2. Create human-readable explanations
        3. List relevant signal tags that triggered

        Args:
            persona_type: User's assigned persona
            confidence: Confidence score for the assignment (0.0-1.0)
            signals: BehaviorSignals object with computed user data

        Returns:
            Rationale object with explanation and key signals

        Raises:
            ValueError: If persona_type is invalid or signals are missing
        """
        pass
