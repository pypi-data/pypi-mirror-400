"""Capture guardrails decisions from OpenTelemetry spans (advanced utility).

NOTE: This is an optional utility function. In the trace-based evaluation model,
the platform analyzes complete spans in the trace, so capturing individual
decisions is not necessary for evaluate().

This function can be used in advanced scenarios where you need programmatic
access to guardrails decisions during execution. It is NOT called automatically
by evaluate().
"""

from typing import Dict, Any
from opentelemetry import trace


def capture_guardrails_decision() -> Dict[str, Any]:
    """
    Capture the most recent guardrails decision from OpenTelemetry context.

    ADVANCED UTILITY: This reads compliance attributes stored by the guardrails
    engine's _create_compliance_audit_span() function. This function is not
    called automatically in the new trace-based model - it's available for
    advanced use cases where you need programmatic access to decisions.

    Returns:
        Dictionary with guardrails decision details:
        {
            "allowed": bool,  # Whether the request was allowed
            "confidence": float,  # Confidence score (0-1)
            "decision_layer": str,  # Which layer made the decision
            "violated_policies": List[str],  # Policies that would block
            "matched_policies": List[str],  # All policies that matched
            "blocked_reason": str,  # Reason if blocked
            "evaluation_method": str,  # How decision was made
        }

        Returns default values if no active span or span not recording.
    """
    # Get current span
    span = trace.get_current_span()
    if not span or not span.is_recording():
        # No active span, return default values
        return {
            "allowed": True,
            "confidence": 0.0,
            "decision_layer": "unknown",
            "violated_policies": [],
            "matched_policies": [],
            "blocked_reason": "",
            "evaluation_method": "allow",
        }

    # Extract compliance attributes from span
    # Note: These are set by _create_compliance_audit_span() in decision.py
    result = {
        "allowed": True,
        "confidence": 0.0,
        "decision_layer": "unknown",
        "violated_policies": [],
        "matched_policies": [],
        "blocked_reason": "",
        "evaluation_method": "allow",
    }

    # Read from span attributes if available
    # OpenTelemetry attributes are stored in the span context
    # Note: Span interface doesn't expose attributes, but SDK implementation does
    try:
        attrs = getattr(span, "attributes", {}) or {}
        result.update(
            {
                "allowed": attrs.get("compliance.decision.allowed", True),
                "confidence": attrs.get("compliance.decision.confidence", 0.0),
                "decision_layer": attrs.get("compliance.decision.layer", "unknown"),
                "violated_policies": attrs.get("compliance.policies.violated", []),
                "matched_policies": attrs.get("compliance.policies.matched", []),
                "blocked_reason": attrs.get("compliance.block.reason", ""),
                "evaluation_method": attrs.get("compliance.evaluation.method", "allow"),
            }
        )
    except Exception:
        # Fail gracefully - return defaults if anything goes wrong
        pass

    return result
