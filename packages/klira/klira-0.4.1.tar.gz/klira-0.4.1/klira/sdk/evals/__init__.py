"""Klira SDK Evaluation System.

Provides evaluation capabilities for testing AI applications with
standard LLM metrics and Klira's unique compliance-focused metrics.

Example:
    >>> from klira.sdk.evals import evaluate
    >>> from klira.sdk.evals.metrics import GuardrailsEffectivenessMetric
    >>> from klira.sdk.evals.convenience import compliance_metrics
    >>>
    >>> result = evaluate(
    ...     target=my_agent,
    ...     data="dataset.csv",
    ...     evaluators=compliance_metrics(required_policies=["pii", "toxicity"]),
    ... )
    >>> result.print_summary()
"""

from klira.sdk.evals.runner import evaluate
from klira.sdk.evals.types import KliraEvalResult, ComplianceReport

# Re-export convenience and ci modules for easier imports
from klira.sdk.evals import convenience
from klira.sdk.evals import ci

__all__ = [
    "evaluate",
    "KliraEvalResult",
    "ComplianceReport",
    "convenience",
    "ci",
]
