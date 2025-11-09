"""
Template-Based Content Generator

This module implements template-based content generation using a YAML catalog
and relevance scoring. It provides explainable, deterministic content selection
without requiring AI API calls.
"""

import yaml
import logging
from typing import List, Dict, Any
from pathlib import Path

from spendsense.recommend.types import ContentGenerator, EducationItem, Rationale, PartnerOffer, EligibilityRules
from spendsense.features import BehaviorSignals
from spendsense.guardrails import check_tone

# Set up logging
logger = logging.getLogger(__name__)

# Default paths to catalogs (relative to project root)
DEFAULT_CATALOG_PATH = "data/content_catalog.yaml"
DEFAULT_OFFERS_CATALOG_PATH = "data/partner_offers_catalog.yaml"


class TemplateGenerator(ContentGenerator):
    """
    Template-based implementation of ContentGenerator.

    Loads curated content from YAML catalog, scores items by signal relevance,
    and generates explainable rationales using template strings.
    """

    def __init__(self, catalog_path: str = None, offers_catalog_path: str = None):
        """
        Initialize TemplateGenerator with content and partner offers catalogs.

        Args:
            catalog_path: Path to content_catalog.yaml file. If None, uses default path
                         relative to the spendsense-backend directory.
            offers_catalog_path: Path to partner_offers_catalog.yaml file. If None, uses default path.
        """
        backend_root = Path(__file__).parent.parent.parent.parent

        if catalog_path is None:
            catalog_path = backend_root / DEFAULT_CATALOG_PATH

        if offers_catalog_path is None:
            offers_catalog_path = backend_root / DEFAULT_OFFERS_CATALOG_PATH

        self.catalog_path = Path(catalog_path)
        self.offers_catalog_path = Path(offers_catalog_path)
        self._catalog_cache = None
        self._offers_catalog_cache = None
        logger.info(f"Initialized TemplateGenerator with catalog: {self.catalog_path}, offers: {self.offers_catalog_path}")

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

    def _convert_to_1_to_5_scale(self, match_score: float) -> int:
        """
        Convert 0-1 match score to 1-5 relevance scale.

        Scale mapping:
        - 1 = Poor match (0.0-0.2)
        - 2 = Fair match (0.2-0.4)
        - 3 = Good match (0.4-0.6)
        - 4 = Very good match (0.6-0.8)
        - 5 = Excellent match (0.8-1.0)

        Args:
            match_score: Raw relevance score between 0.0 and 1.0

        Returns:
            Integer score between 1 and 5
        """
        if match_score < 0.2:
            return 1
        elif match_score < 0.4:
            return 2
        elif match_score < 0.6:
            return 3
        elif match_score < 0.8:
            return 4
        else:
            return 5

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
                relevance_score=self._convert_to_1_to_5_scale(score)
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

    async def generate_content_rationale(
        self,
        content_item: EducationItem,
        persona_type: str,
        confidence: float,
        signals: BehaviorSignals
    ) -> Rationale:
        """
        Generate explainable rationale specific to a content item.

        Creates a rationale that explains why THIS SPECIFIC content is relevant
        to the user's situation, referencing concrete behavioral signals.

        Args:
            content_item: The education item being recommended
            persona_type: User's assigned persona
            confidence: Confidence score for persona assignment (0.0-1.0)
            signals: BehaviorSignals object with computed user data

        Returns:
            Rationale object with content-specific explanation

        Raises:
            ValueError: If inputs are invalid or missing
        """
        logger.info(f"Generating content-specific rationale for '{content_item.title}'")

        # Validate inputs
        if not content_item:
            raise ValueError("content_item is required")
        if not persona_type:
            raise ValueError("persona_type is required")
        if signals is None:
            raise ValueError("signals are required")

        # Extract active signal tags
        signal_tags = self._extract_signal_tags(signals)

        # Generate content-specific explanation
        explanation = self._generate_content_explanation(
            content_item=content_item,
            persona_type=persona_type,
            signals=signals,
            signal_tags=signal_tags
        )

        # Apply tone checking guardrail
        is_valid, violations = check_tone(explanation)
        if not is_valid:
            error_msg = (
                f"Tone guardrail violation in content rationale: "
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

        logger.info(f"Generated content-specific rationale: {len(explanation)} chars")
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
                "You've been identified as a Balanced user, which means you're generally maintaining "
                "healthy financial habits without critical issues requiring immediate attention. "
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

    def _generate_content_explanation(
        self,
        content_item: EducationItem,
        persona_type: str,
        signals: BehaviorSignals,
        signal_tags: List[str]
    ) -> str:
        """
        Generate content-specific explanation with concrete data points.

        Creates an explanation that references the specific content being recommended
        and explains why it's relevant based on the user's behavioral signals.

        Args:
            content_item: The education item being recommended
            persona_type: User's assigned persona
            signals: BehaviorSignals object
            signal_tags: List of active signal tags

        Returns:
            Human-readable explanation string with content-specific context
        """
        # Generate concise, data-driven explanation
        if persona_type == "high_utilization" and signals.credit:
            utilization = signals.credit.get("overall_utilization", 0.0)
            total_balance = signals.credit.get("total_balance", 0) / 100
            explanation = (
                f"Your credit utilization is {utilization:.1f}% with ${total_balance:,.0f} in balances"
            )
            if "interest_charges" in signal_tags:
                explanation += ", and you're paying interest charges"
            explanation += "."

        elif persona_type == "subscription_heavy" and signals.subscriptions:
            count = signals.subscriptions.get("count", 0)
            monthly_spend = signals.subscriptions.get("monthly_recurring_spend", 0) / 100
            explanation = (
                f"You have {count} recurring subscriptions totaling ${monthly_spend:,.0f}/month."
            )

        elif persona_type == "variable_income" and signals.income:
            median_gap = signals.income.get("median_gap_days", 0)
            buffer_months = signals.income.get("buffer_months", 0.0)
            explanation = (
                f"Your income arrives every {median_gap} days with {buffer_months:.1f} months buffer."
            )

        elif persona_type == "savings_builder" and signals.savings:
            monthly_inflow = signals.savings.get("monthly_inflow", 0) / 100
            growth_rate = signals.savings.get("growth_rate", 0.0)
            explanation = (
                f"You're saving ${monthly_inflow:,.0f}/month with {growth_rate:.1f}% growth."
            )

        elif persona_type == "debt_consolidator" and signals.credit:
            utilization = signals.credit.get("overall_utilization", 0.0)
            explanation = (
                f"You're managing multiple cards at {utilization:.1f}% utilization."
            )

        else:  # balanced or fallback
            explanation = "This matches your current financial profile."

        return explanation

    def _load_offers_catalog(self) -> Dict[str, Any]:
        """
        Load partner offers catalog from YAML file.

        Uses caching to avoid reloading on every call.

        Returns:
            Dictionary containing 'partner_offers' list with offer items

        Raises:
            FileNotFoundError: If offers catalog file doesn't exist
            yaml.YAMLError: If catalog file is invalid YAML
        """
        if self._offers_catalog_cache is not None:
            return self._offers_catalog_cache

        if not self.offers_catalog_path.exists():
            raise FileNotFoundError(f"Partner offers catalog not found: {self.offers_catalog_path}")

        logger.info(f"Loading partner offers catalog from {self.offers_catalog_path}")

        with open(self.offers_catalog_path, 'r') as f:
            catalog = yaml.safe_load(f)

        self._offers_catalog_cache = catalog
        logger.info(f"Loaded {len(catalog.get('partner_offers', []))} partner offers from catalog")

        return catalog

    def _estimate_credit_score(self, utilization: float) -> int:
        """
        Estimate credit score based on credit utilization percentage.

        This is a simplified estimation for eligibility checking purposes.
        In a real system, you would use actual credit scores from credit bureaus.

        Credit utilization accounts for ~30% of FICO score. This method provides
        a rough estimate based on typical score ranges:
        - 0-10% utilization: 740-850 (Excellent)
        - 10-30% utilization: 670-739 (Good)
        - 30-50% utilization: 580-669 (Fair)
        - 50-75% utilization: 500-579 (Poor)
        - 75%+ utilization: 300-499 (Very Poor)

        Args:
            utilization: Credit utilization percentage (0.0-100.0)

        Returns:
            Estimated credit score (300-850)
        """
        if utilization <= 10.0:
            # Excellent: 740-850
            return int(850 - (utilization * 11))  # 850 at 0%, 740 at 10%
        elif utilization <= 30.0:
            # Good: 670-739
            return int(739 - ((utilization - 10.0) * 3.45))  # 739 at 10%, 670 at 30%
        elif utilization <= 50.0:
            # Fair: 580-669
            return int(669 - ((utilization - 30.0) * 4.45))  # 669 at 30%, 580 at 50%
        elif utilization <= 75.0:
            # Poor: 500-579
            return int(579 - ((utilization - 50.0) * 3.16))  # 579 at 50%, 500 at 75%
        else:
            # Very Poor: 300-499
            return int(max(300, 500 - ((utilization - 75.0) * 8)))  # 500 at 75%, 300 at 100%

    def _check_eligibility(
        self,
        offer_data: Dict[str, Any],
        signals: BehaviorSignals,
        accounts: List,
        signal_tags: List[str]
    ) -> bool:
        """
        Check if user meets eligibility requirements for an offer.

        All eligibility rules are combined with AND logic - user must meet
        ALL specified criteria to be eligible.

        Args:
            offer_data: Dictionary containing offer data from catalog
            signals: BehaviorSignals object with computed user data
            accounts: List of user's Account objects
            signal_tags: List of active signal tags

        Returns:
            True if user meets all eligibility criteria, False otherwise
        """
        rules = offer_data.get("eligibility_rules", {})

        # Check credit utilization requirements
        if signals.credit:
            utilization = signals.credit.get("overall_utilization", 0.0)

            if "min_credit_utilization" in rules:
                if utilization < rules["min_credit_utilization"]:
                    return False

            if "max_credit_utilization" in rules:
                if utilization > rules["max_credit_utilization"]:
                    return False

            # Check credit score estimate
            estimated_score = self._estimate_credit_score(utilization)

            if "min_credit_score_estimate" in rules:
                if estimated_score < rules["min_credit_score_estimate"]:
                    return False

            if "max_credit_score_estimate" in rules:
                if estimated_score > rules["max_credit_score_estimate"]:
                    return False

        # Check income requirements
        if "min_monthly_income" in rules and signals.income:
            avg_income = signals.income.get("average_income", 0)  # Already in cents
            # Estimate monthly income from average (assume biweekly or monthly frequency)
            monthly_income = avg_income * 2  # Conservative estimate (assume biweekly)
            if monthly_income < rules["min_monthly_income"]:
                return False

        # Check account type requirements
        if "required_account_types" in rules and rules["required_account_types"]:
            account_types = {acc.type for acc in accounts}
            for required_type in rules["required_account_types"]:
                if required_type not in account_types:
                    return False

        # Check excluded account subtypes
        if "excluded_account_subtypes" in rules and rules["excluded_account_subtypes"]:
            account_subtypes = {acc.subtype for acc in accounts}
            for excluded_subtype in rules["excluded_account_subtypes"]:
                if excluded_subtype in account_subtypes:
                    return False

        # Check required signals (AND logic - all must be present)
        if "required_signals" in rules and rules["required_signals"]:
            for required_signal in rules["required_signals"]:
                if required_signal not in signal_tags:
                    return False

        # Check excluded signals (any match disqualifies)
        if "excluded_signals" in rules and rules["excluded_signals"]:
            for excluded_signal in rules["excluded_signals"]:
                if excluded_signal in signal_tags:
                    return False

        # Check emergency fund requirements
        if signals.savings:
            emergency_months = signals.savings.get("emergency_fund_months", 0.0)

            if "min_emergency_fund_months" in rules:
                if emergency_months < rules["min_emergency_fund_months"]:
                    return False

            if "max_emergency_fund_months" in rules:
                if emergency_months > rules["max_emergency_fund_months"]:
                    return False

        # All checks passed
        return True

    async def generate_offers(
        self,
        persona_type: str,
        signals: BehaviorSignals,
        accounts: List,
        limit: int = 3
    ) -> List[PartnerOffer]:
        """
        Generate personalized partner offers with eligibility checking.

        Filters offers by persona relevance, checks eligibility requirements,
        scores by relevance, and returns top N eligible offers.

        Args:
            persona_type: User's assigned persona (e.g., 'high_utilization')
            signals: BehaviorSignals object with computed user data
            accounts: List of user's Account objects for eligibility checking
            limit: Maximum number of offers to return (default: 3)

        Returns:
            List of PartnerOffer objects with eligibility_met=True,
            sorted by relevance (highest first)

        Raises:
            ValueError: If persona_type is invalid or required data missing
        """
        logger.info(f"Generating up to {limit} partner offers for persona: {persona_type}")

        # Load partner offers catalog
        catalog = self._load_offers_catalog()
        all_offers = catalog.get("partner_offers", [])

        if not all_offers:
            logger.warning("No partner offers found in catalog")
            return []

        # Extract signal tags for eligibility checking
        signal_tags = self._extract_signal_tags(signals)

        # Filter and score offers
        scored_offers = []

        for offer_data in all_offers:
            # Check if offer is relevant to persona
            persona_tags = offer_data.get("persona_tags", [])
            if persona_type not in persona_tags:
                continue

            # Check eligibility
            is_eligible = self._check_eligibility(offer_data, signals, accounts, signal_tags)
            if not is_eligible:
                logger.debug(f"Offer {offer_data['id']} not eligible for user")
                continue

            # Calculate relevance score (similar to education content)
            raw_score = self._calculate_relevance(offer_data, persona_type, signal_tags)

            # Create PartnerOffer object
            partner_offer = PartnerOffer(
                id=offer_data["id"],
                title=offer_data["title"],
                provider=offer_data["provider"],
                offer_type=offer_data["offer_type"],
                summary=offer_data["summary"],
                benefits=offer_data["benefits"],
                eligibility_explanation=offer_data["eligibility_explanation"],
                cta=offer_data["cta"],
                cta_url=offer_data["cta_url"],
                disclaimer=offer_data["disclaimer"],
                relevance_score=self._convert_to_1_to_5_scale(raw_score),
                eligibility_met=True
            )

            scored_offers.append((raw_score, partner_offer))

        # Sort by relevance score (highest first)
        scored_offers.sort(reverse=True, key=lambda x: x[0])

        # Return top N offers
        top_offers = [offer for score, offer in scored_offers[:limit]]

        logger.info(f"Generated {len(top_offers)} eligible partner offers from {len(all_offers)} total offers")

        return top_offers
