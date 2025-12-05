"""
Eval Module - Evaluation and Metrics

This module provides the evaluation harness for measuring system performance:
- Coverage: % users with persona + >=3 signal categories
- Explainability: % recommendations with rationales
- Latency: Recommendation generation time
- Auditability: % with complete decision traces
- Relevance: Content match quality (1-5 scale)
- Fairness: Persona distribution analysis
"""

from spendsense.eval.metrics import EvaluationMetrics
from spendsense.eval.harness import (
    run_evaluation,
    evaluate_user,
    save_results_json,
    save_results_csv,
    generate_summary_report,
    main as run_harness,
)

__all__ = [
    "EvaluationMetrics",
    "run_evaluation",
    "evaluate_user",
    "save_results_json",
    "save_results_csv",
    "generate_summary_report",
    "run_harness",
]
