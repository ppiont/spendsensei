"""
Personas Module - Financial Persona Assignment

This module provides persona assignment logic based on behavioral signals.
Personas help categorize users for personalized recommendations.

Main entry point: assign_persona() assigns a persona to a user.
"""

from spendsense.personas.types import PERSONA_PRIORITY, CONFIDENCE_SCORES
from spendsense.personas.assignment import (
    assign_persona,
    calculate_high_utilization_confidence,
    calculate_variable_income_confidence,
    calculate_subscription_heavy_confidence,
    calculate_savings_builder_confidence,
    calculate_debt_consolidator_confidence,
)

__all__ = [
    "PERSONA_PRIORITY",
    "CONFIDENCE_SCORES",
    "assign_persona",
    "calculate_high_utilization_confidence",
    "calculate_variable_income_confidence",
    "calculate_subscription_heavy_confidence",
    "calculate_savings_builder_confidence",
    "calculate_debt_consolidator_confidence",
]
