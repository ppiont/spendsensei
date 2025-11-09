"""
Guardrails Module - Content Safety and Compliance

This module enforces ethical and compliance standards including:
- Tone checking (no shaming language)
- User consent verification
- Standard disclaimers
- Eligibility verification
"""

from spendsense.guardrails.tone import SHAME_PATTERNS, check_tone
from spendsense.guardrails.consent import check_consent
from spendsense.guardrails.disclosure import DISCLAIMER
from spendsense.guardrails.eligibility import (
    check_income_requirement,
    has_existing_account,
    is_predatory_product,
    check_eligibility,
)

__all__ = [
    # Tone
    "SHAME_PATTERNS",
    "check_tone",
    # Consent
    "check_consent",
    # Disclosure
    "DISCLAIMER",
    # Eligibility
    "check_income_requirement",
    "has_existing_account",
    "is_predatory_product",
    "check_eligibility",
]
