"""Policy coverage metric - tracks which policies are triggered.

DEPRECATED: This metric is deprecated and will be removed in v2.0.

The new trace-based evaluation model evaluates on the platform using
an LLM judge analyzing complete execution traces. This metric is no
longer used by the SDK.
"""

import warnings
from typing import List, Dict, Any, Set

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class PolicyCoverageMetric(BaseMetric):
    """
    Tracks which policies are triggered during evals to identify coverage gaps.

    Operates at eval-run level (aggregates across all test cases).
    """

    __name__ = "Policy Coverage"

    def __init__(
        self,
        required_policies: List[str],
        min_trigger_count: int = 3,
        threshold: float = 1.0,
    ):
        """
        Initialize PolicyCoverageMetric.

        Args:
            required_policies: List of policy IDs that must be tested
            min_trigger_count: Minimum times each policy should trigger
            threshold: Coverage threshold (default: 1.0 = 100%)
        """
        warnings.warn(
            "PolicyCoverageMetric is deprecated and will be removed in v2.0. "
            "The new trace-based evaluation model evaluates on the platform using "
            "an LLM judge analyzing complete execution traces.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.required_policies = set(required_policies)
        self.min_trigger_count = min_trigger_count
        self.threshold = threshold

        # Track triggers across all test cases
        self.policy_triggers: Dict[str, int] = {p: 0 for p in required_policies}
        self.untested_policies: Set[str] = set()

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Track policy triggers for this test case."""
        return self.measure(test_case)

    def measure(self, test_case: LLMTestCase) -> float:
        """Track policy triggers for this test case."""
        metadata = test_case.additional_metadata or {}
        guardrail_result = metadata.get("guardrail_result", {})
        matched_policies = guardrail_result.get("matched_policies", [])
        violated_policies = guardrail_result.get("violated_policies", [])

        # Increment trigger count for all matched/violated policies
        all_triggered = set(matched_policies + violated_policies)
        for policy_id in all_triggered:
            if policy_id in self.policy_triggers:
                self.policy_triggers[policy_id] += 1

        # Calculate coverage
        covered_policies = [
            p
            for p, count in self.policy_triggers.items()
            if count >= self.min_trigger_count
        ]
        self.untested_policies = self.required_policies - set(covered_policies)

        coverage_rate = (
            len(covered_policies) / len(self.required_policies)
            if self.required_policies
            else 1.0
        )
        self.score = coverage_rate
        self.success = coverage_rate >= self.threshold

        return coverage_rate

    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return bool(getattr(self, "success", False))

    def generate_report(self) -> Dict[str, Any]:
        """Generate detailed coverage report."""
        return {
            "coverage_rate": self.score,
            "covered_policies": len(
                [
                    c
                    for c in self.policy_triggers.values()
                    if c >= self.min_trigger_count
                ]
            ),
            "total_policies": len(self.required_policies),
            "untested_policies": list(self.untested_policies),
            "trigger_counts": self.policy_triggers,
            "policies_below_threshold": {
                p: count
                for p, count in self.policy_triggers.items()
                if count < self.min_trigger_count
            },
        }
