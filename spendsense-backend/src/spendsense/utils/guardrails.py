"""Guardrails for ethical and appropriate recommendation generation.

This module enforces content standards including:
- Tone checking to prevent shaming language
- User consent verification
- Standard disclaimer for all recommendations
"""

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)


# Patterns that indicate shaming or judgmental language
SHAME_PATTERNS = [
    r"\byou'?re\s+overspending\b",
    r"\bbad\s+financial\s+habits?\b",
    r"\birresponsible\b",
    r"\bcareless\b",
    r"\bwasting\s+money\b",
    r"\bpoor\s+choices?\b",
    r"\bfinancial\s+mistakes?\b",
    r"\bbad\s+decisions?\b",
    r"\bfoolish\b",
    r"\bstupid\b",
    r"\breckless\b",
]


# Standard disclaimer for all recommendations
DISCLAIMER = (
    "This content is for educational purposes only and does not constitute "
    "financial advice. Please consult with a qualified financial professional "
    "before making financial decisions."
)


def check_tone(text: str) -> Tuple[bool, List[str]]:
    """Check if text contains shaming or judgmental language.

    Args:
        text: Text to check for tone violations

    Returns:
        Tuple of (is_valid, violations) where:
        - is_valid: True if text passes tone check, False otherwise
        - violations: List of matched shame patterns (empty if valid)

    Examples:
        >>> check_tone("You have high spending patterns")
        (True, [])

        >>> check_tone("You're overspending on subscriptions")
        (False, ["you're overspending"])
    """
    if not text:
        return True, []

    violations = []
    text_lower = text.lower()

    for pattern in SHAME_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            violations.append(match.group())

    if violations:
        logger.warning(
            f"Tone violation detected: {len(violations)} shame patterns found in text: {violations}"
        )
        return False, violations

    return True, []


def check_consent(user_consent: bool) -> bool:
    """Check if user has provided consent for data processing.

    Args:
        user_consent: User's consent status from database

    Returns:
        True if user has consented, False otherwise

    Examples:
        >>> check_consent(True)
        True

        >>> check_consent(False)
        False

        >>> check_consent(None)
        False
    """
    if user_consent is None:
        logger.warning("User consent is None, treating as False")
        return False

    if not user_consent:
        logger.info("User has not provided consent for recommendations")
        return False

    return True
