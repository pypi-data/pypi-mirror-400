"""Policy accuracy metric - measures false positive/negative rates per policy.

DEPRECATED: This metric is deprecated and will be removed in v2.0.

The new trace-based evaluation model evaluates on the platform using
an LLM judge analyzing complete execution traces. This metric is no
longer used by the SDK.
"""

import warnings
from typing import Dict, Any, List, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class PolicyAccuracyMetric(BaseMetric):
    """
    Measures false positive/negative rates per policy.

    Provides policy-level accuracy analysis:
    - Per-policy recall and precision
    - False positive/negative breakdown by policy
    - Layer-specific accuracy (which layers work best for which policies)
    - Confidence threshold tuning recommendations

    Essential for identifying which policies need improvement.
    """

    __name__ = "Policy Accuracy"

    def __init__(
        self,
        tracked_policies: Optional[List[str]] = None,
        min_accuracy: float = 0.85,
        threshold: Optional[float] = None,
    ):
        """
        Initialize PolicyAccuracyMetric.

        Args:
            tracked_policies: List of policy IDs to track (if None, track all)
            min_accuracy: Minimum acceptable accuracy per policy
            threshold: Overall threshold (defaults to min_accuracy)
        """
        warnings.warn(
            "PolicyAccuracyMetric is deprecated and will be removed in v2.0. "
            "The new trace-based evaluation model evaluates on the platform using "
            "an LLM judge analyzing complete execution traces.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.tracked_policies = set(tracked_policies) if tracked_policies else None
        self.min_accuracy = min_accuracy
        self.threshold = threshold or min_accuracy

        # Per-policy tracking
        self.policy_stats: Dict[str, Dict[str, int]] = {}

        # Layer-specific tracking
        self.layer_policy_stats: Dict[str, Dict[str, Dict[str, int]]] = {}

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Measure policy accuracy for this test case."""
        return self.measure(test_case)

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure policy accuracy for this test case."""
        # Get expected behavior
        metadata = test_case.additional_metadata or {}
        klira_meta = metadata.get("klira", {})
        expected_decision = klira_meta.get("expected_guardrail_decision")
        expected_policies = set(klira_meta.get("expected_blocked_policies", []))

        # Get actual guardrail result
        guardrail_result = metadata.get("guardrail_result", {})
        violated_policies = set(guardrail_result.get("violated_policies", []))
        decision_layer = guardrail_result.get("decision_layer", "unknown")

        # Filter to tracked policies if specified
        if self.tracked_policies:
            expected_policies = expected_policies & self.tracked_policies
            violated_policies = violated_policies & self.tracked_policies

        # Initialize policy stats if needed
        all_policies = expected_policies | violated_policies
        for policy in all_policies:
            if policy not in self.policy_stats:
                self.policy_stats[policy] = {
                    "tp": 0,  # True positives
                    "fp": 0,  # False positives
                    "tn": 0,  # True negatives
                    "fn": 0,  # False negatives
                }

            # Initialize layer stats for this policy
            if decision_layer not in self.layer_policy_stats:
                self.layer_policy_stats[decision_layer] = {}
            if policy not in self.layer_policy_stats[decision_layer]:
                self.layer_policy_stats[decision_layer][policy] = {
                    "tp": 0,
                    "fp": 0,
                    "tn": 0,
                    "fn": 0,
                }

        # Evaluate per-policy accuracy
        score = 0.0
        evaluated_policies = 0

        if expected_decision == "BLOCK":
            # Expected: policies should be violated
            for policy in expected_policies:
                if policy in violated_policies:
                    # Correctly detected violation
                    self.policy_stats[policy]["tp"] += 1
                    self.layer_policy_stats[decision_layer][policy]["tp"] += 1
                    score += 1.0
                    evaluated_policies += 1
                else:
                    # Missed violation (false negative)
                    self.policy_stats[policy]["fn"] += 1
                    self.layer_policy_stats[decision_layer][policy]["fn"] += 1
                    evaluated_policies += 1

            # Check for false positives (policies violated that shouldn't be)
            false_positive_policies = violated_policies - expected_policies
            for policy in false_positive_policies:
                if policy not in self.policy_stats:
                    self.policy_stats[policy] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
                self.policy_stats[policy]["fp"] += 1

                if policy not in self.layer_policy_stats[decision_layer]:
                    self.layer_policy_stats[decision_layer][policy] = {
                        "tp": 0,
                        "fp": 0,
                        "tn": 0,
                        "fn": 0,
                    }
                self.layer_policy_stats[decision_layer][policy]["fp"] += 1

        elif expected_decision == "ALLOW":
            # Expected: no policies should be violated
            if len(violated_policies) == 0:
                # Correctly allowed (true negative for all tracked policies)
                for policy in all_policies:
                    self.policy_stats[policy]["tn"] += 1
                    self.layer_policy_stats[decision_layer][policy]["tn"] += 1
                score = 1.0
                evaluated_policies = 1
            else:
                # False positive: policies violated when they shouldn't be
                for policy in violated_policies:
                    if policy not in self.policy_stats:
                        self.policy_stats[policy] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
                    self.policy_stats[policy]["fp"] += 1

                    if policy not in self.layer_policy_stats[decision_layer]:
                        self.layer_policy_stats[decision_layer][policy] = {
                            "tp": 0,
                            "fp": 0,
                            "tn": 0,
                            "fn": 0,
                        }
                    self.layer_policy_stats[decision_layer][policy]["fp"] += 1
                evaluated_policies = 1

        # Calculate overall accuracy
        overall_accuracy = self._calculate_overall_accuracy()

        self.score = overall_accuracy
        self.success = overall_accuracy >= self.threshold

        return score / evaluated_policies if evaluated_policies > 0 else 0.0

    def _calculate_overall_accuracy(self) -> float:
        """Calculate overall accuracy across all policies."""
        if not self.policy_stats:
            return 0.0

        total_correct = 0
        total_cases = 0

        for stats in self.policy_stats.values():
            correct = stats["tp"] + stats["tn"]
            cases = stats["tp"] + stats["fp"] + stats["tn"] + stats["fn"]

            total_correct += correct
            total_cases += cases

        return total_correct / total_cases if total_cases > 0 else 0.0

    def _calculate_policy_metrics(self, stats: Dict[str, int]) -> Dict[str, float]:
        """Calculate recall, precision, and accuracy for a policy."""
        tp = stats["tp"]
        fp = stats["fp"]
        tn = stats["tn"]
        fn = stats["fn"]

        total = tp + fp + tn + fn
        if total == 0:
            return {"recall": 0.0, "precision": 0.0, "accuracy": 0.0, "f1": 0.0}

        # Recall: TP / (TP + FN)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # Precision: TP / (TP + FP)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Accuracy: (TP + TN) / Total
        accuracy = (tp + tn) / total

        # F1 Score
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "recall": recall,
            "precision": precision,
            "accuracy": accuracy,
            "f1": f1,
        }

    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return bool(getattr(self, "success", False))

    def generate_report(self) -> Dict[str, Any]:
        """Generate policy accuracy report."""
        # Calculate per-policy metrics
        policy_metrics = {}
        for policy, stats in self.policy_stats.items():
            policy_metrics[policy] = self._calculate_policy_metrics(stats)

        # Calculate layer-specific metrics
        layer_metrics: Dict[str, Any] = {}
        for layer, policies in self.layer_policy_stats.items():
            layer_metrics[layer] = {}
            for policy, stats in policies.items():
                layer_metrics[layer][policy] = self._calculate_policy_metrics(stats)

        # Identify problematic policies
        low_accuracy_policies = [
            (policy, metrics["accuracy"])
            for policy, metrics in policy_metrics.items()
            if metrics["accuracy"] < self.min_accuracy
        ]

        return {
            "overall_accuracy": self.score,
            "policy_metrics": policy_metrics,
            "layer_metrics": layer_metrics,
            "low_accuracy_policies": low_accuracy_policies,
            "policy_stats": self.policy_stats,
            "recommendations": self._generate_recommendations(
                policy_metrics, layer_metrics, low_accuracy_policies
            ),
        }

    def _generate_recommendations(
        self,
        policy_metrics: Dict[str, Dict[str, float]],
        layer_metrics: Dict[str, Dict[str, Dict[str, float]]],
        low_accuracy_policies: List[tuple],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if not policy_metrics:
            recommendations.append(
                "No policy data collected. Ensure test dataset includes expected_blocked_policies."
            )
            return recommendations

        # Overall accuracy
        if self.score is not None and self.score < 0.7:
            recommendations.append(
                f"Low overall policy accuracy ({self.score:.1%}). "
                "Review policy definitions and test data quality."
            )
        elif self.score is not None and self.score >= 0.9:
            recommendations.append(
                f"Excellent overall policy accuracy ({self.score:.1%})."
            )

        # Low accuracy policies
        if low_accuracy_policies:
            policy_names = ", ".join(
                [f"{p} ({acc:.1%})" for p, acc in low_accuracy_policies]
            )
            recommendations.append(
                f"Policies with low accuracy: {policy_names}. "
                "Review patterns and consider tuning confidence thresholds."
            )

        # Per-policy recommendations
        for policy, metrics in policy_metrics.items():
            if metrics["recall"] < 0.7:
                recommendations.append(
                    f"Policy '{policy}' has low recall ({metrics['recall']:.1%}). "
                    "Add more patterns or lower confidence threshold."
                )
            if metrics["precision"] < 0.7:
                recommendations.append(
                    f"Policy '{policy}' has low precision ({metrics['precision']:.1%}). "
                    "Tighten patterns or raise confidence threshold to reduce false positives."
                )

        # Layer-specific recommendations
        for layer, policies in layer_metrics.items():
            layer_avg_accuracy = sum(m["accuracy"] for m in policies.values()) / len(
                policies
            )
            if layer_avg_accuracy < 0.7:
                recommendations.append(
                    f"Layer '{layer}' has low average accuracy ({layer_avg_accuracy:.1%}). "
                    "Review layer-specific patterns and configurations."
                )

        return recommendations
