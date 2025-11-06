"""Insight schemas for API responses (recommendations, persona, etc.)"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from spendsense.utils.guardrails import DISCLAIMER


class EducationItemResponse(BaseModel):
    """Educational content item"""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    summary: str = Field(..., description="Brief summary (2-3 sentences)")
    body: str = Field(..., description="Full educational content")
    cta: str = Field(..., description="Call-to-action text")
    source: str = Field(..., description="Content source (template, llm, human)")
    relevance_score: float = Field(..., description="Relevance score (0.0-1.0)", ge=0.0, le=1.0)


class PartnerOfferResponse(BaseModel):
    """Partner product offer"""
    id: str = Field(..., description="Offer ID")
    title: str = Field(..., description="Offer title")
    provider: str = Field(..., description="Partner/provider name")
    offer_type: str = Field(..., description="Type of offer (balance_transfer_card, high_yield_savings, etc.)")
    summary: str = Field(..., description="Brief offer summary")
    benefits: List[str] = Field(..., description="List of key benefits")
    eligibility_explanation: str = Field(..., description="Plain-language eligibility explanation")
    cta: str = Field(..., description="Call-to-action text")
    cta_url: str = Field(..., description="URL for the offer")
    disclaimer: str = Field(..., description="Legal disclaimer")
    relevance_score: float = Field(..., description="Relevance score (0.0-1.0)", ge=0.0, le=1.0)
    eligibility_met: bool = Field(..., description="Whether user meets eligibility criteria")


class RationaleResponse(BaseModel):
    """Rationale explaining why content was recommended"""
    persona_type: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona assignment confidence (0.0-1.0)", ge=0.0, le=1.0)
    explanation: str = Field(..., description="Plain-language explanation of why this content was selected")
    key_signals: List[str] = Field(..., description="Key behavioral signals that triggered this recommendation")


class RecommendationResponse(BaseModel):
    """Complete recommendation with content and rationale"""
    content: EducationItemResponse = Field(..., description="Educational content item")
    rationale: RationaleResponse = Field(..., description="Explainable rationale")
    persona: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona confidence score (0.0-1.0)", ge=0.0, le=1.0)


class OfferRecommendationResponse(BaseModel):
    """Partner offer recommendation with rationale"""
    offer: PartnerOfferResponse = Field(..., description="Partner offer details")
    rationale: RationaleResponse = Field(..., description="Explainable rationale")
    persona: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona confidence score (0.0-1.0)", ge=0.0, le=1.0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": {
                        "id": "credit-util-101",
                        "title": "Understanding Credit Utilization: The 30% Rule",
                        "summary": "Learn why keeping credit utilization below 30% is crucial for your credit score.",
                        "body": "Credit utilization is one of the most important factors...",
                        "cta": "Review Your Credit Cards",
                        "source": "template",
                        "relevance_score": 0.85
                    },
                    "rationale": {
                        "persona_type": "high_utilization",
                        "confidence": 0.95,
                        "explanation": "You've been identified as a High Utilization user because your credit card utilization is 77.5%...",
                        "key_signals": ["high_utilization_50", "interest_charges"]
                    },
                    "persona": "high_utilization",
                    "confidence": 0.95
                }
            ]
        }
    }

    @classmethod
    def from_recommendation(cls, recommendation):
        """Convert Recommendation model to API response schema"""
        return cls(
            content=EducationItemResponse(
                id=recommendation.content.id,
                title=recommendation.content.title,
                summary=recommendation.content.summary,
                body=recommendation.content.body,
                cta=recommendation.content.cta,
                source=recommendation.content.source,
                relevance_score=recommendation.content.relevance_score
            ),
            rationale=RationaleResponse(
                persona_type=recommendation.rationale.persona_type,
                confidence=recommendation.rationale.confidence,
                explanation=recommendation.rationale.explanation,
                key_signals=recommendation.rationale.key_signals
            ),
            persona=recommendation.persona,
            confidence=recommendation.confidence
        )


class InsightsResponse(BaseModel):
    """Insights response with education, offers, persona, and disclaimer"""
    persona_type: str = Field(..., description="Assigned persona type")
    confidence: float = Field(..., description="Persona assignment confidence (0.0-1.0)", ge=0.0, le=1.0)
    education_recommendations: List[RecommendationResponse] = Field(..., description="Educational content recommendations (typically 3)")
    offer_recommendations: List[OfferRecommendationResponse] = Field(default_factory=list, description="Partner offer recommendations (0-3 eligible offers)")
    signals_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of detected behavioral signals")
    consent_required: bool = Field(default=False, description="Whether user needs to provide consent to see insights")
    disclaimer: str = Field(default=DISCLAIMER, description="Legal disclaimer for educational content and offers")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recommendations": [
                        {
                            "content": {
                                "id": "credit-util-101",
                                "title": "Understanding Credit Utilization: The 30% Rule",
                                "summary": "Learn why keeping credit utilization below 30% is crucial for your credit score.",
                                "body": "Credit utilization is one of the most important factors...",
                                "cta": "Review Your Credit Cards",
                                "source": "template",
                                "relevance_score": 0.85
                            },
                            "rationale": {
                                "persona_type": "high_utilization",
                                "confidence": 0.95,
                                "explanation": "You've been identified as a High Utilization user...",
                                "key_signals": ["high_utilization_50", "interest_charges"]
                            },
                            "persona": "high_utilization",
                            "confidence": 0.95
                        }
                    ],
                    "disclaimer": DISCLAIMER
                }
            ]
        }
    }

