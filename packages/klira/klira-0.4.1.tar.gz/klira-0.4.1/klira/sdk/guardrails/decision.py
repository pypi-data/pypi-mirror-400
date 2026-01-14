"""Handles the decision routing logic for the GuardrailsEngine.

This module takes results from different guardrail layers (fast rules, augmentation,
LLM fallback) and determines the final action based on predefined sequences.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, Optional, List, Union
import re  # Import re for Pattern type check

# Import necessary components and types
from .fast_rules import FastRulesEngine, FastRulesEvaluationResult
from klira.sdk.performance import timed_operation
from .policy_augmentation import (
    PolicyAugmentation,
)  # Deprecated, kept for backward compatibility
from .llm_fallback import LLMFallback  # LLMEvaluationResult is imported below
from .llm_service import LLMEvaluationResult  # Import the actual type definition

# Import result types from the new types module
from .types import GuardrailProcessingResult, GuardrailOutputCheckResult

logger = logging.getLogger("klira.guardrails.decision")

# --- Guidelines Cache for Cross-Span Access ---
# This cache stores guidelines by conversation ID so they can be accessed
# across different OpenTelemetry spans during the same conversation

_guidelines_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.RLock()
_cache_ttl_seconds = 300  # 5 minutes TTL


def _store_guidelines_in_cache(conversation_id: str, guidelines: List[str]) -> None:
    """Store guidelines in a persistent cache with TTL."""
    with _cache_lock:
        _guidelines_cache[conversation_id] = {
            "guidelines": guidelines,
            "timestamp": time.time(),
        }


def _get_guidelines_from_cache(conversation_id: str) -> Optional[List[str]]:
    """Retrieve guidelines from cache if not expired."""
    with _cache_lock:
        if conversation_id in _guidelines_cache:
            entry = _guidelines_cache[conversation_id]
            if time.time() - entry["timestamp"] < _cache_ttl_seconds:
                guidelines = entry["guidelines"]
                # Ensure we return the correct type
                if isinstance(guidelines, list):
                    return guidelines
            else:
                # Remove expired entry
                del _guidelines_cache[conversation_id]
    return None


def _clear_guidelines_from_cache(conversation_id: str) -> None:
    """Clear guidelines from cache for a specific conversation."""
    with _cache_lock:
        _guidelines_cache.pop(conversation_id, None)


def _cleanup_expired_cache_entries() -> None:
    """Clean up expired cache entries."""
    current_time = time.time()
    with _cache_lock:
        expired_keys = [
            conv_id
            for conv_id, entry in _guidelines_cache.items()
            if current_time - entry["timestamp"] >= _cache_ttl_seconds
        ]
        for key in expired_keys:
            del _guidelines_cache[key]


# --- Helper Function to Sanitize Results ---


def _sanitize_dict_for_json(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively remove non-serializable items like re.Pattern."""
    if data is None:
        return None

    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized_value = _sanitize_dict_for_json(value)
            if sanitized_value is not None:
                sanitized[key] = sanitized_value
        elif isinstance(value, list):
            sanitized_value = _sanitize_list_for_json(value)  # type: ignore[assignment]
            if sanitized_value is not None:
                sanitized[key] = sanitized_value
        elif not isinstance(value, re.Pattern):
            sanitized[key] = value
        # else: skip re.Pattern objects
    return sanitized


def _sanitize_list_for_json(data: Optional[List[Any]]) -> Optional[List[Any]]:
    """Recursively sanitize lists for JSON serialization."""
    if data is None:
        return None

    sanitized = []
    for item in data:
        if isinstance(item, dict):
            sanitized_item = _sanitize_dict_for_json(item)
            if sanitized_item is not None:
                sanitized.append(sanitized_item)
        elif isinstance(item, list):
            sanitized_item = _sanitize_list_for_json(item)  # type: ignore[assignment]
            if sanitized_item is not None:
                sanitized.append(sanitized_item)
        elif not isinstance(item, re.Pattern):
            sanitized.append(item)
        # else: skip re.Pattern objects
    return sanitized


def _sanitize_typed_dict_for_json(data: Any) -> Optional[Dict[str, Any]]:
    """Convert TypedDict or dict-like objects to sanitized dict for JSON serialization."""
    if data is None:
        return None

    # Convert TypedDict to regular dict
    if hasattr(data, "_asdict"):
        # For NamedTuple-like objects
        data_dict = data._asdict()
    elif isinstance(data, dict):
        # For regular dicts and TypedDict instances
        data_dict = dict(data)
    else:
        # For other objects, try to convert to dict
        try:
            data_dict = dict(data)
        except (TypeError, ValueError):
            # If conversion fails, return None
            return None

    return _sanitize_dict_for_json(data_dict)


# --- Compliance Audit Span Helper ---


def _create_compliance_audit_span(
    result: Union[
        GuardrailProcessingResult, GuardrailOutputCheckResult, Dict[str, Any]
    ],
    direction: str,
    message_content: str,
    context: Dict[str, Any],
) -> None:
    """Create a compliance audit span for the guardrails decision.

    This span is linked to any active parent span (typically an LLM request span)
    to create a complete audit trail from policy evaluation to LLM execution.

    Args:
        result: The decision result (GuardrailProcessingResult or GuardrailOutputCheckResult)
        direction: Direction of evaluation ("inbound" or "outbound")
        message_content: The message or response content that was evaluated
        context: The processing context
    """
    from klira.sdk.utils.span_utils import safe_set_span_attribute
    from opentelemetry import trace
    from opentelemetry.trace import StatusCode, Link

    tracer = trace.get_tracer("klira.guardrails.compliance")

    # Capture current span context for linking
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context() if current_span else None

    # Create compliance audit span with link to parent span if available
    links = []
    if span_context and span_context.is_valid:
        links.append(Link(span_context))
        logger.debug(
            f"Linking compliance audit span to parent span: {span_context.span_id}"
        )

    # Determine span name based on decision type
    decision_layer = result.get("decision_layer", "unknown")
    span_name_map = {
        "fast_rules_blocked": "klira.compliance.blocked",
        "augmentation": "klira.compliance.augmented",
        "default_allow": "klira.compliance.allowed",
        "llm_fallback_blocked": "klira.compliance.llm_fallback",
        "llm_fallback_allowed": "klira.compliance.llm_fallback",
    }
    span_name = span_name_map.get(decision_layer, "klira.compliance.audit")

    # Start span with links (if any)
    if links:
        audit_span_context_manager = tracer.start_as_current_span(
            name=span_name, links=links
        )
    else:
        audit_span_context_manager = tracer.start_as_current_span(name=span_name)

    with audit_span_context_manager as audit_span:
        # Basic audit attributes
        audit_attributes = {
            "compliance.direction": direction,
            "compliance.decision.allowed": result.get("allowed", False),
            "compliance.decision.action": "allow" if result.get("allowed") else "block",
            # PROD-254 Phase 3: Removed deprecated compliance.decision.confidence
            "compliance.input_length": len(message_content),
        }

        # Add evaluation method
        if "evaluation_method" in result:
            audit_attributes["compliance.evaluation.method"] = result[
                "evaluation_method"
            ]

        # Add decision layer
        if "decision_layer" in result:
            audit_attributes["compliance.decision.layer"] = result["decision_layer"]

        # Add context (truncated)
        if context:
            context_str = str(context)[:500]
            audit_attributes["compliance.context"] = context_str

        # Add policy information for inbound (matched policies) - only exists in GuardrailProcessingResult
        if "applied_policies" in result:
            applied_policies = result.get("applied_policies")
            if applied_policies and isinstance(applied_policies, list):
                audit_attributes["compliance.policies.matched"] = applied_policies[:10]
                audit_attributes["compliance.policies.matched_count"] = len(
                    applied_policies
                )

        # Add violated policies information
        if "violated_policies" in result and result["violated_policies"]:
            audit_attributes["compliance.policies.violated"] = result[
                "violated_policies"
            ][:10]
            audit_attributes["compliance.policies.violated_count"] = len(
                result["violated_policies"]
            )

        # Add block reason if blocked
        if not result.get("allowed") and "blocked_reason" in result:
            blocked_reason = result["blocked_reason"]
            audit_attributes["compliance.block.reason"] = (
                blocked_reason[:500] if blocked_reason else ""
            )

        # Add augmentation details if present
        is_augmented = decision_layer == "augmentation"
        audit_attributes["guardrails.augmentation_applied"] = is_augmented

        if is_augmented:
            # Get guidelines from fast_rules_result for augmented decisions
            fast_rules_result = result.get("fast_rules_result", {})
            if fast_rules_result:
                guidelines = fast_rules_result.get("all_guidelines", [])
                augmentation_policies = fast_rules_result.get(
                    "augmentation_policies", []
                )
            else:
                guidelines = []
                augmentation_policies = []

            if guidelines:
                audit_attributes["guardrails.guidelines_count"] = len(guidelines)
                audit_attributes["guardrails.guidelines"] = "\n".join(guidelines[:10])

            if augmentation_policies:
                audit_attributes["guardrails.augmentation_policies"] = (
                    augmentation_policies[:10]
                )
                audit_attributes["guardrails.augmentation_policies_count"] = len(
                    augmentation_policies
                )

        # Legacy augmentation_result support (deprecated)
        if "augmentation_result" in result:
            aug_result = result.get("augmentation_result")
            if (
                aug_result
                and isinstance(aug_result, dict)
                and "matched_policies" in aug_result
            ):
                matched = aug_result["matched_policies"]
                if matched and isinstance(matched, list):
                    policy_names = [
                        p.get("id", p.get("name", "unknown")) for p in matched[:10]
                    ]
                    audit_attributes["compliance.augmentation.policies"] = policy_names
                    audit_attributes["compliance.augmentation.policies_count"] = len(
                        matched
                    )

        # Add blocking-specific attributes
        if not result.get("allowed"):
            fast_rules_result = result.get("fast_rules_result", {})
            if fast_rules_result:
                blocking_policies = fast_rules_result.get("blocking_policies", [])
            else:
                blocking_policies = []
            if blocking_policies:
                audit_attributes["guardrails.blocking_policies"] = blocking_policies[
                    :10
                ]
                audit_attributes["guardrails.blocking_policies_count"] = len(
                    blocking_policies
                )

        # Add LLM fallback indicator
        if "llm_fallback" in decision_layer:
            audit_attributes["guardrails.llm_fallback_used"] = True

        # Set all attributes at once
        for key, value in audit_attributes.items():
            safe_set_span_attribute(audit_span, key, value)

        # Set span status
        audit_span.set_status(StatusCode.OK)


async def _create_compliance_audit_span_async(
    result: Union[
        GuardrailProcessingResult, GuardrailOutputCheckResult, Dict[str, Any]
    ],
    direction: str,
    message_content: str,
    context: Dict[str, Any],
) -> None:
    """Create compliance audit span asynchronously (non-blocking).

    This wrapper allows span creation to happen in the background without
    blocking the response. Reduces guardrails latency from 10-50ms to <5ms.

    Args:
        result: The decision result
        direction: Direction of evaluation ("inbound" or "outbound")
        message_content: The message or response content that was evaluated
        context: The processing context
    """
    try:
        _create_compliance_audit_span(result, direction, message_content, context)
    except Exception as e:
        logger.error(f"Failed to create compliance audit span asynchronously: {e}")


def _schedule_compliance_span_async(
    result: Union[
        GuardrailProcessingResult, GuardrailOutputCheckResult, Dict[str, Any]
    ],
    direction: str,
    message_content: str,
    context: Dict[str, Any],
) -> None:
    """Schedule compliance span creation asynchronously if possible.

    Tries to create the span in the background using asyncio. Falls back
    to synchronous creation if no event loop is available.

    Args:
        result: The decision result
        direction: Direction of evaluation
        message_content: The message content
        context: The processing context
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Event loop is running - create task for async span creation
            loop.create_task(
                _create_compliance_audit_span_async(
                    result, direction, message_content, context
                )
            )
            logger.debug("Scheduled compliance audit span creation asynchronously")
            return
    except RuntimeError:
        # No event loop running - fall back to sync creation
        logger.debug("No event loop available, creating compliance span synchronously")

    # Fallback: create span synchronously
    _create_compliance_audit_span(result, direction, message_content, context)


# --- Decision Routing Functions ---


async def route_message_decision(
    message: str,
    context: Dict[str, Any],
    fast_rules_engine: Optional[FastRulesEngine],
    augmentation_engine: Optional[PolicyAugmentation],  # Deprecated, not used
    llm_fallback_engine: Optional[LLMFallback],
) -> GuardrailProcessingResult:
    """Routes the decision logic for processing input messages.

    Simplified architecture (PROD-243):
    Executes the sequence: Fast Rules (single layer) -> LLM Fallback (if configured) -> Default Allow.

    Args:
        message: The input message.
        context: The processing context (will be updated with intermediate results).
        fast_rules_engine: Initialized FastRulesEngine instance.
        augmentation_engine: Deprecated, not used (guideline extraction now in Fast Rules).
        llm_fallback_engine: Initialized LLMFallback instance (only runs if enabled in config).

    Returns:
        The final GuardrailProcessingResult.
    """
    # Get parent span BEFORE entering timed_operation to set augmentation attributes on it
    from klira.sdk.tracing.tracing import get_current_span

    parent_span = get_current_span()

    with timed_operation("route_decision", "guardrails"):
        from klira.sdk.config import get_config

        conversation_id = context.get("conversation_id", "unknown")
        config = get_config()
        direction = context.get("direction", "inbound")

        # --- Step 1: Fast Rules (single layer evaluation) ---
        if not fast_rules_engine:
            logger.warning(
                f"[{conversation_id}] DecisionRouter: No fast_rules_engine provided. Defaulting to allow."
            )
            result = GuardrailProcessingResult(
                allowed=True,
                confidence=0.0,
                decision_layer="default_allow",
                evaluation_method="none",
            )
            # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
            _schedule_compliance_span_async(result, direction, message, context)
            return result

        logger.debug(
            f"[{conversation_id}] DecisionRouter: Evaluating with FastRules..."
        )
        fast_result = fast_rules_engine.evaluate(message, direction, context)

        # --- Step 2: Check for blocking policies ---
        if fast_result["blocking_policies"]:
            blocking_policy_id = fast_result["blocking_policies"][0]
            logger.info(
                f"[{conversation_id}] DecisionRouter: Blocked by FastRules (Policy: {blocking_policy_id})."
            )

            # Find the violation response from the first blocking policy
            violation_response = "Request blocked by guardrails."
            for policy_match in fast_result["matched_policies"]:
                if policy_match["policy_id"] == blocking_policy_id:
                    # Try to get violation_response from policy (would need to be added to PolicyMatch)
                    # For now, use a default message
                    violation_response = (
                        f"Policy '{blocking_policy_id}' blocked this request."
                    )
                    break

            result = GuardrailProcessingResult(
                allowed=False,
                confidence=1.0,  # Blocking is absolute (no confidence levels)
                decision_layer="fast_rules",
                evaluation_method="fast_rules",
                violated_policies=fast_result["blocking_policies"],
                blocked_reason=violation_response,
                fast_rules_result=_sanitize_typed_dict_for_json(fast_result),
            )
            # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
            _schedule_compliance_span_async(result, direction, message, context)
            return result

        # --- Step 3: Check for augmentation policies (action="allow" with guidelines) ---
        if fast_result["augmentation_policies"]:
            guidelines = fast_result["all_guidelines"]
            logger.info(
                f"[{conversation_id}] DecisionRouter: {len(fast_result['augmentation_policies'])} augmentation policies matched. "
                f"Storing {len(guidelines)} guidelines."
            )

            # Store guidelines for adapter injection
            try:
                # Store in simple storage for decorator access
                from klira.sdk.decorators.guardrails import _set_current_guidelines

                _set_current_guidelines(guidelines)

                # Also store in OTel context as backup
                from opentelemetry import context as otel_context

                current_ctx = otel_context.get_current()
                new_ctx = otel_context.set_value(
                    "klira.augmentation.guidelines", guidelines, current_ctx
                )
                otel_context.attach(new_ctx)

                # Add augmentation attributes to parent span for tracking
                from klira.sdk.utils.span_utils import safe_set_span_attribute

                if parent_span:
                    safe_set_span_attribute(
                        parent_span, "klira.guardrails.augmentation.applied", True
                    )
                    safe_set_span_attribute(
                        parent_span,
                        "klira.guardrails.augmentation.policies_count",
                        len(fast_result["augmentation_policies"]),
                    )
                    safe_set_span_attribute(
                        parent_span,
                        "klira.guardrails.augmentation.policy_names",
                        fast_result["augmentation_policies"][:10],  # First 10
                    )

                    # Store formatted guidelines sample (first 500 chars)
                    formatted_guidelines = "\n".join(guidelines)
                    guidelines_sample = (
                        formatted_guidelines[:500]
                        if len(formatted_guidelines) > 500
                        else formatted_guidelines
                    )
                    safe_set_span_attribute(
                        parent_span,
                        "klira.guardrails.augmentation.guidelines_sample",
                        guidelines_sample,
                    )

            except Exception as e:
                logger.warning(
                    f"[{conversation_id}] DecisionRouter: Failed to store guidelines: {e}"
                )

            # Build matched policies list from fast_rules_result for augmentation_result
            # Issues 251/252: Extract full policy details including guidelines from original policies
            matched_policies_for_aug = []
            if fast_rules_engine:
                # Get original policy objects to extract full details including guidelines
                for policy_match in fast_result.get("matched_policies", []):
                    if isinstance(policy_match, dict):
                        policy_id = policy_match.get("policy_id")
                        if policy_id in fast_result["augmentation_policies"]:
                            # Find the original policy object to get full details
                            original_policy = None
                            for policy in fast_rules_engine.policies:
                                if policy.get("id") == policy_id:
                                    original_policy = policy
                                    break

                            # Build matched policy dict with full details
                            matched_policy_dict = {
                                "id": policy_id,
                                "action": policy_match.get("action", "allow"),
                                "matched_patterns": policy_match.get(
                                    "matched_patterns", []
                                ),
                            }

                            # Include guidelines from original policy if available
                            if original_policy:
                                policy_guidelines = original_policy.get(
                                    "guidelines", []
                                )
                                if policy_guidelines:
                                    matched_policy_dict["guidelines"] = (
                                        policy_guidelines
                                    )

                            matched_policies_for_aug.append(matched_policy_dict)

            # Create augmentation_result with guidelines and matched policies (Issues 251/252 fix)
            augmentation_result = {
                "matched_policies": matched_policies_for_aug,
                "extracted_guidelines": guidelines,
            }

            result = GuardrailProcessingResult(
                allowed=True,
                confidence=1.0,  # High confidence when policies match
                decision_layer="policy_augmentation",
                evaluation_method="fast_rules",
                applied_policies=fast_result["augmentation_policies"],
                fast_rules_result=_sanitize_typed_dict_for_json(fast_result),
                augmentation_result=augmentation_result,  # Issues 251/252: Include augmentation_result with guidelines
            )
            # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
            _schedule_compliance_span_async(result, direction, message, context)
            return result

        # --- Step 4: No policies matched - check LLM fallback configuration ---
        if (
            config.llm_fallback_enabled
            and config.llm_fallback_provider
            and config.llm_fallback_model
            and config.llm_fallback_api_key
            and llm_fallback_engine  # Engine should always be initialized, but check for safety
        ):
            logger.debug(
                f"[{conversation_id}] DecisionRouter: No policies matched. Running LLM fallback evaluation."
            )
            # Convert FastRulesEvaluationResult to dict for LLM fallback
            fast_result_dict = dict(fast_result)
            llm_eval_result = await llm_fallback_engine.evaluate(
                message, context, fast_result_dict
            )

            if not llm_eval_result["allowed"]:
                logger.info(
                    f"[{conversation_id}] DecisionRouter: Blocked by LLM fallback."
                )
                result = GuardrailProcessingResult(
                    allowed=False,
                    confidence=llm_eval_result.get("confidence", 0.9),
                    decision_layer="llm_fallback",
                    evaluation_method="llm_fallback",
                    violated_policies=llm_eval_result.get("violated_policies", []),
                    blocked_reason=llm_eval_result.get(
                        "reasoning", "Blocked by LLM evaluation."
                    ),
                    llm_evaluation_result=llm_eval_result,
                    fast_rules_result=_sanitize_typed_dict_for_json(fast_result),
                )
                # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
                _schedule_compliance_span_async(result, direction, message, context)
                return result

            logger.debug(
                f"[{conversation_id}] DecisionRouter: LLM fallback allowed request."
            )
        elif config.llm_fallback_enabled:
            logger.warning(
                f"[{conversation_id}] DecisionRouter: LLM fallback enabled but not fully configured. "
                "Skipping LLM evaluation. Required: provider, model, api_key."
            )

        # --- Step 5: Default Allow (no matches, no LLM fallback) ---
        logger.debug(
            f"[{conversation_id}] DecisionRouter: No blocking policies, no augmentation. Defaulting to allow."
        )
        final_result = GuardrailProcessingResult(
            allowed=True,
            confidence=0.0,  # Low confidence - no policies matched
            decision_layer="default_allow",
            evaluation_method="fast_rules",
            fast_rules_result=_sanitize_typed_dict_for_json(fast_result),
        )

        # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
        _schedule_compliance_span_async(final_result, direction, message, context)
        return final_result


async def route_output_decision(
    ai_response: str,
    context: Dict[str, Any],
    fast_rules_engine: Optional[FastRulesEngine],
    llm_fallback_engine: Optional[LLMFallback],
) -> GuardrailOutputCheckResult:
    """Routes the decision logic for checking AI output.

    Executes the sequence: Fast Rules -> LLM Fallback -> Default.

    Args:
        ai_response: The AI response text.
        context: The processing context.
        fast_rules_engine: Initialized FastRulesEngine instance.
        llm_fallback_engine: Initialized LLMFallback instance.

    Returns:
        The final GuardrailOutputCheckResult.
    """
    with timed_operation("route_decision", "guardrails"):
        conversation_id = context.get("conversation_id", "unknown")
        final_result: Optional[GuardrailOutputCheckResult] = None
        fast_result: Optional[FastRulesEvaluationResult] = None
        llm_eval_result: Optional[LLMEvaluationResult] = None

        # --- Step 1: Fast Rules (using new simplified structure) ---
        if fast_rules_engine:
            logger.debug(
                f"[{conversation_id}] DecisionRouter: Evaluating output with FastRules..."
            )
            # Output evaluation is always outbound direction
            fast_result = fast_rules_engine.evaluate(ai_response, "outbound", context)

            # Check for blocking policies (new structure)
            if fast_result["blocking_policies"]:
                blocking_policy_id = fast_result["blocking_policies"][0]
                logger.info(
                    f"[{conversation_id}] DecisionRouter: Output blocked by FastRules (Policy: {blocking_policy_id})."
                )
                # Return result immediately if blocked by a specific fast rule
                # TODO: Implement redaction based on fast rule matches if possible/needed
                final_result = GuardrailOutputCheckResult(
                    allowed=False,
                    confidence=1.0,  # Blocking is absolute (no confidence levels)
                    decision_layer="fast_rules",
                    evaluation_method="fast_rules",
                    violated_policies=fast_result["blocking_policies"],
                    blocked_reason=f"Harmful content related to policy '{blocking_policy_id}' detected in output by fast rules.",
                    fast_rules_result=_sanitize_typed_dict_for_json(fast_result),
                    # transformed_response=... # Add if redaction implemented
                )
                # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
                _schedule_compliance_span_async(
                    final_result, "outbound", ai_response, context
                )
                return final_result  # Early exit

        # --- Step 2: LLM Fallback ---
        # Check if LLM fallback is enabled and configured (same pattern as inbound)
        from klira.sdk.config import get_config

        config = get_config()
        if (
            config.llm_fallback_enabled
            and config.llm_fallback_provider
            and config.llm_fallback_model
            and config.llm_fallback_api_key
            and llm_fallback_engine  # Engine should always be initialized, but check for safety
        ):
            logger.debug(
                f"[{conversation_id}] DecisionRouter: Evaluating output with LLMFallback..."
            )
            # Convert FastRulesEvaluationResult to dict for LLM fallback
            fast_result_dict = dict(fast_result) if fast_result else None
            llm_eval_result = await llm_fallback_engine.evaluate(
                ai_response, context, fast_result_dict
            )
            if not llm_eval_result["allowed"] or llm_eval_result["action"] != "allow":
                logger.info(
                    f"[{conversation_id}] DecisionRouter: Output action '{llm_eval_result['action']}' determined by LLMFallback."
                )
                transformed = None
                if llm_eval_result["action"] == "transform":
                    logger.warning(
                        "LLM recommended 'transform' but transformation logic is not implemented."
                    )
                    # transformed = llm_eval_result.get("transformed_output")
                final_result = GuardrailOutputCheckResult(
                    allowed=(llm_eval_result["action"] == "allow"),
                    confidence=llm_eval_result["confidence"],
                    decision_layer="llm_fallback",
                    evaluation_method="llm_fallback",
                    violated_policies=llm_eval_result["violated_policies"],
                    blocked_reason=llm_eval_result["reasoning"],
                    transformed_response=transformed,
                    llm_evaluation_result=llm_eval_result,
                    fast_rules_result=_sanitize_typed_dict_for_json(
                        fast_result
                    ),  # Sanitize
                )
                # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
                _schedule_compliance_span_async(
                    final_result, "outbound", ai_response, context
                )
                return final_result  # Early exit

        # --- Step 3: Default Allow ---
        logger.debug(
            f"[{conversation_id}] DecisionRouter: Output check passed. Defaulting to allowed."
        )
        evaluation_method = "llm_fallback" if llm_eval_result else "fast_rules"
        final_result = GuardrailOutputCheckResult(
            allowed=True,
            confidence=1.0,
            decision_layer="default_allow",
            evaluation_method=evaluation_method,
            fast_rules_result=_sanitize_typed_dict_for_json(fast_result),  # Sanitize
            llm_evaluation_result=llm_eval_result,
        )

        # PROD-243 Phase 3: Schedule span creation asynchronously (non-blocking)
        _schedule_compliance_span_async(final_result, "outbound", ai_response, context)

        return final_result
