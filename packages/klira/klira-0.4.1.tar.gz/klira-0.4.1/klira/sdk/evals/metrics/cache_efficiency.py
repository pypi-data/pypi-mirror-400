"""Cache efficiency metric - analyzes LLM fallback cache performance.

DEPRECATED: This metric is deprecated and will be removed in v2.0.

The new trace-based evaluation model evaluates on the platform using
an LLM judge analyzing complete execution traces. This metric is no
longer used by the SDK.
"""

import warnings
from typing import Dict, Any, List, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class CacheEfficiencyMetric(BaseMetric):
    """
    Analyzes LLM fallback cache performance.

    The guardrails engine uses semantic caching for expensive LLM fallback
    decisions. This metric measures:
    - Cache hit rate (% of LLM calls avoided)
    - Cost savings from caching
    - Opportunities for cache warming
    - Cache-eligible decisions that missed

    Key insights for cost optimization.
    """

    __name__ = "Cache Efficiency"

    def __init__(
        self,
        min_hit_rate: float = 0.30,
        llm_cost_per_call: float = 0.001,  # $0.001 per LLM call (example)
        threshold: Optional[float] = None,
    ):
        """
        Initialize CacheEfficiencyMetric.

        Args:
            min_hit_rate: Minimum acceptable cache hit rate
            llm_cost_per_call: Cost per LLM fallback call (for savings calculation)
            threshold: Overall threshold (defaults to min_hit_rate)
        """
        warnings.warn(
            "CacheEfficiencyMetric is deprecated and will be removed in v2.0. "
            "The new trace-based evaluation model evaluates on the platform using "
            "an LLM judge analyzing complete execution traces.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.min_hit_rate = min_hit_rate
        self.llm_cost_per_call = llm_cost_per_call
        self.threshold = threshold or min_hit_rate

        # Track cache performance
        self.llm_fallback_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.non_llm_decisions = 0

        # Track similar inputs that could benefit from caching
        self.similar_inputs: List[str] = []

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Measure cache efficiency for this test case."""
        return self.measure(test_case)

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure cache efficiency for this test case."""
        metadata = test_case.additional_metadata or {}
        guardrail_result = metadata.get("guardrail_result", {})
        decision_layer = guardrail_result.get("decision_layer", "")
        cache_hit = guardrail_result.get("cache_hit", False)

        # Only track LLM fallback layer
        if decision_layer == "llm_fallback":
            self.llm_fallback_count += 1

            if cache_hit:
                self.cache_hits += 1
                score = 1.0  # Cache hit is good
            else:
                self.cache_misses += 1
                score = 0.0  # Cache miss (expensive LLM call)

                # Track input for potential cache warming
                self.similar_inputs.append(test_case.input[:100])
        else:
            self.non_llm_decisions += 1
            score = None  # Not applicable

        # Calculate overall cache hit rate
        hit_rate = self._calculate_hit_rate()

        self.score = hit_rate if hit_rate is not None else 0.0
        self.success = hit_rate >= self.threshold if hit_rate is not None else False

        return score if score is not None else 0.0

    def _calculate_hit_rate(self) -> Optional[float]:
        """Calculate cache hit rate."""
        if self.llm_fallback_count == 0:
            return None  # No LLM fallback decisions to measure

        return self.cache_hits / self.llm_fallback_count

    def _calculate_cost_savings(self) -> Dict[str, float]:
        """Calculate cost savings from caching."""
        # Cost if no caching (all LLM calls)
        cost_without_cache = self.llm_fallback_count * self.llm_cost_per_call

        # Actual cost (only cache misses)
        actual_cost = self.cache_misses * self.llm_cost_per_call

        # Savings
        savings = cost_without_cache - actual_cost
        savings_percentage = (
            (savings / cost_without_cache * 100) if cost_without_cache > 0 else 0.0
        )

        return {
            "cost_without_cache": cost_without_cache,
            "actual_cost": actual_cost,
            "savings": savings,
            "savings_percentage": savings_percentage,
        }

    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return bool(getattr(self, "success", False))

    def generate_report(self) -> Dict[str, Any]:
        """Generate cache efficiency report."""
        hit_rate = self._calculate_hit_rate()
        cost_analysis = self._calculate_cost_savings()

        return {
            "hit_rate": hit_rate,
            "llm_fallback_count": self.llm_fallback_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "non_llm_decisions": self.non_llm_decisions,
            "cost_analysis": cost_analysis,
            "cache_miss_inputs": self.similar_inputs[:10],  # First 10
            "recommendations": self._generate_recommendations(hit_rate, cost_analysis),
        }

    def _generate_recommendations(
        self, hit_rate: Optional[float], cost_analysis: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if hit_rate is None:
            recommendations.append(
                "No LLM fallback decisions detected. "
                "Either policies are well-defined (good!) or test coverage is insufficient."
            )
            return recommendations

        # Cache hit rate recommendations
        if hit_rate < 0.2:
            recommendations.append(
                f"Very low cache hit rate ({hit_rate:.1%}). "
                "Consider implementing cache warming for common queries."
            )
        elif hit_rate < 0.5:
            recommendations.append(
                f"Moderate cache hit rate ({hit_rate:.1%}). "
                "Review cache miss patterns to improve hit rate."
            )
        else:
            recommendations.append(
                f"Good cache hit rate ({hit_rate:.1%}). "
                "Cache is effectively reducing LLM calls."
            )

        # Cost savings recommendations
        savings_pct = cost_analysis["savings_percentage"]
        if savings_pct > 0:
            recommendations.append(
                f"Cache saved {savings_pct:.1f}% in LLM costs "
                f"(${cost_analysis['savings']:.4f} out of ${cost_analysis['cost_without_cache']:.4f})."
            )

        # Potential optimization
        if self.cache_misses > 10:
            recommendations.append(
                f"Found {self.cache_misses} cache misses. "
                "Review similar inputs to identify patterns for cache warming."
            )

        # Overall LLM fallback usage
        total_decisions = self.llm_fallback_count + self.non_llm_decisions
        if total_decisions > 0:
            llm_fallback_rate = self.llm_fallback_count / total_decisions
            if llm_fallback_rate > 0.3:
                recommendations.append(
                    f"High LLM fallback rate ({llm_fallback_rate:.1%}). "
                    "Consider adding more fast rules patterns to reduce expensive LLM calls."
                )

        return recommendations
