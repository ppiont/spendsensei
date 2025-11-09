"""
Features Module - Behavioral Signal Detection

This module provides comprehensive behavioral signal detection including:
- Income stability analysis
- Savings patterns and emergency fund coverage
- Credit utilization and risk patterns
- Subscription detection

Main entry point: compute_signals() orchestrates all signal detection.
"""

from spendsense.features.types import BehaviorSignals
from spendsense.features.signals import compute_signals
from spendsense.features.income import analyze_income
from spendsense.features.savings import analyze_savings
from spendsense.features.credit import analyze_credit
from spendsense.features.subscriptions import detect_subscriptions

__all__ = [
    "BehaviorSignals",
    "compute_signals",
    "analyze_income",
    "analyze_savings",
    "analyze_credit",
    "detect_subscriptions",
]
