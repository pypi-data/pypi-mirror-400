"""Layer confidence metric - analyzes decision confidence per layer.

DEPRECATED: This metric is deprecated and will be removed in v2.0.

The new trace-based evaluation model evaluates on the platform using
an LLM judge analyzing complete execution traces. This metric is no
longer used by the SDK.
"""

import warnings
from typing import Dict, Any, List, Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class LayerConfidenceMetric(BaseMetric):
    """
    Analyzes confidence scores per guardrails layer.

    Helps identify:
    - Low-confidence decisions requiring LLM fallback (expensive)
    - Opportunities to add fast rules patterns (cheap)
    - Layer distribution across eval dataset
    """

    __name__ = "Layer Confidence"

    def __init__(
        self,
        min_confidence: float = 0.7,
        preferred_layers: Optional[List[str]] = None,
        threshold: Optional[float] = None,
    ):
        """
        Initialize LayerConfidenceMetric.

        Args:
            min_confidence: Minimum acceptable confidence (default: 0.7)
            preferred_layers: Preferred layers for performance (default: fast_rules, augmentation)
            threshold: Overall threshold (defaults to min_confidence)
        """
        warnings.warn(
            "LayerConfidenceMetric is deprecated and will be removed in v2.0. "
            "The new trace-based evaluation model evaluates on the platform using "
            "an LLM judge analyzing complete execution traces.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.min_confidence = min_confidence
        self.preferred_layers = preferred_layers or ["fast_rules", "augmentation"]
        self.threshold = threshold or min_confidence

        # Track layer distribution
        self.layer_counts: Dict[str, int] = {
            "fast_rules": 0,
            "augmentation": 0,
            "llm_fallback": 0,
            "default_allow": 0,
            "error": 0,
        }
        self.low_confidence_cases: List[Dict[str, Any]] = []
        self.confidence_scores: List[float] = []

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Measure confidence for this test case."""
        return self.measure(test_case)

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure confidence for this test case."""
        metadata = test_case.additional_metadata or {}
        guardrail_result = metadata.get("guardrail_result", {})

        decision_layer = guardrail_result.get("decision_layer", "unknown")
        confidence = guardrail_result.get("confidence", 0.0)

        # Track layer distribution
        if decision_layer in self.layer_counts:
            self.layer_counts[decision_layer] += 1

        # Track confidence scores
        self.confidence_scores.append(confidence)

        # Track low-confidence cases
        if confidence < self.min_confidence:
            self.low_confidence_cases.append(
                {
                    "input": test_case.input[:100],  # First 100 chars
                    "layer": decision_layer,
                    "confidence": confidence,
                    "decision": (
                        "BLOCK" if not guardrail_result.get("allowed") else "ALLOW"
                    ),
                }
            )

        # Score is confidence level
        self.score = confidence
        self.success = (
            confidence >= self.threshold and decision_layer in self.preferred_layers
        )

        return confidence

    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        avg_confidence = (
            sum(self.confidence_scores) / len(self.confidence_scores)
            if self.confidence_scores
            else 0.0
        )
        return avg_confidence >= self.threshold

    def generate_report(self) -> Dict[str, Any]:
        """Generate layer distribution report."""
        total_cases = sum(self.layer_counts.values())
        avg_confidence = (
            sum(self.confidence_scores) / len(self.confidence_scores)
            if self.confidence_scores
            else 0.0
        )

        return {
            "avg_confidence": avg_confidence,
            "layer_distribution": {
                layer: {
                    "count": count,
                    "percentage": (count / total_cases * 100) if total_cases > 0 else 0,
                }
                for layer, count in self.layer_counts.items()
            },
            "low_confidence_count": len(self.low_confidence_cases),
            "low_confidence_rate": (
                (len(self.low_confidence_cases) / total_cases * 100)
                if total_cases > 0
                else 0
            ),
            "recommendations": self._generate_recommendations(total_cases),
        }

    def _generate_recommendations(self, total_cases: int) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        llm_fallback_rate = (
            (self.layer_counts["llm_fallback"] / total_cases * 100)
            if total_cases > 0
            else 0
        )

        if llm_fallback_rate > 15:
            recommendations.append(
                f"High LLM fallback usage ({llm_fallback_rate:.1f}%). "
                f"Consider adding more fast rules patterns to reduce costs."
            )

        if len(self.low_confidence_cases) > 0:
            recommendations.append(
                f"Found {len(self.low_confidence_cases)} low-confidence decisions. "
                f"Review these cases to improve policy definitions."
            )

        return recommendations
