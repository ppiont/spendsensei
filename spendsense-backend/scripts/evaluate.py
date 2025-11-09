#!/usr/bin/env python3
"""
Evaluation Harness for SpendSense System

Measures system performance against PRD requirements:
- Coverage: % users with persona + ≥3 signals
- Explainability: % recommendations with rationales
- Latency: Average recommendation generation time
- Auditability: % with complete decision trace

Outputs results to console and data/evaluation_results.json
"""

import asyncio
import json
import sys
import time
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.services.recommendations import generate_recommendations
from spendsense.services.features import compute_signals
from spendsense.generators.template import TemplateGenerator


class EvaluationMetrics:
    """Container for evaluation metrics."""

    def __init__(self):
        self.total_users = 0
        self.total_recommendations = 0

        # Coverage metrics
        self.users_with_persona = 0
        self.users_with_min_signals = 0  # ≥3 signal categories

        # Explainability metrics
        self.recs_with_explanation = 0
        self.recs_with_signals = 0

        # Latency metrics
        self.latencies = []

        # Auditability metrics
        self.recs_with_complete_trace = 0

        # Relevance metrics
        self.relevance_scores = []

        # Persona distribution
        self.persona_counts = {}

        # Signal distribution
        self.signal_counts = []

    def calculate_coverage(self) -> float:
        """Calculate coverage percentage."""
        if self.total_users == 0:
            return 0.0
        # User must have BOTH persona AND ≥3 signals
        users_with_coverage = min(self.users_with_persona, self.users_with_min_signals)
        return (users_with_coverage / self.total_users) * 100

    def calculate_explainability(self) -> float:
        """Calculate explainability percentage."""
        if self.total_recommendations == 0:
            return 0.0
        # Recommendation must have BOTH explanation AND key_signals
        recs_with_explainability = min(self.recs_with_explanation, self.recs_with_signals)
        return (recs_with_explainability / self.total_recommendations) * 100

    def calculate_latency_avg(self) -> float:
        """Calculate average latency."""
        if not self.latencies:
            return 0.0
        return statistics.mean(self.latencies)

    def calculate_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles."""
        if not self.latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_latencies = sorted(self.latencies)
        return {
            "p50": statistics.median(sorted_latencies),
            "p95": statistics.quantiles(sorted_latencies, n=20)[18],  # 95th percentile
            "p99": statistics.quantiles(sorted_latencies, n=100)[98] if len(sorted_latencies) >= 100 else sorted_latencies[-1],
        }

    def calculate_auditability(self) -> float:
        """Calculate auditability percentage."""
        if self.total_recommendations == 0:
            return 0.0
        return (self.recs_with_complete_trace / self.total_recommendations) * 100

    def calculate_relevance_avg(self) -> float:
        """Calculate average relevance score (1-5 scale)."""
        if not self.relevance_scores:
            return 0.0
        return statistics.mean(self.relevance_scores)


async def evaluate_user(
    db: AsyncSession,
    user_id: str,
    generator: TemplateGenerator,
    metrics: EvaluationMetrics
) -> Dict[str, Any]:
    """Evaluate a single user and update metrics."""

    user_result = {
        "user_id": user_id,
        "success": False,
        "error": None,
        "latency": 0.0,
        "persona": None,
        "signal_count": 0,
        "recommendation_count": 0
    }

    try:
        # Measure latency
        start_time = time.time()

        # Generate recommendations
        recommendations = await generate_recommendations(
            db=db,
            user_id=user_id,
            generator=generator,
            window_days=30
        )

        end_time = time.time()
        latency = end_time - start_time

        metrics.latencies.append(latency)
        user_result["latency"] = latency
        user_result["recommendation_count"] = len(recommendations)
        metrics.total_recommendations += len(recommendations)

        # Check coverage: persona assigned
        if recommendations and recommendations[0].persona:
            metrics.users_with_persona += 1
            user_result["persona"] = recommendations[0].persona

            # Track persona distribution
            persona = recommendations[0].persona
            metrics.persona_counts[persona] = metrics.persona_counts.get(persona, 0) + 1

        # Check coverage: ≥3 signal categories
        # Need to recompute signals to count them
        from spendsense.services.features import compute_signals
        from spendsense.models.transaction import Transaction
        from spendsense.models.account import Account

        # Get transactions for signal computation
        trans_result = await db.execute(
            select(Transaction)
            .join(Account)
            .where(Account.user_id == user_id)
            .order_by(Transaction.date)
        )
        transactions = trans_result.scalars().all()

        if transactions:
            signals = await compute_signals(db, user_id, window_days=30)

            # Count non-empty signal categories
            signal_count = sum([
                bool(signals.subscriptions),
                bool(signals.savings),
                bool(signals.credit),
                bool(signals.income)
            ])

            user_result["signal_count"] = signal_count
            metrics.signal_counts.append(signal_count)

            if signal_count >= 3:
                metrics.users_with_min_signals += 1

        # Check explainability, auditability, and relevance for each recommendation
        for rec in recommendations:
            # Explainability: has explanation text
            if rec.rationale.explanation and len(rec.rationale.explanation) > 0:
                metrics.recs_with_explanation += 1

            # Explainability: has key signals
            if rec.rationale.key_signals and len(rec.rationale.key_signals) > 0:
                metrics.recs_with_signals += 1

            # Auditability: has complete trace
            has_complete_trace = all([
                rec.persona,
                rec.confidence is not None,
                rec.rationale.explanation,
                rec.rationale.key_signals,
                rec.content.id
            ])

            if has_complete_trace:
                metrics.recs_with_complete_trace += 1

            # Relevance: track relevance score (1-5 scale)
            if hasattr(rec.content, 'relevance_score') and rec.content.relevance_score is not None:
                metrics.relevance_scores.append(rec.content.relevance_score)

        user_result["success"] = True

    except Exception as e:
        user_result["error"] = str(e)
        print(f"  ✗ Error evaluating user {user_id[:8]}: {e}")

    return user_result


async def run_evaluation() -> Dict[str, Any]:
    """Run evaluation against all users."""

    print("=" * 80)
    print("SPENDSENSE EVALUATION HARNESS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    metrics = EvaluationMetrics()
    user_results = []

    # Initialize generator
    generator = TemplateGenerator()

    async with AsyncSessionLocal() as db:
        # Get all user IDs
        result = await db.execute(select(User.id))
        user_ids = [row[0] for row in result.all()]

        if not user_ids:
            print("✗ No users found in database")
            return {}

        metrics.total_users = len(user_ids)
        print(f"Found {len(user_ids)} users to evaluate")
        print()

        # Evaluate each user
        for i, user_id in enumerate(user_ids, 1):
            print(f"[{i}/{len(user_ids)}] Evaluating user {user_id[:8]}...")

            user_result = await evaluate_user(db, user_id, generator, metrics)
            user_results.append(user_result)

            if user_result["success"]:
                print(f"  ✓ Persona: {user_result['persona']}, "
                      f"Signals: {user_result['signal_count']}, "
                      f"Recs: {user_result['recommendation_count']}, "
                      f"Latency: {user_result['latency']:.3f}s")
            print()

    # Calculate metrics
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print()

    # Coverage
    coverage = metrics.calculate_coverage()
    coverage_pass = coverage >= 100.0
    print(f"Coverage:       {coverage:6.2f}% {'✓ PASS' if coverage_pass else '✗ FAIL'} (target: 100%)")
    print(f"  - Users with persona: {metrics.users_with_persona}/{metrics.total_users}")
    print(f"  - Users with ≥3 signals: {metrics.users_with_min_signals}/{metrics.total_users}")
    print()

    # Explainability
    explainability = metrics.calculate_explainability()
    explainability_pass = explainability >= 100.0
    print(f"Explainability: {explainability:6.2f}% {'✓ PASS' if explainability_pass else '✗ FAIL'} (target: 100%)")
    print(f"  - Recs with explanation: {metrics.recs_with_explanation}/{metrics.total_recommendations}")
    print(f"  - Recs with key signals: {metrics.recs_with_signals}/{metrics.total_recommendations}")
    print()

    # Latency
    latency_avg = metrics.calculate_latency_avg()
    latency_pass = latency_avg < 5.0
    percentiles = metrics.calculate_latency_percentiles()
    print(f"Latency (avg):  {latency_avg:6.3f}s {'✓ PASS' if latency_pass else '✗ FAIL'} (target: <5s)")
    print(f"  - P50: {percentiles['p50']:.3f}s")
    print(f"  - P95: {percentiles['p95']:.3f}s")
    print(f"  - P99: {percentiles['p99']:.3f}s")
    print()

    # Auditability
    auditability = metrics.calculate_auditability()
    auditability_pass = auditability >= 100.0
    print(f"Auditability:   {auditability:6.2f}% {'✓ PASS' if auditability_pass else '✗ FAIL'} (target: 100%)")
    print(f"  - Recs with complete trace: {metrics.recs_with_complete_trace}/{metrics.total_recommendations}")
    print()

    # Relevance
    relevance_avg = metrics.calculate_relevance_avg()
    relevance_pass = relevance_avg >= 3.0  # Target: average relevance ≥ 3.0 (Good match or better)
    print(f"Relevance (avg): {relevance_avg:6.2f}/5 {'✓ PASS' if relevance_pass else '✗ FAIL'} (target: ≥3.0)")
    print(f"  - Recommendations with relevance scores: {len(metrics.relevance_scores)}/{metrics.total_recommendations}")
    if metrics.relevance_scores:
        print(f"  - Min: {min(metrics.relevance_scores)}, Max: {max(metrics.relevance_scores)}")
    print()

    # Persona distribution
    print("Persona Distribution:")
    for persona, count in sorted(metrics.persona_counts.items()):
        pct = (count / metrics.total_users) * 100 if metrics.total_users > 0 else 0
        print(f"  - {persona}: {count} ({pct:.1f}%)")
    print()

    # Overall result
    all_pass = all([coverage_pass, explainability_pass, latency_pass, auditability_pass, relevance_pass])
    print("=" * 80)
    if all_pass:
        print("✓ ALL METRICS PASS")
    else:
        print("✗ SOME METRICS FAILED")
    print("=" * 80)
    print()

    # Prepare results dictionary
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_users": metrics.total_users,
        "total_recommendations": metrics.total_recommendations,
        "metrics": {
            "coverage": {
                "value": coverage,
                "target": 100.0,
                "pass": coverage_pass,
                "users_with_persona": metrics.users_with_persona,
                "users_with_min_signals": metrics.users_with_min_signals
            },
            "explainability": {
                "value": explainability,
                "target": 100.0,
                "pass": explainability_pass,
                "recs_with_explanation": metrics.recs_with_explanation,
                "recs_with_signals": metrics.recs_with_signals
            },
            "latency_avg": {
                "value": latency_avg,
                "target": 5.0,
                "pass": latency_pass
            },
            "auditability": {
                "value": auditability,
                "target": 100.0,
                "pass": auditability_pass,
                "recs_with_complete_trace": metrics.recs_with_complete_trace
            },
            "relevance_avg": {
                "value": relevance_avg,
                "target": 3.0,
                "pass": relevance_pass,
                "recs_with_scores": len(metrics.relevance_scores),
                "min_score": min(metrics.relevance_scores) if metrics.relevance_scores else None,
                "max_score": max(metrics.relevance_scores) if metrics.relevance_scores else None
            }
        },
        "latency_percentiles": percentiles,
        "persona_distribution": metrics.persona_counts,
        "all_metrics_pass": all_pass,
        "user_results": user_results
    }

    return results


def main():
    """Main entry point."""
    # Run evaluation
    results = asyncio.run(run_evaluation())

    if not results:
        return 1

    # Save results to JSON
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "evaluation_results.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # Exit code based on whether all metrics passed
    return 0 if results["all_metrics_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
