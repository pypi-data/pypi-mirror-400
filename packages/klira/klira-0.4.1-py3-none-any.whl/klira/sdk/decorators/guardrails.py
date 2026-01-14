import functools
import asyncio
import concurrent.futures
import logging
from typing import Any, Callable, List, Optional, Union, Dict, Type, cast

from opentelemetry import context as otel_context

from klira.sdk.utils.framework_registry import FrameworkRegistry

logger = logging.getLogger("klira.decorators.guardrails")

# Import adapters (will be dynamically imported to avoid circular imports)
_ADAPTERS: Dict[str, Type[Any]] = {}

# Simple storage for guidelines that can be accessed across contexts
_current_guidelines: Optional[List[str]] = None

# Context key for storing guardrail decision data
_GUARDRAIL_DECISION_CONTEXT_KEY = "klira.guardrail_decision"


def _set_current_guidelines(guidelines: List[str]) -> None:
    """Set the current guidelines for decorator access."""
    global _current_guidelines
    _current_guidelines = guidelines


def _get_current_guidelines() -> Optional[List[str]]:
    """Get the current guidelines."""
    global _current_guidelines
    return _current_guidelines


def _clear_current_guidelines() -> None:
    """Clear the current guidelines."""
    global _current_guidelines
    _current_guidelines = None


def _store_guardrail_decision(
    blocked: bool, reason: str, augmentation_applied: bool
) -> None:
    """
    Store guardrail decision data in OpenTelemetry context for agent access.

    Args:
        blocked: Whether input was blocked by guardrails
        reason: Reason for the decision
        augmentation_applied: Whether augmentation was applied
    """
    decision_data = {
        "blocked": blocked,
        "reason": reason,
        "augmentation_applied": augmentation_applied,
        "decision": "BLOCK"
        if blocked
        else ("AUGMENTED" if augmentation_applied else "ALLOW"),
    }
    try:
        ctx = otel_context.set_value(_GUARDRAIL_DECISION_CONTEXT_KEY, decision_data)
        otel_context.attach(ctx)
    except Exception as e:
        logger.debug(f"Failed to store guardrail decision in context: {e}")


def guardrails(
    _func: Optional[Callable[..., Any]] = None,
    *,
    check_input: bool = True,
    check_output: bool = True,
    augment_prompt: bool = True,
    on_input_violation: str = "exception",
    on_output_violation: str = "alternative",
    violation_response: str = "Request blocked due to policy violation.",
    output_violation_response: str = "Response blocked or modified due to policy violation.",
    injection_strategy: str = "auto",  # New parameter to control injection strategy
    **adapter_kwargs: Any,
) -> Union[Callable[..., Any], Callable[[Callable[..., Any]], Callable[..., Any]]]:
    """Decorator to apply Klira AI guardrails using framework adapters.

    This decorator detects the framework (or uses the one provided by other Klira AI decorators)
    and delegates guardrail application (input check, output check, augmentation)
    to the appropriate framework adapter.

    Args:
        check_input: If True, apply input guardrails.
        check_output: If True, apply output guardrails.
        augment_prompt: If True, attempt prompt augmentation based on input check results.
        on_input_violation: Action on input violation: 'exception' (raise KliraPolicyViolation),
                           'alternative' (return violation_response string).
        on_output_violation: Action on output violation: 'exception' (raise KliraPolicyViolation),
                             'alternative' (return output_violation_response or transformed/redacted response),
                             'redact' (synonym for 'alternative', relies on adapter's transformation).
        violation_response: String to return for 'alternative' input violation.
        output_violation_response: Default string for 'alternative' output violation if no specific transformation available.
        injection_strategy: Strategy for injecting guidelines - 'auto' (detect), 'instructions' (inject into agent instructions),
                            'completion' (store in OTel for completion methods to inject)
        **adapter_kwargs: Additional keyword arguments passed to the adapter's guardrail methods.
    """

    def decorator_guardrails(func: Callable[..., Any]) -> Callable[..., Any]:
        func_name = func.__name__
        is_async = asyncio.iscoroutinefunction(func)

        # Get the adapter instance early. This relies on the adapter
        # already being registered and potentially selected by another decorator.
        # If no adapter is found (e.g., @guardrails used alone without framework detection context),
        # it might default to a base/standard adapter or fail gracefully.
        adapter_instance = FrameworkRegistry.get_adapter_instance_for_function(func)

        if not adapter_instance:
            logger.warning(
                f"No adapter found for {func_name} in @guardrails. "
                f"This should not happen as StandardFrameworkAdapter should always be available. "
                f"Attempting to retrieve standard adapter explicitly..."
            )

            # Try to get standard adapter explicitly
            adapter_instance = FrameworkRegistry.get_adapter("standard")

            if not adapter_instance:
                # CRITICAL: Don't return unwrapped function - this breaks guardrails!
                # Instead, log error and continue with None adapter.
                # The wrapper will use GuardrailsEngine directly as fallback.
                logger.error(
                    f"StandardFrameworkAdapter not found in registry for {func_name}. "
                    f"Guardrails will use GuardrailsEngine directly as fallback. "
                    f"This may indicate Klira.init() was not called properly."
                )
                # Continue with adapter_instance = None, wrapper will handle it

        # Detect the function type for use in determining injection strategy
        def is_chat_completion_function(f: Callable[..., Any]) -> bool:
            """Check if this function appears to be an OpenAI chat.completions.create call."""
            return (
                "chat.completions.create" in func_name
                or "create" in func_name
                and hasattr(f, "__self__")
                and hasattr(f.__self__, "__class__")
                and "completion" in f.__self__.__class__.__name__.lower()
            )

        def is_agent_function(f: Callable[..., Any]) -> bool:
            """Check if this function appears to be an agent runner function."""
            return (
                "run" in func_name
                and hasattr(f, "__self__")
                and hasattr(f.__self__, "__class__")
                and "runner" in f.__self__.__class__.__name__.lower()
            )

        # Determine the effective injection strategy based on function type if set to auto
        effective_injection_strategy = injection_strategy
        if injection_strategy == "auto":
            if is_chat_completion_function(func):
                effective_injection_strategy = "completion"
                logger.debug(
                    f"Auto-detected 'completion' injection strategy for {func_name}"
                )
            elif is_agent_function(func):
                effective_injection_strategy = "instructions"
                logger.debug(
                    f"Auto-detected 'instructions' injection strategy for {func_name}"
                )
            else:
                # Default to completion-based strategy if we can't detect
                effective_injection_strategy = "completion"
                logger.debug(
                    f"Defaulting to 'completion' injection strategy for {func_name}"
                )

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal adapter_instance  # Ensure we use the adapter found outside
            nonlocal effective_injection_strategy

            # BUGFIX: Ensure LLM adapters are patched before first use
            # This handles cases where LLM libraries are imported after Klira.init()
            try:
                from klira.sdk import ensure_frameworks_patched

                ensure_frameworks_patched()
            except Exception as e:
                logger.debug(f"Could not ensure frameworks patched: {e}")

            if not adapter_instance:
                logger.warning(
                    f"No adapter available for {func_name} in async_wrapper. "
                    f"Using GuardrailsEngine directly as fallback."
                )
                # Use GuardrailsEngine directly as fallback
                use_direct_engine = True
            else:
                use_direct_engine = False

            current_args, current_kwargs = args, kwargs
            guidelines: Optional[List[str]] = None  # Store guidelines from input check

            # Import at function scope for exception handling
            from klira.sdk.decorators.policies import KliraPolicyViolation

            # --- 1. Input Check (if enabled) ---
            if check_input:
                try:
                    # Use GuardrailsEngine directly if no adapter available
                    if use_direct_engine:
                        from klira.sdk.guardrails.engine import GuardrailsEngine

                        # Extract message from args/kwargs
                        message = None
                        if "query" in kwargs and isinstance(kwargs["query"], str):
                            message = kwargs["query"]
                        elif "message" in kwargs and isinstance(kwargs["message"], str):
                            message = kwargs["message"]
                        elif "input" in kwargs and isinstance(kwargs["input"], str):
                            message = kwargs["input"]
                        else:
                            # Check positional args
                            for arg in args:
                                if isinstance(arg, str):
                                    message = arg
                                    break

                        if message:
                            engine = GuardrailsEngine.get_instance()
                            if engine:
                                # Create context
                                context = {
                                    "conversation_id": kwargs.get("conversation_id"),
                                    "user_id": kwargs.get("user_id"),
                                }

                                # Process message
                                result = await engine.process_message(message, context)

                                blocked = not result.get("allowed", True)
                                reason_raw = (
                                    result.get("blocked_reason", "") if blocked else ""
                                )
                                reason = str(reason_raw) if reason_raw else ""

                                # Store decision
                                _store_guardrail_decision(
                                    blocked=blocked,
                                    reason=reason,
                                    augmentation_applied=False,
                                )

                                if blocked:
                                    if on_input_violation == "exception":
                                        from klira.sdk.decorators.policies import (
                                            KliraPolicyViolation,
                                        )

                                        raise KliraPolicyViolation(
                                            f"Input violation in {func_name}: {reason}",
                                            reason=reason,
                                        )
                                    elif on_input_violation == "alternative":
                                        response = result.get("response", reason)
                                        return (
                                            response if response else violation_response
                                        )
                                    else:
                                        logger.warning(
                                            f"Unhandled input violation action '{on_input_violation}' for {func_name}. Blocking."
                                        )
                                        return violation_response

                        # No blocking, continue with original args
                        modified_args, modified_kwargs = args, kwargs
                    elif adapter_instance is not None:
                        # Call adapter's input check method with explicit keywords
                        modified_args, modified_kwargs, blocked, reason = (
                            adapter_instance.apply_input_guardrails(
                                args=current_args,
                                kwargs=current_kwargs,
                                func_name=func_name,
                                injection_strategy=effective_injection_strategy,  # Pass the injection strategy to the adapter
                            )
                        )

                        # Store guardrail decision data for agent access
                        # (augmentation_applied will be updated after guidelines are retrieved)
                        _store_guardrail_decision(
                            blocked=blocked, reason=reason, augmentation_applied=False
                        )

                        # If blocked, handle based on configuration
                        if blocked:
                            if on_input_violation == "exception":
                                # Import exception class locally to avoid circular dependency issues
                                from klira.sdk.decorators.policies import (
                                    KliraPolicyViolation,
                                )

                                raise KliraPolicyViolation(
                                    f"Input violation in {func_name}: {reason}",
                                    reason=reason,
                                )
                            elif on_input_violation == "alternative":
                                # If the reason itself is the alternative response (e.g., direct reply)
                                if reason and reason != "Input policy violation":
                                    return reason
                                else:
                                    return violation_response
                            else:  # Default or unknown: Log and potentially allow/block based on adapter's default?
                                logger.warning(
                                    f"Unhandled input violation action '{on_input_violation}' for {func_name}. Blocking."
                                )
                                return violation_response  # Default to blocking safely
                    else:
                        # No adapter available, continue with original args
                        modified_args, modified_kwargs = args, kwargs

                    # Update args/kwargs if modified by the adapter (e.g., redaction)
                    current_args, current_kwargs = modified_args, modified_kwargs

                    # Retrieve guidelines from simple storage or OTel context
                    if augment_prompt:
                        global _current_guidelines

                        guidelines = None

                        # First try simple storage
                        if _current_guidelines:
                            guidelines = _current_guidelines
                        else:
                            # Fallback to OTel context
                            try:
                                from opentelemetry import context as otel_context

                                current_otel_ctx = otel_context.get_current()
                                guidelines = otel_context.get_value(
                                    "klira.augmentation.guidelines",
                                    context=current_otel_ctx,
                                )  # type: ignore[assignment]
                            except ImportError:
                                pass  # OpenTelemetry not available
                            except Exception as e:
                                logger.debug(
                                    f"Error retrieving guidelines from OTel context: {e}"
                                )

                        if guidelines and isinstance(guidelines, list):
                            logger.debug(
                                f"Retrieved {len(guidelines)} guidelines for {func_name}."
                            )

                            # Try to inject guidelines into global agent or function arguments
                            try:
                                agent_injected = _inject_guidelines_into_agent_args(
                                    current_args, current_kwargs, guidelines
                                )
                                if not agent_injected:
                                    # Try to find agent in function's global scope
                                    agent_injected = (
                                        _inject_guidelines_into_global_agent(
                                            func, guidelines
                                        )
                                    )

                                if agent_injected:
                                    logger.info(
                                        f"Successfully injected {len(guidelines)} guidelines into agent instructions for {func_name}."
                                    )
                                    # Clear guidelines after successful injection
                                    _current_guidelines = None
                                    # Update decision data to reflect augmentation
                                    _store_guardrail_decision(
                                        blocked=False,
                                        reason="Augmented with policy guidelines",
                                        augmentation_applied=True,
                                    )
                                else:
                                    logger.debug(
                                        f"No agent found for {func_name}. Guidelines not injected."
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to inject guidelines into agent for {func_name}: {e}"
                                )

                except KliraPolicyViolation:
                    # Policy violations should propagate to caller (fail-closed)
                    raise
                except Exception as e:
                    # Infrastructure errors should fail-open with logging
                    logger.error(
                        f"Error during input guardrail check for {func_name}: {e}",
                        exc_info=True,
                    )
                    logger.warning(
                        f"Guardrail check failed for {func_name}, failing open and allowing request to proceed"
                    )
                    # Continue execution (fail-open)

            # --- 3. Execute Original Function ---
            # Use the potentially modified current_args and current_kwargs from apply_input_guardrails
            try:
                result = await func(*current_args, **current_kwargs)
            except Exception as e:
                logger.error(
                    f"Error executing wrapped function {func_name} after guardrails: {e}",
                    exc_info=True,
                )
                raise  # Re-raise the original exception

            # --- 4. Output Check (if enabled) ---
            if check_output:
                try:
                    # Use GuardrailsEngine directly if no adapter available
                    if use_direct_engine:
                        from klira.sdk.guardrails.engine import GuardrailsEngine

                        # Extract output text from result
                        output_text = None
                        if isinstance(result, str):
                            output_text = result
                        elif hasattr(result, "content"):
                            output_text = str(result.content)
                        elif isinstance(result, dict):
                            # Check for common response keys
                            # Note: result is Any type, not necessarily GuardrailProcessingResult
                            result_dict = cast(Dict[str, Any], result)
                            if "content" in result_dict:
                                output_text = str(result_dict["content"])
                            elif "response" in result_dict:
                                output_text = str(result_dict["response"])
                        else:
                            output_text = str(result) if result else None

                        if output_text:
                            engine = GuardrailsEngine.get_instance()
                            if engine:
                                # Create context for outbound evaluation
                                context = {
                                    "conversation_id": kwargs.get("conversation_id"),
                                    "user_id": kwargs.get("user_id"),
                                }

                                # Evaluate output with outbound direction
                                eval_result = await engine.evaluate(
                                    output_text, context, direction="outbound"
                                )

                                blocked = not eval_result.allowed
                                reason = eval_result.reason or "" if blocked else ""

                                if blocked:
                                    if on_output_violation == "exception":
                                        raise KliraPolicyViolation(
                                            f"Output violation in {func_name}: {reason}",
                                            reason=reason,
                                        )
                                    elif on_output_violation in [
                                        "alternative",
                                        "redact",
                                    ]:
                                        return output_violation_response
                                    else:
                                        logger.warning(
                                            f"Unhandled output violation action '{on_output_violation}' for {func_name}. Returning default response."
                                        )
                                        return output_violation_response

                        # No blocking, return original result
                        return result
                    elif adapter_instance is not None:
                        # Call adapter's output check method with explicit keywords
                        modified_result, blocked, alternative_response = (
                            adapter_instance.apply_output_guardrails(
                                result=result,
                                func_name=func_name,
                                # **adapter_kwargs # Base method doesn't take extra kwargs
                            )
                        )

                        # If blocked/modified, handle based on configuration
                        if blocked:
                            if on_output_violation == "exception":
                                from klira.sdk.decorators.policies import (
                                    KliraPolicyViolation,
                                )

                                raise KliraPolicyViolation(
                                    f"Output violation in {func_name}: {alternative_response}"
                                )
                            # 'alternative' and 'redact' both use the alternative_response from the adapter
                            elif on_output_violation in ["alternative", "redact"]:
                                return (
                                    alternative_response or output_violation_response
                                )  # Return adapter's response or default
                            else:
                                logger.warning(
                                    f"Unhandled output violation action '{on_output_violation}' for {func_name}. Returning adapter response or default."
                                )
                                return alternative_response or output_violation_response
                        else:
                            # If not blocked, return the potentially modified result from the adapter
                            return modified_result
                    else:
                        # No adapter available, return original result
                        return result

                except KliraPolicyViolation:
                    # Policy violations should propagate to caller (fail-closed)
                    raise
                except Exception as e:
                    # Infrastructure errors should fail-open with logging
                    logger.error(
                        f"Error during output guardrail check for {func_name}: {e}",
                        exc_info=True,
                    )
                    logger.warning(
                        f"Output guardrail check failed for {func_name}, failing open and returning original result"
                    )
                    return result
            else:
                # If output check disabled, return original result
                return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Synchronous wrapper for guardrails processing."""
            nonlocal adapter_instance
            nonlocal effective_injection_strategy

            # BUGFIX: Ensure LLM adapters are patched before first use
            # This handles cases where LLM libraries are imported after Klira.init()
            try:
                from klira.sdk import ensure_frameworks_patched

                ensure_frameworks_patched()
            except Exception as e:
                logger.debug(f"Could not ensure frameworks patched: {e}")

            if not adapter_instance:
                logger.warning(
                    f"No adapter available for {func_name} in sync_wrapper. "
                    f"Using GuardrailsEngine directly as fallback."
                )
                # Use GuardrailsEngine directly as fallback
                use_direct_engine = True
            else:
                use_direct_engine = False

            current_args, current_kwargs = args, kwargs
            guidelines: Optional[List[str]] = None

            # Import at function scope for exception handling
            from klira.sdk.decorators.policies import KliraPolicyViolation

            # --- 1. Input Check (if enabled) ---
            if check_input:
                try:
                    # Use GuardrailsEngine directly if no adapter available
                    if use_direct_engine:
                        from klira.sdk.guardrails.engine import GuardrailsEngine

                        # Extract message from args/kwargs
                        message = None
                        if "query" in kwargs and isinstance(kwargs["query"], str):
                            message = kwargs["query"]
                        elif "message" in kwargs and isinstance(kwargs["message"], str):
                            message = kwargs["message"]
                        elif "input" in kwargs and isinstance(kwargs["input"], str):
                            message = kwargs["input"]
                        else:
                            # Check positional args
                            for arg in args:
                                if isinstance(arg, str):
                                    message = arg
                                    break

                        if message:
                            engine = GuardrailsEngine.get_instance()
                            if engine:
                                # Create context
                                context = {
                                    "conversation_id": kwargs.get("conversation_id"),
                                    "user_id": kwargs.get("user_id"),
                                }

                                # Process message (sync version), handling existing event loops
                                try:
                                    loop = asyncio.get_event_loop()
                                    if loop.is_running():
                                        # If we're already in an async context, run in a thread pool
                                        with (
                                            concurrent.futures.ThreadPoolExecutor() as executor
                                        ):
                                            future = executor.submit(
                                                asyncio.run,
                                                engine.process_message(
                                                    message, context
                                                ),
                                            )
                                            result = future.result()
                                    else:
                                        result = loop.run_until_complete(
                                            engine.process_message(message, context)
                                        )
                                except RuntimeError:
                                    # No event loop available, create a new one
                                    result = asyncio.run(
                                        engine.process_message(message, context)
                                    )

                                blocked = not result.get("allowed", True)
                                reason_raw = (
                                    result.get("blocked_reason", "") if blocked else ""
                                )
                                reason = str(reason_raw) if reason_raw else ""

                                # Store decision
                                _store_guardrail_decision(
                                    blocked=blocked,
                                    reason=reason,
                                    augmentation_applied=False,
                                )

                                if blocked:
                                    if on_input_violation == "exception":
                                        from klira.sdk.decorators.policies import (
                                            KliraPolicyViolation,
                                        )

                                        raise KliraPolicyViolation(
                                            f"Input violation in {func_name}: {reason}",
                                            reason=reason,
                                        )
                                    elif on_input_violation == "alternative":
                                        response = result.get("response", reason)
                                        return (
                                            response if response else violation_response
                                        )
                                    else:
                                        logger.warning(
                                            f"Unhandled input violation action '{on_input_violation}' for {func_name}. Blocking."
                                        )
                                        return violation_response

                        # No blocking, continue with original args
                        modified_args, modified_kwargs = args, kwargs
                    elif adapter_instance is not None:
                        modified_args, modified_kwargs, blocked, reason = (
                            adapter_instance.apply_input_guardrails(
                                args=current_args,
                                kwargs=current_kwargs,
                                func_name=func_name,
                                injection_strategy=effective_injection_strategy,
                            )
                        )

                        # Store guardrail decision data for agent access
                        # (augmentation_applied will be updated after guidelines are retrieved)
                        _store_guardrail_decision(
                            blocked=blocked, reason=reason, augmentation_applied=False
                        )

                        if blocked:
                            if on_input_violation == "exception":
                                from klira.sdk.decorators.policies import (
                                    KliraPolicyViolation,
                                )

                                raise KliraPolicyViolation(
                                    f"Input violation in {func_name}: {reason}",
                                    reason=reason,
                                )
                            elif on_input_violation == "alternative":
                                if reason and reason != "Input policy violation":
                                    return reason
                                else:
                                    return violation_response
                            else:
                                logger.warning(
                                    f"Unhandled input violation action '{on_input_violation}' for {func_name}. Blocking."
                                )
                                return violation_response
                    else:
                        # No adapter available, continue with original args
                        modified_args, modified_kwargs = args, kwargs

                    current_args, current_kwargs = modified_args, modified_kwargs

                    # Retrieve guidelines from simple storage or OTel context
                    if augment_prompt:
                        global _current_guidelines
                        guidelines = None

                        if _current_guidelines:
                            guidelines = _current_guidelines
                        else:
                            try:
                                from opentelemetry import context as otel_context

                                current_otel_ctx = otel_context.get_current()
                                guidelines_value = otel_context.get_value(
                                    "klira.augmentation.guidelines",
                                    context=current_otel_ctx,
                                )
                                guidelines = (
                                    guidelines_value
                                    if isinstance(guidelines_value, list)
                                    else None
                                )
                            except ImportError:
                                pass
                            except Exception as e:
                                logger.debug(
                                    f"Error retrieving guidelines from OTel context: {e}"
                                )

                        if guidelines and isinstance(guidelines, list):
                            logger.debug(
                                f"Retrieved {len(guidelines)} guidelines for {func_name}."
                            )

                            try:
                                agent_injected = _inject_guidelines_into_agent_args(
                                    current_args, current_kwargs, guidelines
                                )
                                if not agent_injected:
                                    agent_injected = (
                                        _inject_guidelines_into_global_agent(
                                            func, guidelines
                                        )
                                    )

                                if agent_injected:
                                    logger.info(
                                        f"Successfully injected {len(guidelines)} guidelines into agent instructions for {func_name}."
                                    )
                                    _current_guidelines = None
                                    # Update decision data to reflect augmentation
                                    _store_guardrail_decision(
                                        blocked=False,
                                        reason="Augmented with policy guidelines",
                                        augmentation_applied=True,
                                    )
                                else:
                                    logger.debug(
                                        f"No agent found for {func_name}. Guidelines not injected."
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to inject guidelines into agent for {func_name}: {e}"
                                )

                except KliraPolicyViolation:
                    # Policy violations should propagate to caller (fail-closed)
                    raise
                except Exception as e:
                    # Infrastructure errors should fail-open with logging
                    logger.error(
                        f"Error during input guardrail check for {func_name}: {e}",
                        exc_info=True,
                    )
                    logger.warning(
                        f"Guardrail check failed for {func_name}, failing open and allowing request to proceed"
                    )
                    # Continue execution (fail-open)

            # --- 2. Execute Original Function ---
            try:
                result = func(*current_args, **current_kwargs)
            except Exception as e:
                logger.error(
                    f"Error executing wrapped function {func_name} after guardrails: {e}",
                    exc_info=True,
                )
                raise

            # --- 3. Output Check (if enabled) ---
            if check_output:
                try:
                    # Use GuardrailsEngine directly if no adapter available
                    if use_direct_engine:
                        from klira.sdk.guardrails.engine import GuardrailsEngine

                        # Extract output text from result
                        output_text = None
                        if isinstance(result, str):
                            output_text = result
                        elif hasattr(result, "content"):
                            output_text = str(result.content)
                        elif isinstance(result, dict):
                            # Check for common response keys
                            # Note: result is Any type, not necessarily GuardrailProcessingResult
                            result_dict = cast(Dict[str, Any], result)
                            if "content" in result_dict:
                                output_text = str(result_dict["content"])
                            elif "response" in result_dict:
                                output_text = str(result_dict["response"])
                        else:
                            output_text = str(result) if result else None

                        if output_text:
                            engine = GuardrailsEngine.get_instance()
                            if engine:
                                # Create context for outbound evaluation
                                context = {
                                    "conversation_id": kwargs.get("conversation_id"),
                                    "user_id": kwargs.get("user_id"),
                                }

                                # Evaluate output with outbound direction (sync version)
                                try:
                                    loop = asyncio.get_event_loop()
                                    if loop.is_running():
                                        # If we're already in an async context, run in a thread pool
                                        with (
                                            concurrent.futures.ThreadPoolExecutor() as executor
                                        ):
                                            future = executor.submit(
                                                asyncio.run,
                                                engine.evaluate(
                                                    output_text,
                                                    context,
                                                    direction="outbound",
                                                ),
                                            )
                                            eval_result = future.result()
                                    else:
                                        eval_result = loop.run_until_complete(
                                            engine.evaluate(
                                                output_text,
                                                context,
                                                direction="outbound",
                                            )
                                        )
                                except RuntimeError:
                                    # No event loop available, create a new one
                                    eval_result = asyncio.run(
                                        engine.evaluate(
                                            output_text, context, direction="outbound"
                                        )
                                    )

                                blocked = not eval_result.allowed
                                reason = eval_result.reason or "" if blocked else ""

                                if blocked:
                                    if on_output_violation == "exception":
                                        raise KliraPolicyViolation(
                                            f"Output violation in {func_name}: {reason}",
                                            reason=reason,
                                        )
                                    elif on_output_violation in [
                                        "alternative",
                                        "redact",
                                    ]:
                                        return output_violation_response
                                    else:
                                        logger.warning(
                                            f"Unhandled output violation action '{on_output_violation}' for {func_name}. Returning default response."
                                        )
                                        return output_violation_response

                        # No blocking, return original result
                        return result
                    elif adapter_instance is not None:
                        modified_result, blocked, alternative_response = (
                            adapter_instance.apply_output_guardrails(
                                result=result,
                                func_name=func_name,
                            )
                        )

                        if blocked:
                            if on_output_violation == "exception":
                                from klira.sdk.decorators.policies import (
                                    KliraPolicyViolation,
                                )

                                raise KliraPolicyViolation(
                                    f"Output violation in {func_name}: {alternative_response}"
                                )
                            elif on_output_violation in ["alternative", "redact"]:
                                return alternative_response or output_violation_response
                            else:
                                logger.warning(
                                    f"Unhandled output violation action '{on_output_violation}' for {func_name}. Returning adapter response or default."
                                )
                                return alternative_response or output_violation_response
                        else:
                            return modified_result
                    else:
                        # No adapter available, return original result
                        return result

                except KliraPolicyViolation:
                    # Policy violations should propagate to caller (fail-closed)
                    raise
                except Exception as e:
                    # Infrastructure errors should fail-open with logging
                    logger.error(
                        f"Error during output guardrail check for {func_name}: {e}",
                        exc_info=True,
                    )
                    logger.warning(
                        f"Output guardrail check failed for {func_name}, failing open and returning original result"
                    )
                    return result
            else:
                return result

        # Return the correct wrapper based on the original function type
        if is_async:
            return async_wrapper
        else:
            return sync_wrapper

    # Handle decorator called with or without arguments
    if _func is None:
        return decorator_guardrails  # Called with arguments: @guardrails(...)
    else:
        # Support both sync and async functions
        return decorator_guardrails(_func)  # Called without arguments: @guardrails


# Alias for backward compatibility with previous Klira AI SDK versions
add_policies = guardrails


def _inject_guidelines_into_global_agent(
    func: Callable[..., Any], guidelines: List[str]
) -> bool:
    """
    Helper function to inject guidelines into agent found in function's global scope.

    Args:
        func: The function whose globals to search
        guidelines: List of guideline strings to inject

    Returns:
        True if an agent was found and guidelines were injected, False otherwise
    """
    try:
        # Try to import agents module to check for Agent instances
        try:
            from agents import Agent
        except ImportError:
            # OpenAI Agents SDK not available
            return False

        # Get the function's global namespace
        func_globals = getattr(func, "__globals__", {})

        # Look for Agent instances in the global namespace
        for name, value in func_globals.items():
            if isinstance(value, Agent) and hasattr(value, "instructions"):
                original_instructions = getattr(value, "instructions", "")
                if not isinstance(original_instructions, str):
                    original_instructions = str(original_instructions)

                # Format guidelines
                policy_section_header = "\n\nIMPORTANT POLICY GUIDELINES:"
                formatted_guidelines = (
                    policy_section_header
                    + "\n"
                    + "\n".join([f"- {g}" for g in guidelines])
                )

                # Avoid duplicate injection
                if policy_section_header in original_instructions:
                    original_instructions = original_instructions.split(
                        policy_section_header
                    )[0].rstrip()

                # Inject guidelines
                separator = "\n\n" if original_instructions else ""
                new_instructions = (
                    original_instructions + separator + formatted_guidelines
                )

                # Update agent instructions
                setattr(value, "instructions", new_instructions)
                logger.debug(
                    f"Injected {len(guidelines)} guidelines into global Agent '{name}'"
                )
                return True

        return False

    except Exception as e:
        logger.error(
            f"Error in _inject_guidelines_into_global_agent: {e}", exc_info=True
        )
        return False


def _inject_guidelines_into_agent_args(
    args: tuple[Any, ...], kwargs: dict[str, Any], guidelines: List[str]
) -> bool:
    """
    Helper function to inject guidelines into agent instructions found in function arguments.

    Args:
        args: Function positional arguments
        kwargs: Function keyword arguments
        guidelines: List of guideline strings to inject

    Returns:
        True if an agent was found and guidelines were injected, False otherwise
    """
    try:
        # Try to import agents module to check for Agent instances
        try:
            from agents import Agent
        except ImportError:
            # OpenAI Agents SDK not available
            return False

        # Look for Agent instances in the arguments
        agent_found = False

        # Check positional arguments
        for arg in args:
            if isinstance(arg, Agent) and hasattr(arg, "instructions"):
                agent_found = True
                original_instructions = getattr(arg, "instructions", "")
                if not isinstance(original_instructions, str):
                    original_instructions = str(original_instructions)

                # Format guidelines
                policy_section_header = "\n\nIMPORTANT POLICY GUIDELINES:"
                formatted_guidelines = (
                    policy_section_header
                    + "\n"
                    + "\n".join([f"- {g}" for g in guidelines])
                )

                # Avoid duplicate injection
                if policy_section_header in original_instructions:
                    original_instructions = original_instructions.split(
                        policy_section_header
                    )[0].rstrip()

                # Inject guidelines
                separator = "\n\n" if original_instructions else ""
                new_instructions = (
                    original_instructions + separator + formatted_guidelines
                )

                # Update agent instructions
                setattr(arg, "instructions", new_instructions)
                logger.debug(
                    f"Injected {len(guidelines)} guidelines into Agent.instructions"
                )

        # Check keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, Agent) and hasattr(value, "instructions"):
                agent_found = True
                original_instructions = getattr(value, "instructions", "")
                if not isinstance(original_instructions, str):
                    original_instructions = str(original_instructions)

                # Format guidelines
                policy_section_header = "\n\nIMPORTANT POLICY GUIDELINES:"
                formatted_guidelines = (
                    policy_section_header
                    + "\n"
                    + "\n".join([f"- {g}" for g in guidelines])
                )

                # Avoid duplicate injection
                if policy_section_header in original_instructions:
                    original_instructions = original_instructions.split(
                        policy_section_header
                    )[0].rstrip()

                # Inject guidelines
                separator = "\n\n" if original_instructions else ""
                new_instructions = (
                    original_instructions + separator + formatted_guidelines
                )

                # Update agent instructions
                setattr(value, "instructions", new_instructions)
                logger.debug(
                    f"Injected {len(guidelines)} guidelines into Agent.instructions (kwarg: {key})"
                )

        return agent_found

    except Exception as e:
        logger.error(f"Error in _inject_guidelines_into_agent_args: {e}", exc_info=True)
        return False
