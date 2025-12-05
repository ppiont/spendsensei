#!/usr/bin/env python3
"""
Evaluation Harness for SpendSense System

Measures system performance against PRD requirements:
- Coverage: % users with persona + >=3 signals
- Explainability: % recommendations with rationales
- Latency: Average recommendation generation time
- Auditability: % with complete decision trace
- Relevance: Average content match quality (1-5 scale)
- Fairness: Persona distribution analysis

Outputs results to:
- data/evaluation_results.json (full results)
- data/evaluation_results.csv (per-user results)
- data/evaluation_report.md (summary report)

Usage:
    python scripts/evaluate.py [--window 30|180] [--limit N]
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spendsense.eval.harness import main


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="SpendSense Evaluation Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run full evaluation with 30-day window
    python scripts/evaluate.py

    # Run evaluation with 180-day window
    python scripts/evaluate.py --window 180

    # Run quick test with only 5 users
    python scripts/evaluate.py --limit 5
        """,
    )
    parser.add_argument(
        "--window",
        type=int,
        default=30,
        choices=[30, 180],
        help="Analysis window in days (default: 30)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of users to evaluate (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for results (default: data/)",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    exit_code = asyncio.run(main(
        window_days=args.window,
        limit=args.limit,
        output_dir=output_dir,
    ))
    sys.exit(exit_code)
