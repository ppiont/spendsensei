"""
Consent Verification Guardrails

Ensures user consent is obtained before processing data.
"""

import logging

logger = logging.getLogger(__name__)


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
