"""
Abstract Base Class for Content Generators

This module defines the abstract interface for content generators that provide
personalized educational content, partner offers, and rationales based on user
behavioral signals.

The abstract design allows for future implementations (e.g., LLM-based generators)
while maintaining a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from spendsense.features import BehaviorSignals


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
    relevance_score: int = Field(..., description="Computed relevance score (1-5 scale) for this user", ge=1, le=5)


class EligibilityRules(BaseModel):
    """
    Eligibility criteria for partner offers.

    Defines the requirements a user must meet to receive a partner offer.
    All criteria are optional and are combined with AND logic.
    """
    min_credit_utilization: Optional[float] = Field(None, description="Minimum credit utilization % (e.g., 50.0)", ge=0.0, le=100.0)
    max_credit_utilization: Optional[float] = Field(None, description="Maximum credit utilization % (e.g., 30.0)", ge=0.0, le=100.0)
    min_monthly_income: Optional[int] = Field(None, description="Minimum monthly income in cents")
    min_credit_score_estimate: Optional[int] = Field(None, description="Estimated minimum credit score (derived from utilization)", ge=300, le=850)
    max_credit_score_estimate: Optional[int] = Field(None, description="Estimated maximum credit score", ge=300, le=850)
    required_account_types: Optional[List[str]] = Field(default_factory=list, description="Required account types (e.g., ['credit'])")
    excluded_account_subtypes: Optional[List[str]] = Field(default_factory=list, description="Exclude if user has these account subtypes (e.g., ['savings'])")
    required_signals: Optional[List[str]] = Field(default_factory=list, description="Required signal tags (AND logic)")
    excluded_signals: Optional[List[str]] = Field(default_factory=list, description="Exclude if these signals present")
    min_emergency_fund_months: Optional[float] = Field(None, description="Minimum emergency fund coverage in months", ge=0.0)
    max_emergency_fund_months: Optional[float] = Field(None, description="Maximum emergency fund coverage in months", ge=0.0)


class PartnerOffer(BaseModel):
    """
    Partner product offer selected for a user.

    Represents a financial product or service offer from a partner,
    with eligibility rules and explainable benefits.
    """
    id: str = Field(..., description="Unique offer identifier (e.g., 'offer_balance_transfer_01')")
    title: str = Field(..., description="Offer title")
    provider: str = Field(..., description="Partner/provider name")
    offer_type: str = Field(..., description="Type of offer (balance_transfer_card, high_yield_savings, budgeting_app, etc.)")
    summary: str = Field(..., description="Brief offer summary")
    benefits: List[str] = Field(..., description="List of key benefits")
    eligibility_explanation: str = Field(..., description="Plain-language eligibility explanation")
    cta: str = Field(..., description="Call-to-action text")
    cta_url: str = Field(..., description="URL for the offer (partner link)")
    disclaimer: str = Field(..., description="Required legal disclaimer")
    relevance_score: int = Field(..., description="Computed relevance score (1-5 scale) for this user", ge=1, le=5)
    eligibility_met: bool = Field(..., description="Whether user meets eligibility criteria")


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
    async def generate_offers(
        self,
        persona_type: str,
        signals: BehaviorSignals,
        accounts: List,  # List of Account objects
        limit: int = 3
    ) -> List[PartnerOffer]:
        """
        Generate personalized partner offers with eligibility checking.

        Implementations should:
        1. Filter offers by persona relevance
        2. Check eligibility requirements against user data
        3. Score offers by relevance and eligibility fit
        4. Return top N eligible offers

        Args:
            persona_type: User's assigned persona (e.g., 'high_utilization')
            signals: BehaviorSignals object with computed user data
            accounts: List of user's Account objects for eligibility checking
            limit: Maximum number of offers to return (default: 3)

        Returns:
            List of PartnerOffer objects with eligibility_met=True,
            sorted by relevance (highest first)

        Raises:
            ValueError: If persona_type is invalid or required data missing
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
