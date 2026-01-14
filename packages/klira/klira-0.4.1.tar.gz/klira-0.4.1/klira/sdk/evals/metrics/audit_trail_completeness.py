"""Audit trail completeness metric - verifies complete audit trails in OpenTelemetry spans.

DEPRECATED: This metric is deprecated and will be removed in v2.0.

The new trace-based evaluation model evaluates on the platform using
an LLM judge analyzing complete execution traces. This metric is no
longer used by the SDK.
"""

import warnings
from typing import Dict, Any, List, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class AuditTrailCompletenessMetric(BaseMetric):
    """
    Verifies complete audit trails in OpenTelemetry spans.

    For compliance (SOC 2, GDPR, HIPAA), every guardrails decision must
    have a complete audit trail with required attributes:
    - compliance.decision.allowed
    - compliance.decision.confidence
    - compliance.decision.layer
    - compliance.policies.violated
    - compliance.policies.matched
    - compliance.block.reason (if blocked)
    - decision.evaluation.method

    This metric validates span completeness and generates compliance
    readiness scores.
    """

    __name__ = "Audit Trail Completeness"

    # Required attributes for compliance audit trails
    REQUIRED_ATTRIBUTES = {
        "allowed",
        "confidence",
        "decision_layer",
    }

    # Optional but recommended attributes
    RECOMMENDED_ATTRIBUTES = {
        "violated_policies",
        "matched_policies",
        "blocked_reason",
        "evaluation_method",
    }

    def __init__(
        self,
        require_all_attributes: bool = False,
        min_completeness: float = 0.80,
        threshold: Optional[float] = None,
    ):
        """
        Initialize AuditTrailCompletenessMetric.

        Args:
            require_all_attributes: If True, require both required and recommended attributes
            min_completeness: Minimum completeness score
            threshold: Overall threshold (defaults to min_completeness)
        """
        warnings.warn(
            "AuditTrailCompletenessMetric is deprecated and will be removed in v2.0. "
            "The new trace-based evaluation model evaluates on the platform using "
            "an LLM judge analyzing complete execution traces.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.require_all_attributes = require_all_attributes
        self.min_completeness = min_completeness
        self.threshold = threshold or min_completeness

        # Track attribute completeness
        self.total_test_cases = 0
        self.complete_trails = 0
        self.incomplete_trails = 0
        self.missing_attributes: Dict[str, int] = {}

        # Track incomplete cases for review
        self.incomplete_cases: List[Dict[str, Any]] = []

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Measure audit trail completeness for this test case."""
        return self.measure(test_case)

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure audit trail completeness for this test case."""
        self.total_test_cases += 1

        metadata = test_case.additional_metadata or {}
        guardrail_result = metadata.get("guardrail_result", {})

        # Check for required attributes
        missing_required = self._check_required_attributes(guardrail_result)

        # Check for recommended attributes
        missing_recommended = self._check_recommended_attributes(guardrail_result)

        # Determine completeness
        if self.require_all_attributes:
            # Must have all required + recommended
            is_complete = len(missing_required) == 0 and len(missing_recommended) == 0
            missing = missing_required + missing_recommended
        else:
            # Only required attributes matter
            is_complete = len(missing_required) == 0
            missing = missing_required

        # Update counters
        if is_complete:
            self.complete_trails += 1
            score = 1.0
        else:
            self.incomplete_trails += 1
            score = 0.0

            # Track missing attributes
            for attr in missing:
                self.missing_attributes[attr] = self.missing_attributes.get(attr, 0) + 1

            # Record incomplete case
            self.incomplete_cases.append(
                {
                    "input": test_case.input[:100],
                    "missing_attributes": missing,
                    "guardrail_result": guardrail_result,
                }
            )

        # Calculate overall completeness score
        completeness = (
            self.complete_trails / self.total_test_cases
            if self.total_test_cases > 0
            else 0.0
        )

        self.score = completeness
        self.success = completeness >= self.threshold

        return score

    def _check_required_attributes(self, guardrail_result: Dict[str, Any]) -> List[str]:
        """Check for required audit trail attributes."""
        missing = []

        for attr in self.REQUIRED_ATTRIBUTES:
            if attr not in guardrail_result or guardrail_result[attr] is None:
                missing.append(attr)

        return missing

    def _check_recommended_attributes(
        self, guardrail_result: Dict[str, Any]
    ) -> List[str]:
        """Check for recommended audit trail attributes."""
        missing = []

        for attr in self.RECOMMENDED_ATTRIBUTES:
            if attr not in guardrail_result or guardrail_result[attr] is None:
                missing.append(attr)

        return missing

    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return bool(getattr(self, "success", False))

    def generate_report(self) -> Dict[str, Any]:
        """Generate audit trail completeness report."""
        completeness = (
            self.complete_trails / self.total_test_cases
            if self.total_test_cases > 0
            else 0.0
        )

        # Calculate compliance readiness score
        compliance_score = self._calculate_compliance_score()

        return {
            "completeness": completeness,
            "compliance_readiness_score": compliance_score,
            "total_test_cases": self.total_test_cases,
            "complete_trails": self.complete_trails,
            "incomplete_trails": self.incomplete_trails,
            "missing_attributes_frequency": self.missing_attributes,
            "incomplete_cases": self.incomplete_cases[:10],  # First 10
            "recommendations": self._generate_recommendations(
                completeness, compliance_score
            ),
        }

    def _calculate_compliance_score(self) -> Dict[str, str]:
        """Calculate compliance readiness for major standards."""
        completeness = (
            self.complete_trails / self.total_test_cases
            if self.total_test_cases > 0
            else 0.0
        )

        # Define compliance thresholds
        scores = {}

        # SOC 2 (requires comprehensive audit trails)
        if completeness >= 0.95:
            scores["SOC2"] = "Ready"
        elif completeness >= 0.85:
            scores["SOC2"] = "Needs Improvement"
        else:
            scores["SOC2"] = "Not Ready"

        # GDPR (requires decision explanations)
        # Check if decision reasoning is captured
        has_reasoning = "evaluation_method" not in self.missing_attributes
        if completeness >= 0.90 and has_reasoning:
            scores["GDPR"] = "Ready"
        elif completeness >= 0.75:
            scores["GDPR"] = "Needs Improvement"
        else:
            scores["GDPR"] = "Not Ready"

        # HIPAA (requires complete audit trails for PHI decisions)
        if completeness >= 0.98:
            scores["HIPAA"] = "Ready"
        elif completeness >= 0.90:
            scores["HIPAA"] = "Needs Improvement"
        else:
            scores["HIPAA"] = "Not Ready"

        return scores

    def _generate_recommendations(
        self, completeness: float, compliance_scores: Dict[str, str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Overall completeness
        if completeness < 0.7:
            recommendations.append(
                f"Low audit trail completeness ({completeness:.1%}). "
                "Review guardrails engine to ensure all attributes are captured."
            )
        elif completeness < 0.95:
            recommendations.append(
                f"Moderate audit trail completeness ({completeness:.1%}). "
                "Address missing attributes to improve compliance readiness."
            )
        else:
            recommendations.append(
                f"Excellent audit trail completeness ({completeness:.1%}). "
                "Audit trails meet compliance standards."
            )

        # Missing attributes
        if self.missing_attributes:
            top_missing = sorted(
                self.missing_attributes.items(), key=lambda x: x[1], reverse=True
            )[:3]
            missing_str = ", ".join(
                [f"{attr} ({count})" for attr, count in top_missing]
            )
            recommendations.append(
                f"Most frequently missing attributes: {missing_str}. "
                "Ensure guardrails engine populates these fields."
            )

        # Compliance-specific recommendations
        for standard, status in compliance_scores.items():
            if status == "Not Ready":
                recommendations.append(
                    f"{standard} compliance not ready. "
                    f"Improve audit trail completeness to meet {standard} requirements."
                )
            elif status == "Needs Improvement":
                recommendations.append(
                    f"{standard} compliance needs improvement. "
                    f"Address gaps to achieve {standard} compliance."
                )

        return recommendations
