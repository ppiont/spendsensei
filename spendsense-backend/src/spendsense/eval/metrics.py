"""
Evaluation Metrics Module

Calculates and aggregates metrics for system evaluation:
- Coverage: % users with persona + >=3 signal categories
- Explainability: % recommendations with rationales and key signals
- Latency: Average and percentile recommendation generation times
- Auditability: % recommendations with complete decision traces
- Relevance: Average relevance scores (1-5 scale)
- Fairness: Persona distribution analysis
"""

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class EvaluationMetrics:
    """Container for all evaluation metrics."""

    # Totals
    total_users: int = 0
    total_recommendations: int = 0

    # Coverage metrics
    users_with_persona: int = 0
    users_with_min_signals: int = 0  # >=3 signal categories

    # Explainability metrics
    recs_with_explanation: int = 0
    recs_with_signals: int = 0

    # Latency metrics (in seconds)
    latencies: List[float] = field(default_factory=list)

    # Auditability metrics
    recs_with_complete_trace: int = 0

    # Relevance metrics (1-5 scale)
    relevance_scores: List[int] = field(default_factory=list)

    # Persona distribution
    persona_counts: Dict[str, int] = field(default_factory=dict)

    # Signal counts per user
    signal_counts: List[int] = field(default_factory=list)

    # Errors
    error_count: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def calculate_coverage(self) -> float:
        """
        Calculate coverage percentage.

        Coverage = users who have BOTH:
        - An assigned persona
        - >= 3 active signal categories
        """
        if self.total_users == 0:
            return 0.0
        # User must have BOTH persona AND >=3 signals
        users_with_full_coverage = min(self.users_with_persona, self.users_with_min_signals)
        return (users_with_full_coverage / self.total_users) * 100

    def calculate_explainability(self) -> float:
        """
        Calculate explainability percentage.

        Explainability = recommendations with BOTH:
        - Non-empty explanation text
        - Non-empty key_signals list
        """
        if self.total_recommendations == 0:
            return 0.0
        # Recommendation must have BOTH explanation AND key_signals
        recs_fully_explained = min(self.recs_with_explanation, self.recs_with_signals)
        return (recs_fully_explained / self.total_recommendations) * 100

    def calculate_latency_stats(self) -> Dict[str, float]:
        """
        Calculate latency statistics.

        Returns:
            Dictionary with avg, min, max, p50, p95, p99
        """
        if not self.latencies:
            return {
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        return {
            "avg": statistics.mean(sorted_latencies),
            "min": sorted_latencies[0],
            "max": sorted_latencies[-1],
            "p50": statistics.median(sorted_latencies),
            "p95": sorted_latencies[int(n * 0.95)] if n >= 20 else sorted_latencies[-1],
            "p99": sorted_latencies[int(n * 0.99)] if n >= 100 else sorted_latencies[-1],
        }

    def calculate_auditability(self) -> float:
        """
        Calculate auditability percentage.

        Auditability = recommendations with complete decision trace:
        - persona assigned
        - confidence score
        - explanation text
        - key_signals
        - content/offer id
        """
        if self.total_recommendations == 0:
            return 0.0
        return (self.recs_with_complete_trace / self.total_recommendations) * 100

    def calculate_relevance_stats(self) -> Dict[str, float]:
        """
        Calculate relevance score statistics.

        Returns:
            Dictionary with avg, min, max, distribution by score
        """
        if not self.relevance_scores:
            return {
                "avg": 0.0,
                "min": 0,
                "max": 0,
                "distribution": {},
            }

        distribution = {}
        for score in range(1, 6):
            count = sum(1 for s in self.relevance_scores if s == score)
            distribution[str(score)] = count

        return {
            "avg": statistics.mean(self.relevance_scores),
            "min": min(self.relevance_scores),
            "max": max(self.relevance_scores),
            "distribution": distribution,
        }

    def calculate_fairness(self) -> Dict[str, Any]:
        """
        Calculate fairness metrics based on persona distribution.

        Fairness analysis checks:
        - No single persona dominates (>50% of users)
        - All personas have some representation (except balanced as fallback)
        - Distribution entropy (higher = more fair)
        """
        if self.total_users == 0:
            return {
                "is_fair": False,
                "max_persona_percentage": 0.0,
                "entropy": 0.0,
                "underrepresented": [],
                "analysis": "No users to analyze",
            }

        # Calculate percentages
        percentages = {}
        for persona, count in self.persona_counts.items():
            percentages[persona] = (count / self.total_users) * 100

        max_pct = max(percentages.values()) if percentages else 0.0

        # Check for underrepresented personas (excluding balanced)
        expected_personas = {
            "high_utilization", "variable_income", "subscription_heavy",
            "savings_builder", "debt_consolidator"
        }
        underrepresented = [
            p for p in expected_personas
            if p not in self.persona_counts or self.persona_counts[p] == 0
        ]

        # Calculate entropy (measure of distribution evenness)
        import math
        entropy = 0.0
        for count in self.persona_counts.values():
            if count > 0:
                p = count / self.total_users
                entropy -= p * math.log2(p)

        # Max possible entropy (all personas equally likely)
        max_entropy = math.log2(len(self.persona_counts)) if self.persona_counts else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Fairness criteria
        is_fair = (
            max_pct <= 50.0 and  # No dominant persona
            len(underrepresented) <= 2 and  # Allow some underrepresentation
            normalized_entropy >= 0.5  # Reasonable distribution
        )

        return {
            "is_fair": is_fair,
            "max_persona_percentage": max_pct,
            "entropy": entropy,
            "normalized_entropy": normalized_entropy,
            "underrepresented": underrepresented,
            "persona_percentages": percentages,
            "analysis": self._generate_fairness_analysis(is_fair, max_pct, underrepresented),
        }

    def _generate_fairness_analysis(
        self, is_fair: bool, max_pct: float, underrepresented: List[str]
    ) -> str:
        """Generate human-readable fairness analysis."""
        if is_fair:
            return "Persona distribution is reasonably balanced."

        issues = []
        if max_pct > 50.0:
            issues.append(f"One persona dominates ({max_pct:.1f}% of users)")
        if len(underrepresented) > 2:
            issues.append(f"Multiple personas underrepresented: {', '.join(underrepresented)}")

        return "Fairness concerns: " + "; ".join(issues)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for JSON serialization."""
        latency_stats = self.calculate_latency_stats()
        relevance_stats = self.calculate_relevance_stats()
        fairness = self.calculate_fairness()

        coverage = self.calculate_coverage()
        explainability = self.calculate_explainability()
        auditability = self.calculate_auditability()

        return {
            "summary": {
                "total_users": self.total_users,
                "total_recommendations": self.total_recommendations,
                "error_count": self.error_count,
            },
            "metrics": {
                "coverage": {
                    "value": round(coverage, 2),
                    "target": 100.0,
                    "pass": coverage >= 100.0,
                    "details": {
                        "users_with_persona": self.users_with_persona,
                        "users_with_min_signals": self.users_with_min_signals,
                    },
                },
                "explainability": {
                    "value": round(explainability, 2),
                    "target": 100.0,
                    "pass": explainability >= 100.0,
                    "details": {
                        "recs_with_explanation": self.recs_with_explanation,
                        "recs_with_signals": self.recs_with_signals,
                    },
                },
                "latency": {
                    "avg_seconds": round(latency_stats["avg"], 4),
                    "target_seconds": 5.0,
                    "pass": latency_stats["avg"] < 5.0,
                    "details": {
                        "min": round(latency_stats["min"], 4),
                        "max": round(latency_stats["max"], 4),
                        "p50": round(latency_stats["p50"], 4),
                        "p95": round(latency_stats["p95"], 4),
                        "p99": round(latency_stats["p99"], 4),
                    },
                },
                "auditability": {
                    "value": round(auditability, 2),
                    "target": 100.0,
                    "pass": auditability >= 100.0,
                    "details": {
                        "recs_with_complete_trace": self.recs_with_complete_trace,
                    },
                },
                "relevance": {
                    "avg_score": round(relevance_stats["avg"], 2),
                    "target": 3.0,
                    "pass": relevance_stats["avg"] >= 3.0,
                    "details": {
                        "min": relevance_stats["min"],
                        "max": relevance_stats["max"],
                        "distribution": relevance_stats["distribution"],
                    },
                },
                "fairness": {
                    "is_fair": fairness["is_fair"],
                    "details": {
                        "max_persona_percentage": round(fairness["max_persona_percentage"], 2),
                        "normalized_entropy": round(fairness["normalized_entropy"], 4),
                        "underrepresented": fairness["underrepresented"],
                        "persona_percentages": {
                            k: round(v, 2) for k, v in fairness["persona_percentages"].items()
                        },
                    },
                    "analysis": fairness["analysis"],
                },
            },
            "persona_distribution": self.persona_counts,
            "signal_count_distribution": self._calculate_signal_distribution(),
        }

    def _calculate_signal_distribution(self) -> Dict[str, int]:
        """Calculate distribution of signal counts."""
        distribution = {str(i): 0 for i in range(5)}  # 0-4 signals
        for count in self.signal_counts:
            key = str(min(count, 4))
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def passes_all_targets(self) -> bool:
        """Check if all metrics pass their targets."""
        latency_stats = self.calculate_latency_stats()
        relevance_stats = self.calculate_relevance_stats()

        return all([
            self.calculate_coverage() >= 100.0,
            self.calculate_explainability() >= 100.0,
            latency_stats["avg"] < 5.0,
            self.calculate_auditability() >= 100.0,
            relevance_stats["avg"] >= 3.0,
        ])
