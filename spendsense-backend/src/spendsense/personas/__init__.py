"""
Personas Module - Financial Persona Assignment

This module provides persona assignment logic based on behavioral signals.
Personas help categorize users for personalized recommendations.

Main entry point: assign_persona() assigns a persona to a user.
"""

from spendsense.personas.types import PERSONA_PRIORITY, CONFIDENCE_SCORES
from spendsense.personas.assignment import (
    assign_persona,
    matches_high_utilization,
    matches_variable_income,
    matches_subscription_heavy,
    matches_savings_builder,
    matches_debt_consolidator,
)

__all__ = [
    "PERSONA_PRIORITY",
    "CONFIDENCE_SCORES",
    "assign_persona",
    "matches_high_utilization",
    "matches_variable_income",
    "matches_subscription_heavy",
    "matches_savings_builder",
    "matches_debt_consolidator",
]
