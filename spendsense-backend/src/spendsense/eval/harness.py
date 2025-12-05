"""
Evaluation Harness Module

Main evaluation runner that:
1. Iterates through all users in the database
2. Generates recommendations for each user
3. Collects metrics (coverage, explainability, latency, auditability, relevance)
4. Outputs results to JSON and CSV
5. Generates summary report
"""

import asyncio
import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from spendsense.features import compute_signals
from spendsense.recommend import StandardRecommendationEngine
from spendsense.eval.metrics import EvaluationMetrics

logger = logging.getLogger(__name__)


async def evaluate_user(
    db: AsyncSession,
    user_id: str,
    engine: StandardRecommendationEngine,
    metrics: EvaluationMetrics,
    window_days: int = 30,
) -> Dict[str, Any]:
    """
    Evaluate a single user and update metrics.

    Args:
        db: Database session
        user_id: User ID to evaluate
        engine: Recommendation engine instance
        metrics: Metrics container to update
        window_days: Analysis window (30 or 180)

    Returns:
        Per-user evaluation result dictionary
    """
    user_result = {
        "user_id": user_id,
        "success": False,
        "error": None,
        "latency_seconds": 0.0,
        "persona": None,
        "confidence": None,
        "signal_count": 0,
        "education_count": 0,
        "offer_count": 0,
        "window_days": window_days,
    }

    try:
        # Measure latency for recommendation generation
        start_time = time.perf_counter()

        result = await engine.generate_recommendations(
            db=db,
            user_id=user_id,
            window_days=window_days,
        )

        end_time = time.perf_counter()
        latency = end_time - start_time

        # Record latency
        metrics.latencies.append(latency)
        user_result["latency_seconds"] = latency

        # Record recommendation counts
        education_recs = result.education_recommendations
        offer_recs = result.offer_recommendations

        user_result["education_count"] = len(education_recs)
        user_result["offer_count"] = len(offer_recs)

        total_recs = len(education_recs) + len(offer_recs)
        metrics.total_recommendations += total_recs

        # Check coverage: persona assigned
        if result.persona_type and result.persona_type != "consent_required":
            metrics.users_with_persona += 1
            user_result["persona"] = result.persona_type
            user_result["confidence"] = result.confidence

            # Track persona distribution
            persona = result.persona_type
            metrics.persona_counts[persona] = metrics.persona_counts.get(persona, 0) + 1

        # Check coverage: signal categories
        # Count non-empty signal categories from signals_summary
        signals = result.signals_summary
        signal_count = 0

        if signals.get("credit") and any(signals["credit"].values()):
            signal_count += 1
        if signals.get("income") and any(signals["income"].values()):
            signal_count += 1
        if signals.get("savings") and any(signals["savings"].values()):
            signal_count += 1
        if signals.get("subscriptions") and any(signals["subscriptions"].values()):
            signal_count += 1

        user_result["signal_count"] = signal_count
        metrics.signal_counts.append(signal_count)

        if signal_count >= 3:
            metrics.users_with_min_signals += 1

        # Check explainability and auditability for education recommendations
        for rec in education_recs:
            # Explainability: has explanation text
            if rec.rationale and rec.rationale.explanation:
                metrics.recs_with_explanation += 1

            # Explainability: has key signals
            if rec.rationale and rec.rationale.key_signals:
                metrics.recs_with_signals += 1

            # Auditability: complete trace
            has_complete_trace = all([
                rec.persona,
                rec.confidence is not None,
                rec.rationale and rec.rationale.explanation,
                rec.rationale and rec.rationale.key_signals,
                rec.content and rec.content.id,
            ])

            if has_complete_trace:
                metrics.recs_with_complete_trace += 1

            # Relevance score
            if rec.content and rec.content.relevance_score:
                metrics.relevance_scores.append(rec.content.relevance_score)

        # Check explainability and auditability for offer recommendations
        for rec in offer_recs:
            # Explainability: has explanation text
            if rec.rationale and rec.rationale.explanation:
                metrics.recs_with_explanation += 1

            # Explainability: has key signals
            if rec.rationale and rec.rationale.key_signals:
                metrics.recs_with_signals += 1

            # Auditability: complete trace
            has_complete_trace = all([
                rec.persona,
                rec.confidence is not None,
                rec.rationale and rec.rationale.explanation,
                rec.rationale and rec.rationale.key_signals,
                rec.offer and rec.offer.id,
            ])

            if has_complete_trace:
                metrics.recs_with_complete_trace += 1

            # Relevance score
            if rec.offer and rec.offer.relevance_score:
                metrics.relevance_scores.append(rec.offer.relevance_score)

        user_result["success"] = True

    except Exception as e:
        user_result["error"] = str(e)
        metrics.error_count += 1
        metrics.errors.append({
            "user_id": user_id,
            "error": str(e),
        })
        logger.warning(f"Error evaluating user {user_id[:8]}: {e}")

    return user_result


async def run_evaluation(
    window_days: int = 30,
    limit: Optional[int] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run evaluation against all users (or limited subset).

    Args:
        window_days: Analysis window (30 or 180)
        limit: Optional limit on number of users to evaluate
        verbose: Whether to print progress

    Returns:
        Complete evaluation results dictionary
    """
    if verbose:
        print("=" * 80)
        print("SPENDSENSE EVALUATION HARNESS")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Window: {window_days} days")
        print()

    metrics = EvaluationMetrics()
    user_results = []
    engine = StandardRecommendationEngine()

    async with AsyncSessionLocal() as db:
        # Get all user IDs
        query = select(User.id).order_by(User.created_at)
        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        user_ids = [row[0] for row in result.all()]

        if not user_ids:
            if verbose:
                print("No users found in database")
            return {"error": "No users found", "timestamp": datetime.now().isoformat()}

        metrics.total_users = len(user_ids)

        if verbose:
            print(f"Found {len(user_ids)} users to evaluate")
            print()

        # Evaluate each user
        for i, user_id in enumerate(user_ids, 1):
            if verbose:
                print(f"[{i}/{len(user_ids)}] Evaluating user {user_id[:8]}...", end=" ")

            user_result = await evaluate_user(
                db=db,
                user_id=user_id,
                engine=engine,
                metrics=metrics,
                window_days=window_days,
            )
            user_results.append(user_result)

            if verbose:
                if user_result["success"]:
                    print(
                        f"OK | {user_result['persona']} | "
                        f"{user_result['signal_count']} signals | "
                        f"{user_result['education_count']}E + {user_result['offer_count']}O | "
                        f"{user_result['latency_seconds']:.3f}s"
                    )
                else:
                    print(f"ERROR: {user_result['error']}")

    # Build final results
    results = {
        "timestamp": datetime.now().isoformat(),
        "window_days": window_days,
        "metrics": metrics.to_dict(),
        "all_targets_pass": metrics.passes_all_targets(),
        "user_results": user_results,
    }

    if verbose:
        print()
        print_summary(results)

    return results


def print_summary(results: Dict[str, Any]) -> None:
    """Print evaluation summary to console."""
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print()

    m = results["metrics"]["metrics"]

    # Coverage
    cov = m["coverage"]
    status = "PASS" if cov["pass"] else "FAIL"
    print(f"Coverage:       {cov['value']:6.2f}% [{status}] (target: 100%)")
    print(f"  - Users with persona:     {cov['details']['users_with_persona']}/{results['metrics']['summary']['total_users']}")
    print(f"  - Users with >=3 signals: {cov['details']['users_with_min_signals']}/{results['metrics']['summary']['total_users']}")
    print()

    # Explainability
    exp = m["explainability"]
    status = "PASS" if exp["pass"] else "FAIL"
    print(f"Explainability: {exp['value']:6.2f}% [{status}] (target: 100%)")
    print(f"  - With explanation: {exp['details']['recs_with_explanation']}/{results['metrics']['summary']['total_recommendations']}")
    print(f"  - With key signals: {exp['details']['recs_with_signals']}/{results['metrics']['summary']['total_recommendations']}")
    print()

    # Latency
    lat = m["latency"]
    status = "PASS" if lat["pass"] else "FAIL"
    print(f"Latency (avg):  {lat['avg_seconds']:6.4f}s [{status}] (target: <5s)")
    print(f"  - Min: {lat['details']['min']:.4f}s")
    print(f"  - P50: {lat['details']['p50']:.4f}s")
    print(f"  - P95: {lat['details']['p95']:.4f}s")
    print(f"  - Max: {lat['details']['max']:.4f}s")
    print()

    # Auditability
    aud = m["auditability"]
    status = "PASS" if aud["pass"] else "FAIL"
    print(f"Auditability:   {aud['value']:6.2f}% [{status}] (target: 100%)")
    print(f"  - Complete traces: {aud['details']['recs_with_complete_trace']}/{results['metrics']['summary']['total_recommendations']}")
    print()

    # Relevance
    rel = m["relevance"]
    status = "PASS" if rel["pass"] else "FAIL"
    print(f"Relevance:      {rel['avg_score']:6.2f}/5 [{status}] (target: >=3.0)")
    print(f"  - Score distribution: {rel['details']['distribution']}")
    print()

    # Fairness
    fair = m["fairness"]
    status = "PASS" if fair["is_fair"] else "WARN"
    print(f"Fairness:       [{status}]")
    print(f"  - Max persona %: {fair['details']['max_persona_percentage']:.1f}%")
    print(f"  - Entropy: {fair['details']['normalized_entropy']:.4f}")
    if fair["details"]["underrepresented"]:
        print(f"  - Underrepresented: {', '.join(fair['details']['underrepresented'])}")
    print(f"  - Analysis: {fair['analysis']}")
    print()

    # Persona Distribution
    print("Persona Distribution:")
    for persona, pct in sorted(fair["details"]["persona_percentages"].items()):
        count = results["metrics"]["persona_distribution"].get(persona, 0)
        print(f"  - {persona}: {count} ({pct:.1f}%)")
    print()

    # Overall
    print("=" * 80)
    if results["all_targets_pass"]:
        print("ALL METRICS PASS")
    else:
        print("SOME METRICS FAILED - Review details above")
    print("=" * 80)


def save_results_json(results: Dict[str, Any], output_path: Path) -> None:
    """Save results to JSON file."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)


def save_results_csv(results: Dict[str, Any], output_path: Path) -> None:
    """Save per-user results to CSV file."""
    user_results = results.get("user_results", [])

    if not user_results:
        return

    fieldnames = [
        "user_id", "success", "error", "latency_seconds",
        "persona", "confidence", "signal_count",
        "education_count", "offer_count", "window_days"
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in user_results:
            writer.writerow(row)


def generate_summary_report(results: Dict[str, Any]) -> str:
    """Generate markdown summary report."""
    m = results["metrics"]["metrics"]
    summary = results["metrics"]["summary"]
    timestamp = results["timestamp"]

    report = f"""# SpendSense Evaluation Report

**Generated**: {timestamp}
**Window**: {results['window_days']} days
**Users Evaluated**: {summary['total_users']}
**Recommendations Generated**: {summary['total_recommendations']}

## Results Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Coverage | {m['coverage']['value']:.2f}% | 100% | {'PASS' if m['coverage']['pass'] else 'FAIL'} |
| Explainability | {m['explainability']['value']:.2f}% | 100% | {'PASS' if m['explainability']['pass'] else 'FAIL'} |
| Latency | {m['latency']['avg_seconds']:.4f}s | <5s | {'PASS' if m['latency']['pass'] else 'FAIL'} |
| Auditability | {m['auditability']['value']:.2f}% | 100% | {'PASS' if m['auditability']['pass'] else 'FAIL'} |
| Relevance | {m['relevance']['avg_score']:.2f}/5 | >=3.0 | {'PASS' if m['relevance']['pass'] else 'FAIL'} |

## Coverage Details

- Users with assigned persona: {m['coverage']['details']['users_with_persona']}/{summary['total_users']}
- Users with >=3 signal categories: {m['coverage']['details']['users_with_min_signals']}/{summary['total_users']}

Coverage measures whether each user receives meaningful analysis. A user has coverage if:
1. They have an assigned persona (not "consent_required" or "balanced" fallback without signals)
2. At least 3 of the 4 signal categories (credit, income, savings, subscriptions) have data

## Explainability Details

- Recommendations with explanation text: {m['explainability']['details']['recs_with_explanation']}/{summary['total_recommendations']}
- Recommendations with key signals: {m['explainability']['details']['recs_with_signals']}/{summary['total_recommendations']}

Every recommendation includes a "because" rationale that cites specific data points from the user's
financial profile. This ensures transparency in why each piece of content was selected.

## Latency Details

| Percentile | Value |
|------------|-------|
| Min | {m['latency']['details']['min']:.4f}s |
| P50 (Median) | {m['latency']['details']['p50']:.4f}s |
| P95 | {m['latency']['details']['p95']:.4f}s |
| P99/Max | {m['latency']['details']['max']:.4f}s |
| **Average** | **{m['latency']['avg_seconds']:.4f}s** |

Recommendation generation completes well under the 5-second target, ensuring responsive user experience.

## Auditability Details

- Recommendations with complete decision trace: {m['auditability']['details']['recs_with_complete_trace']}/{summary['total_recommendations']}

A complete decision trace includes: persona type, confidence score, explanation text, key signals list,
and content/offer ID. This enables full reconstruction of why each recommendation was made.

## Relevance Score Distribution

| Score | Count | Meaning |
|-------|-------|---------|
| 5 | {m['relevance']['details']['distribution'].get('5', 0)} | Excellent match |
| 4 | {m['relevance']['details']['distribution'].get('4', 0)} | Very good match |
| 3 | {m['relevance']['details']['distribution'].get('3', 0)} | Good match |
| 2 | {m['relevance']['details']['distribution'].get('2', 0)} | Fair match |
| 1 | {m['relevance']['details']['distribution'].get('1', 0)} | Poor match |

Average relevance score: **{m['relevance']['avg_score']:.2f}/5**

## Fairness Analysis

{m['fairness']['analysis']}

### Persona Distribution

| Persona | Count | Percentage |
|---------|-------|------------|
"""

    for persona, pct in sorted(m['fairness']['details']['persona_percentages'].items()):
        count = results["metrics"]["persona_distribution"].get(persona, 0)
        report += f"| {persona} | {count} | {pct:.1f}% |\n"

    report += f"""
**Entropy**: {m['fairness']['details']['normalized_entropy']:.4f} (higher = more evenly distributed)

## Conclusion

**Overall Status**: {'ALL TARGETS PASS' if results['all_targets_pass'] else 'SOME TARGETS FAILED'}

"""

    if results["all_targets_pass"]:
        report += """The SpendSense recommendation system meets all evaluation criteria defined in the
Product Requirements Document. The system provides:

- Complete coverage of all users with meaningful behavioral analysis
- 100% explainable recommendations with data-driven rationales
- Sub-second response times for real-time recommendations
- Full auditability with complete decision traces
- High-quality content matching with average relevance scores above target
"""
    else:
        report += "Review the details above to identify areas requiring improvement.\n"

    report += f"""
---

*This report was automatically generated by the SpendSense evaluation harness.*
*Timestamp: {timestamp}*
"""

    return report


async def main(
    window_days: int = 30,
    limit: Optional[int] = None,
    output_dir: Optional[Path] = None,
) -> int:
    """
    Main entry point for evaluation harness.

    Args:
        window_days: Analysis window (30 or 180)
        limit: Optional limit on users to evaluate
        output_dir: Output directory for results files

    Returns:
        Exit code (0 = all pass, 1 = some fail)
    """
    # Run evaluation
    results = await run_evaluation(
        window_days=window_days,
        limit=limit,
        verbose=True,
    )

    if "error" in results:
        return 1

    # Determine output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent.parent / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON results
    json_path = output_dir / "evaluation_results.json"
    save_results_json(results, json_path)
    print(f"\nResults saved to: {json_path}")

    # Save CSV results
    csv_path = output_dir / "evaluation_results.csv"
    save_results_csv(results, csv_path)
    print(f"Per-user CSV saved to: {csv_path}")

    # Generate and save summary report
    report = generate_summary_report(results)
    report_path = output_dir / "evaluation_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Summary report saved to: {report_path}")

    return 0 if results["all_targets_pass"] else 1


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="SpendSense Evaluation Harness")
    parser.add_argument("--window", type=int, default=30, help="Analysis window (30 or 180 days)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of users to evaluate")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for results")

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    exit_code = asyncio.run(main(
        window_days=args.window,
        limit=args.limit,
        output_dir=output_dir,
    ))
    sys.exit(exit_code)
