"""
Behavioral Signal Types

Defines the data structures for behavioral signals.
"""

from dataclasses import dataclass


@dataclass
class BehaviorSignals:
    """
    Container for all computed behavioral signals for a user.

    Each field contains a dictionary with signal-specific data structure.
    Fields are initialized as empty dicts and populated by analysis functions.
    """
    subscriptions: dict = None  # Subscription detection
    savings: dict = None        # Savings analysis
    credit: dict = None         # Credit utilization
    income: dict = None         # Income stability

    def __post_init__(self):
        """Initialize all fields as empty dicts if None"""
        if self.subscriptions is None:
            self.subscriptions = {}
        if self.savings is None:
            self.savings = {}
        if self.credit is None:
            self.credit = {}
        if self.income is None:
            self.income = {}
