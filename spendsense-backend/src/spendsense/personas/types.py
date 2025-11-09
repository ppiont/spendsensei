"""
Persona Type Definitions

Defines the persona types, priority order, and confidence scores.
"""

# Persona priority order (most urgent/important first)
PERSONA_PRIORITY = [
    "high_utilization",    # Most urgent: >70% utilization OR overdue OR min-payment-only
    "variable_income",     # Cash flow risk: irregular income + low buffer
    "debt_consolidator",   # Opportunity: multiple cards with moderate utilization
    "subscription_heavy",  # Cost optimization: high recurring spend
    "savings_builder",     # Building wealth: positive savings trajectory
    "balanced"             # Default fallback
]

# Confidence scores for each persona type
CONFIDENCE_SCORES = {
    "high_utilization": 0.95,
    "variable_income": 0.90,
    "debt_consolidator": 0.88,
    "subscription_heavy": 0.85,
    "savings_builder": 0.80,
    "balanced": 0.60
}
