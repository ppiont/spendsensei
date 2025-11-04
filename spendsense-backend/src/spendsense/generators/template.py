"""
Template-Based Content Generator

This module implements template-based content generation using a YAML catalog
and relevance scoring. It provides explainable, deterministic content selection
without requiring AI API calls.
"""

import os
import yaml
import logging
from typing import List, Dict, Any
from pathlib import Path

from spendsense.generators.base import ContentGenerator, EducationItem, Rationale
from spendsense.services.features import BehaviorSignals
from spendsense.utils.guardrails import check_tone

# Set up logging
logger = logging.getLogger(__name__)

# Default path to content catalog (relative to project root)
DEFAULT_CATALOG_PATH = "data/content_catalog.yaml"


class TemplateGenerator(ContentGenerator):
    """
    Template-based implementation of ContentGenerator.

    Loads curated content from YAML catalog, scores items by signal relevance,
    and generates explainable rationales using template strings.
    """

    def __init__(self, catalog_path: str = None):
        """
        Initialize TemplateGenerator with content catalog.

        Args:
            catalog_path: Path to content_catalog.yaml file. If None, uses default path
                         relative to the spendsense-backend directory.
        """
        if catalog_path is None:
            # Default to data/content_catalog.yaml relative to spendsense-backend root
            backend_root = Path(__file__).parent.parent.parent.parent
            catalog_path = backend_root / DEFAULT_CATALOG_PATH

        self.catalog_path = Path(catalog_path)
        self._catalog_cache = None
        logger.info(f"Initialized TemplateGenerator with catalog: {self.catalog_path}")

    def _load_catalog(self) -> Dict[str, Any]:
        """
        Load content catalog from YAML file.

        Uses caching to avoid reloading on every call.

        Returns:
            Dictionary containing 'education' list with content items

        Raises:
            FileNotFoundError: If catalog file doesn't exist
            yaml.YAMLError: If catalog file is invalid YAML
        """
        if self._catalog_cache is not None:
            return self._catalog_cache

        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Content catalog not found: {self.catalog_path}")

        logger.info(f"Loading content catalog from {self.catalog_path}")

        with open(self.catalog_path, 'r') as f:
            catalog = yaml.safe_load(f)

        self._catalog_cache = catalog
        logger.info(f"Loaded {len(catalog.get('education', []))} education items from catalog")

        return catalog

    def _extract_signal_tags(self, signals: BehaviorSignals) -> List[str]:
        """
        Extract active signal tags from BehaviorSignals object.

        Analyzes the signals to determine which specific conditions are met
        and returns corresponding signal tags (e.g., 'high_utilization_80').

        Args:
            signals: BehaviorSignals object with computed user data

        Returns:
            List of active signal tag strings
        """
        tags = []

        # Credit utilization tags
        if signals.credit:
            utilization = signals.credit.get("overall_utilization", 0.0)
            if utilization >= 80.0:
                tags.append("high_utilization_80")
            elif utilization >= 50.0:
                tags.append("high_utilization_50")
            elif utilization >= 30.0:
                tags.append("moderate_utilization_30")

            # Credit flags
            flags = signals.credit.get("flags", [])
            if "interest_charges" in flags:
                tags.append("interest_charges")
            if "overdue" in flags:
                tags.append("overdue")

        # Subscription tags
        if signals.subscriptions:
            count = signals.subscriptions.get("count", 0)
            if count >= 3:
                tags.append("subscription_heavy")

        # Income tags
        if signals.income:
            median_gap = signals.income.get("median_gap_days", 0)
            if median_gap > 45:
                tags.append("variable_income")

            stability = signals.income.get("stability", "unknown")
            if stability == "stable":
                tags.append("stable_income")

        # Savings tags
        if signals.savings:
            monthly_inflow = signals.savings.get("monthly_inflow", 0)
            if monthly_inflow > 0:
                tags.append("positive_savings")

            buffer_months = signals.savings.get("buffer_months", 0.0)
            if buffer_months < 3.0:
                tags.append("low_emergency_fund")

        logger.debug(f"Extracted signal tags: {tags}")
        return tags

    def _calculate_relevance(
        self,
        content_item: Dict[str, Any],
        persona_type: str,
        signal_tags: List[str]
    ) -> float:
        """
        Calculate relevance score for a content item.

        Scoring algorithm:
        1. Base score = 0.5 if persona matches
        2. +0.1 for each matching signal tag (max +0.5)
        3. Final score capped at 1.0

        Args:
            content_item: Dictionary from content catalog with persona_tags and signal_tags
            persona_type: User's assigned persona
            signal_tags: List of active signal tags for the user

        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0

        # Check persona match
        content_personas = content_item.get("persona_tags", [])
        if persona_type in content_personas:
            score += 0.5

        # Check signal tag matches
        content_signals = content_item.get("signal_tags", [])
        matching_signals = set(signal_tags) & set(content_signals)
        signal_bonus = len(matching_signals) * 0.1
        score += min(signal_bonus, 0.5)  # Cap signal bonus at 0.5

        # Cap total score at 1.0
        score = min(score, 1.0)

        logger.debug(
            f"Relevance score for '{content_item.get('id')}': {score:.2f} "
            f"(persona_match: {persona_type in content_personas}, "
            f"signal_matches: {len(matching_signals)})"
        )

        return score

    async def generate_education(
        self,
        persona_type: str,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> List[EducationItem]:
        """
        Generate personalized educational content items.

        Implementation steps:
        1. Load content catalog from YAML
        2. Extract active signal tags from user signals
        3. Calculate relevance score for each content item
        4. Filter items with score > 0
        5. Sort by relevance (highest first)
        6. Return top N items

        Args:
            persona_type: User's assigned persona (e.g., 'high_utilization')
            signals: BehaviorSignals object with computed user data
            limit: Maximum number of education items to return (default: 3)

        Returns:
            List of EducationItem objects, sorted by relevance (highest first)

        Raises:
            ValueError: If persona_type is invalid or signals are missing
            FileNotFoundError: If content catalog is not found
        """
        logger.info(f"Generating education content for persona '{persona_type}', limit={limit}")

        # Validate inputs
        if not persona_type:
            raise ValueError("persona_type is required")
        if signals is None:
            raise ValueError("signals are required")

        # Load catalog
        catalog = self._load_catalog()
        education_items = catalog.get("education", [])

        if not education_items:
            logger.warning("No education items found in catalog")
            return []

        # Extract active signal tags
        signal_tags = self._extract_signal_tags(signals)

        # Score and filter content items
        scored_items = []
        for item in education_items:
            score = self._calculate_relevance(item, persona_type, signal_tags)
            if score > 0:
                scored_items.append((score, item))

        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x[0], reverse=True)

        # Convert to EducationItem objects (top N)
        result = []
        for score, item in scored_items[:limit]:
            education_item = EducationItem(
                id=item["id"],
                title=item["title"],
                summary=item["summary"],
                body=item["body"],
                cta=item["cta"],
                source=item["source"],
                relevance_score=score
            )
            result.append(education_item)

        logger.info(f"Generated {len(result)} education items (scores: {[item.relevance_score for item in result]})")
        return result

    async def generate_rationale(
        self,
        persona_type: str,
        confidence: float,
        signals: BehaviorSignals
    ) -> Rationale:
        """
        Generate explainable rationale for persona assignment.

        Creates human-readable explanations with concrete data points from
        the user's behavioral signals.

        Template strings by persona:
        - high_utilization: Credit utilization and interest data
        - variable_income: Income frequency and buffer data
        - subscription_heavy: Subscription count and spending data
        - savings_builder: Savings growth and credit health data
        - balanced: General financial health indicators

        Args:
            persona_type: User's assigned persona
            confidence: Confidence score for the assignment (0.0-1.0)
            signals: BehaviorSignals object with computed user data

        Returns:
            Rationale object with explanation and key signals

        Raises:
            ValueError: If persona_type is invalid or signals are missing
        """
        logger.info(f"Generating rationale for persona '{persona_type}' with confidence {confidence}")

        # Validate inputs
        if not persona_type:
            raise ValueError("persona_type is required")
        if signals is None:
            raise ValueError("signals are required")

        # Extract active signal tags
        signal_tags = self._extract_signal_tags(signals)

        # Generate explanation based on persona type
        explanation = self._generate_explanation(persona_type, signals, signal_tags)

        # Apply tone checking guardrail - BLOCK on violations
        is_valid, violations = check_tone(explanation)
        if not is_valid:
            error_msg = (
                f"Tone guardrail violation: Content contains inappropriate language. "
                f"Found {len(violations)} violations: {violations}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        rationale = Rationale(
            persona_type=persona_type,
            confidence=confidence,
            explanation=explanation,
            key_signals=signal_tags
        )

        logger.info(f"Generated rationale: {len(explanation)} chars, {len(signal_tags)} signals")
        return rationale

    def _generate_explanation(
        self,
        persona_type: str,
        signals: BehaviorSignals,
        signal_tags: List[str]
    ) -> str:
        """
        Generate persona-specific explanation text with concrete data points.

        Args:
            persona_type: User's assigned persona
            signals: BehaviorSignals object
            signal_tags: List of active signal tags

        Returns:
            Human-readable explanation string with concrete data
        """
        if persona_type == "high_utilization":
            credit = signals.credit or {}
            utilization = credit.get("overall_utilization", 0.0)
            total_balance = credit.get("total_balance", 0) / 100  # Convert cents to dollars
            total_limit = credit.get("total_limit", 0) / 100

            explanation = (
                f"You've been identified as a High Utilization user because your credit card "
                f"utilization is {utilization:.1f}%, which is above the recommended 30% threshold. "
                f"You're currently using ${total_balance:,.2f} of your ${total_limit:,.2f} total credit limit. "
            )

            flags = credit.get("flags", [])
            if "interest_charges" in flags:
                explanation += "You're also paying interest charges on your balances, which adds to the cost of carrying debt. "
            if "overdue" in flags:
                explanation += "Additionally, you have overdue payments, which can negatively impact your credit score. "

            explanation += (
                "High credit utilization can hurt your credit score and lead to higher interest costs. "
                "We recommend focusing on paying down high balances and keeping utilization below 30%."
            )

        elif persona_type == "variable_income":
            income = signals.income or {}
            median_gap = income.get("median_gap_days", 0)
            buffer_months = income.get("buffer_months", 0.0)
            avg_amount = income.get("average_amount", 0) / 100

            explanation = (
                f"You've been identified as a Variable Income user because your income arrives irregularly, "
                f"with a median gap of {median_gap} days between payments. Your average income payment is "
                f"${avg_amount:,.2f}, and you currently have {buffer_months:.1f} months of cash flow buffer. "
                f"Variable income requires special budgeting strategies and a larger emergency fund. "
                f"We recommend building your buffer to at least 6-12 months of expenses and using "
                f"percentage-based budgeting rather than fixed amounts."
            )

        elif persona_type == "subscription_heavy":
            subscriptions = signals.subscriptions or {}
            count = subscriptions.get("count", 0)
            monthly_spend = subscriptions.get("monthly_recurring_spend", 0) / 100
            percentage = subscriptions.get("percentage_of_spending", 0.0)

            explanation = (
                f"You've been identified as a Subscription Heavy user because you have {count} active "
                f"recurring subscriptions totaling ${monthly_spend:,.2f} per month. This represents "
                f"{percentage:.1f}% of your total spending. While some subscriptions provide value, "
                f"it's easy for unused subscriptions to accumulate. We recommend conducting a subscription "
                f"audit to identify services you rarely use and canceling or downgrading them to save money."
            )

        elif persona_type == "savings_builder":
            savings = signals.savings or {}
            growth_rate = savings.get("growth_rate", 0.0)
            monthly_inflow = savings.get("monthly_inflow", 0) / 100
            credit = signals.credit or {}
            utilization = credit.get("overall_utilization", 0.0)

            explanation = (
                f"You've been identified as a Savings Builder because you're making consistent progress "
                f"toward your financial goals. Your savings are growing at {growth_rate:.1f}% with an average "
                f"monthly inflow of ${monthly_inflow:,.2f}. Your credit utilization is {utilization:.1f}%, "
                f"which is in a healthy range. Keep up the great work! We recommend focusing on building your "
                f"emergency fund, automating your savings, and optimizing your investment strategy."
            )

        else:  # balanced
            explanation = (
                f"You've been identified as a Balanced user, which means you're generally maintaining "
                f"healthy financial habits without critical issues requiring immediate attention. "
            )

            # Add specific insights based on available signals
            insights = []

            if signals.credit:
                utilization = signals.credit.get("overall_utilization", 0.0)
                if utilization < 30:
                    insights.append(f"your credit utilization of {utilization:.1f}% is in a healthy range")

            if signals.income:
                stability = signals.income.get("stability", "unknown")
                if stability == "stable":
                    insights.append("you have stable, regular income")

            if signals.savings:
                monthly_inflow = signals.savings.get("monthly_inflow", 0)
                if monthly_inflow > 0:
                    insights.append(f"you're saving consistently with ${monthly_inflow/100:,.2f} monthly inflow")

            if insights:
                explanation += "Specifically, " + ", and ".join(insights) + ". "

            explanation += (
                "Continue monitoring your financial wellness and consider setting specific goals "
                "to optimize your savings, reduce debt, or build wealth."
            )

        return explanation
