"""Base OpenTelemetry decorator implementations for the Klira AI SDK.

Provides wrappers around Traceloop decorators OR framework-specific adapters
to automatically add Klira AI-specific context attributes and apply framework-aware tracing.
"""

import functools
import logging
from typing import Optional, Callable, Any, Dict, Type, TypeVar, cast

from opentelemetry import context, trace
from opentelemetry.semconv_ai import TraceloopSpanKindValues

# Import Traceloop decorators for fallback
try:
    from traceloop.sdk.decorators import (
        workflow as traceloop_workflow,
        task as traceloop_task,
        agent as traceloop_agent,
        tool as traceloop_tool,
    )

    TRACELOOP_DECORATORS_AVAILABLE = True
except ImportError:
    TRACELOOP_DECORATORS_AVAILABLE = False

    # Define dummy fallback decorators if Traceloop isn't fully available
    def _dummy_decorator(
        name: Optional[str] = None, **kwargs: Any
    ) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, **_kwargs: Any) -> Any:
                return func(*args, **_kwargs)

            return wrapper

        return decorator

    traceloop_workflow = traceloop_task = traceloop_agent = traceloop_tool = (
        _dummy_decorator
    )

# Klira AI SDK specific imports
from klira.sdk.utils.framework_detection import (
    detect_framework_cached as detect_framework,
)
from klira.sdk.utils.framework_registry import FrameworkRegistry

# Type variable definitions (keep as before)
F = TypeVar("F", bound=Callable[..., Any])
C = TypeVar("C", bound=Type[Any])

logger = logging.getLogger("klira.decorators.base")

# Mapping from Traceloop span kind to Klira entity type (keep as before)
_SPAN_KIND_TO_KLIRA_ENTITY_TYPE: Dict[TraceloopSpanKindValues, str] = {
    TraceloopSpanKindValues.WORKFLOW: "workflow",
    TraceloopSpanKindValues.TASK: "task",
    TraceloopSpanKindValues.AGENT: "agent",
    TraceloopSpanKindValues.TOOL: "tool",
}


def _validate_user_id(
    decorator_type: str, func_or_class: Any, ctx_attrs: Dict[str, Any]
) -> None:
    """
    Validate that user_id is provided via decorator parameter or global context.

    Args:
        decorator_type: The type of decorator (workflow, task, agent, tool)
        func_or_class: The decorated function or class
        ctx_attrs: Context attributes from decorator

    Raises:
        ValueError: If user_id is not found in either location
    """
    from klira.sdk.tracing.tracing import get_current_context

    # Check decorator parameter first
    user_id_from_decorator = ctx_attrs.get("user_id")

    if not user_id_from_decorator:
        # Fall back to global context
        current_context = get_current_context()
        user_id_from_context = current_context.get("user_id")

        if not user_id_from_context:
            # Neither source has user_id - raise error
            func_name = getattr(func_or_class, "__name__", "unknown")

            raise ValueError(
                f"user_id is required for {decorator_type} '{func_name}'. "
                f"Provide it via decorator parameter or set_hierarchy_context().\n\n"
                f"Example 1 - Via decorator parameter:\n"
                f"  @{decorator_type}(name='my_{decorator_type}', user_id='user_123')\n"
                f"  def {func_name}():\n"
                f"      pass\n\n"
                f"Example 2 - Via global context:\n"
                f"  from klira.sdk.tracing import set_hierarchy_context\n"
                f"  set_hierarchy_context(user_id='user_123')\n"
                f"  @{decorator_type}(name='my_{decorator_type}')\n"
                f"  def {func_name}():\n"
                f"      pass\n\n"
                f"For more information, see: https://docs.getklira.com/user-tracking"
            )


def _add_klira_context(
    ctx_attributes: Optional[Dict[str, str]],
    span_kind: Optional[
        TraceloopSpanKindValues
    ] = None,  # Made optional, may not always apply
) -> None:
    """Helper to add custom klira.* attributes to the current OTel context."""
    current_ctx = context.get_current()
    new_values: Dict[str, Any] = {}

    # Add custom context attributes prefixed with 'klira.'
    if ctx_attributes:
        for key, value in ctx_attributes.items():
            new_values[f"klira.{key}"] = value

    # Add klira.entity_type based on span kind if provided
    if span_kind:
        entity_type = _SPAN_KIND_TO_KLIRA_ENTITY_TYPE.get(span_kind)
        if entity_type:
            new_values["klira.entity_type"] = entity_type

    if new_values:
        modified_ctx = current_ctx
        for key, value in new_values.items():
            modified_ctx = context.set_value(key, value, context=modified_ctx)
        context.attach(modified_ctx)


# --- Unified Trace Detection ---


def _is_in_unified_trace() -> bool:
    """
    Check if we're currently in a unified trace context.

    Returns:
        True if a valid root span named "klira.user.message" exists in context
    """
    current_span = trace.get_current_span()
    if not current_span:
        return False

    # Check if span context is valid
    span_context = current_span.get_span_context()
    if not span_context or not span_context.is_valid:
        return False

    # Check if the current span is a unified trace root
    # The root span is named "klira.user.message"
    # Note: Span interface doesn't expose name, but SDK implementation does
    if hasattr(current_span, "name") and current_span.name == "klira.user.message":
        return True

    # Also check if we're a descendant of a unified trace root
    # by looking for the klira.user_id attribute which is set on the root
    # This works because child spans inherit access to parent context
    try:
        # If we can get user_id from context, we're likely in a unified trace
        user_id_in_context = context.get_value("klira.user_id")
        if user_id_in_context:
            return True
    except Exception:
        pass

    return False


def _wrap_with_unified_trace_detection(
    decorator_type: str,
    adapted_func: Any,
    original_func: Any,
    name: str,
    **kwargs: Any,
) -> Any:
    """
    Wrap a decorated function with runtime unified trace detection.

    At execution time, this wrapper checks if we're in a unified trace context:
    - If we should auto-trace (@workflow only): create root unified trace automatically
    - If yes (already in trace): create a child span using the original function
    - If no: call the adapted function (adapter/Traceloop decorated version)

    This allows the same decorator to work in both modes without code changes.

    Args:
        decorator_type: Type of decorator (workflow, agent, task, tool)
        adapted_func: The function after adapter/Traceloop decoration
        original_func: The original undecorated function
        name: Name for the span
        **kwargs: Decorator kwargs (for child span attributes)

    Returns:
        Wrapped function that detects unified trace at runtime
    """
    import asyncio
    import uuid
    from klira.sdk.utils.span_utils import safe_set_span_attribute
    from opentelemetry import context as otel_context

    # Get context attributes for child span mode
    ctx_attrs = kwargs.get("context_attributes", {})
    span_name = f"klira.{decorator_type}.{name}"

    # Check if original function is async
    is_async = asyncio.iscoroutinefunction(original_func)

    def should_auto_trace() -> bool:
        """
        Check if we should auto-create a unified trace.

        Auto-tracing only happens for @workflow decorators when:
        1. We're not already in a unified trace
        2. Auto-tracing hasn't already started (prevents nested auto-traces)
        3. We have a user_id in context attributes

        Returns:
            True if we should auto-create a unified trace, False otherwise
        """
        # Only workflows auto-trace (agents, tasks, tools don't)
        if decorator_type != "workflow":
            return False

        # Don't auto-trace if already in unified trace
        if _is_in_unified_trace():
            return False

        # Prevent nested auto-tracing with context variable check
        try:
            is_active = otel_context.get_value("klira._auto_trace_in_progress")
            if is_active:
                return False
        except Exception:
            pass

        # Need user_id to create a trace
        if not ctx_attrs.get("user_id"):
            return False

        return True

    if is_async:

        @functools.wraps(original_func)
        async def async_runtime_wrapper(*args: Any, **wrapper_kwargs: Any) -> Any:
            """Async wrapper with runtime unified trace detection and auto-tracing."""
            # Check if we should auto-create a unified trace
            if should_auto_trace():
                # Import here to avoid circular imports
                from klira.sdk.tracing import start_user_message_trace

                # Auto-generate conversation_id if not provided
                user_id = ctx_attrs.get("user_id")
                conversation_id = (
                    ctx_attrs.get("conversation_id") or f"conv_{uuid.uuid4().hex[:12]}"
                )
                organization_id = ctx_attrs.get("organization_id")
                project_id = ctx_attrs.get("project_id")

                # Mark that we've started auto-trace to prevent nesting
                auto_trace_ctx = otel_context.set_value(
                    "klira._auto_trace_in_progress", True
                )
                token = otel_context.attach(auto_trace_ctx)

                try:
                    # Create unified trace context and execute within it
                    with start_user_message_trace(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        organization_id=organization_id,
                        project_id=project_id,
                    ):
                        # Now we're in a unified trace, call the original function
                        # It will create a child span via the else branch below
                        return await original_func(*args, **wrapper_kwargs)
                finally:
                    # Reset the auto-trace flag
                    otel_context.detach(token)

            # Runtime check: are we in a unified trace?
            elif _is_in_unified_trace():
                # Yes: create child span using original function
                tracer = trace.get_tracer("klira")
                with tracer.start_as_current_span(span_name) as span:
                    safe_set_span_attribute(span, "klira.entity_type", decorator_type)
                    safe_set_span_attribute(span, "klira.entity_name", name)

                    for key, value in ctx_attrs.items():
                        safe_set_span_attribute(span, f"klira.{key}", value)

                    try:
                        result = await original_func(*args, **wrapper_kwargs)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            else:
                # No: use adapted function (standard behavior)
                return await adapted_func(*args, **wrapper_kwargs)

        return async_runtime_wrapper
    else:

        @functools.wraps(original_func)
        def sync_runtime_wrapper(*args: Any, **wrapper_kwargs: Any) -> Any:
            """Sync wrapper with runtime unified trace detection and auto-tracing."""
            # Check if we should auto-create a unified trace
            if should_auto_trace():
                # Import here to avoid circular imports
                from klira.sdk.tracing import start_user_message_trace

                # Auto-generate conversation_id if not provided
                user_id = ctx_attrs.get("user_id")
                conversation_id = (
                    ctx_attrs.get("conversation_id") or f"conv_{uuid.uuid4().hex[:12]}"
                )
                organization_id = ctx_attrs.get("organization_id")
                project_id = ctx_attrs.get("project_id")

                # Mark that we've started auto-trace to prevent nesting
                auto_trace_ctx = otel_context.set_value(
                    "klira._auto_trace_in_progress", True
                )
                token = otel_context.attach(auto_trace_ctx)

                try:
                    # Create unified trace context and execute within it
                    with start_user_message_trace(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        organization_id=organization_id,
                        project_id=project_id,
                    ):
                        # Now we're in a unified trace, call the original function
                        # It will create a child span via the else branch below
                        return original_func(*args, **wrapper_kwargs)
                finally:
                    # Reset the auto-trace flag
                    otel_context.detach(token)

            # Runtime check: are we in a unified trace?
            elif _is_in_unified_trace():
                # Yes: create child span using original function
                tracer = trace.get_tracer("klira")
                with tracer.start_as_current_span(span_name) as span:
                    safe_set_span_attribute(span, "klira.entity_type", decorator_type)
                    safe_set_span_attribute(span, "klira.entity_name", name)

                    for key, value in ctx_attrs.items():
                        safe_set_span_attribute(span, f"klira.{key}", value)

                    try:
                        result = original_func(*args, **wrapper_kwargs)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            else:
                # No: use adapted function (standard behavior)
                return adapted_func(*args, **wrapper_kwargs)

        return sync_runtime_wrapper


def _create_child_span_decorator(
    decorator_type: str,
    func_or_class: Any,
    name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a decorator that creates child spans in unified trace mode.

    This is used when we detect that we're already in a unified trace context.
    Instead of creating a new root trace, we create child spans under the
    current context.

    Args:
        decorator_type: Type of decorator (workflow, agent, task, tool)
        func_or_class: Function or class being decorated
        name: Optional name for the span
        **kwargs: Additional decorator arguments

    Returns:
        Decorated function that creates child spans
    """
    import asyncio
    from klira.sdk.utils.span_utils import safe_set_span_attribute

    # Get function name
    func_name = name or getattr(func_or_class, "__name__", f"klira.{decorator_type}")
    span_name = f"klira.{decorator_type}.{func_name}"

    # Get context attributes
    ctx_attrs = kwargs.get("context_attributes", {})

    # Determine if function is async
    is_async = asyncio.iscoroutinefunction(func_or_class)

    if is_async:

        @functools.wraps(func_or_class)
        async def async_wrapper(*args: Any, **wrapper_kwargs: Any) -> Any:
            """Async wrapper that creates a child span."""
            tracer = trace.get_tracer("klira")

            # Create child span (will automatically be a child of current span)
            with tracer.start_as_current_span(span_name) as span:
                # Set standard attributes
                safe_set_span_attribute(span, "klira.entity_type", decorator_type)
                safe_set_span_attribute(span, "klira.entity_name", func_name)

                # Set context attributes from decorator
                for key, value in ctx_attrs.items():
                    safe_set_span_attribute(span, f"klira.{key}", value)

                # Call the original function
                try:
                    result = await func_or_class(*args, **wrapper_kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return async_wrapper
    else:

        @functools.wraps(func_or_class)
        def sync_wrapper(*args: Any, **wrapper_kwargs: Any) -> Any:
            """Sync wrapper that creates a child span."""
            tracer = trace.get_tracer("klira")

            # Create child span (will automatically be a child of current span)
            with tracer.start_as_current_span(span_name) as span:
                # Set standard attributes
                safe_set_span_attribute(span, "klira.entity_type", decorator_type)
                safe_set_span_attribute(span, "klira.entity_name", func_name)

                # Set context attributes from decorator
                for key, value in ctx_attrs.items():
                    safe_set_span_attribute(span, f"klira.{key}", value)

                # Call the original function
                try:
                    result = func_or_class(*args, **wrapper_kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return sync_wrapper


# --- New Core Decorator Logic ---


def _apply_klira_decorator(
    decorator_type: str,  # e.g., "workflow", "tool"
    func_or_class: Any,
    name: Optional[str] = None,
    # context_attributes removed here, handled by specific decorators below
    **kwargs: Any,  # Pass other kwargs (like version, and context_attributes/tlp_span_kind for fallback context) through
) -> Any:
    """Core helper function to apply Klira decorators with framework adaptation.

    IMPORTANT: We create a runtime wrapper that checks for unified trace at
    EXECUTION time, not decoration time. This is because decorators are applied
    when the function is defined, but unified trace context is only active
    when the function is called within start_user_message_trace().
    """

    # Detect framework based on the function/class being decorated
    try:
        framework = detect_framework(func_or_class)
    except Exception as e:
        logger.error(
            f"Error detecting framework for {getattr(func_or_class, '__name__', func_or_class)}: {e}. Defaulting to 'standard'.",
            exc_info=True,
        )
        framework = "standard"

    adapter = FrameworkRegistry.get_adapter(framework)
    logger.debug(
        f"Applying Klira decorator '{decorator_type}' for detected framework '{framework}'. Adapter: {type(adapter).__name__ if adapter else 'None'}"
    )

    adapter_method_name = f"adapt_{decorator_type}"

    # Determine the fallback Traceloop decorator
    fallback_decorator = None
    if TRACELOOP_DECORATORS_AVAILABLE:
        fallback_decorator = globals().get(f"traceloop_{decorator_type}")

    adapted_func_or_class: Any = (
        func_or_class  # Default to original if everything fails
    )
    applied_adapter = False

    # Get original name for preservation
    original_name = getattr(func_or_class, "__name__", None)
    if not original_name and hasattr(func_or_class, "__class__"):
        original_name = func_or_class.__class__.__name__

    # Use provided name or original name as fallback
    func_name = name or original_name or "unknown_function"

    if adapter:
        try:
            # Validate user_id before applying adapter (required for all decorators)
            _validate_user_id(
                decorator_type=decorator_type,
                func_or_class=func_or_class,
                ctx_attrs=kwargs.get("context_attributes", {}),
            )

            # Get the appropriate adapt method (adapt_workflow, adapt_task, etc.)
            apply_adapter = getattr(adapter, f"adapt_{decorator_type}", None)

            if apply_adapter:
                # Separate Klira-specific context args from args meant for the adapter/traceloop
                adapter_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["context_attributes", "tlp_span_kind"]
                }

                adapted_func_or_class = apply_adapter(
                    func_or_class, name=name, **adapter_kwargs
                )

                # Check if adapter actually did something (it might return original func if it declines)
                if adapted_func_or_class is not func_or_class:
                    applied_adapter = True
                    logger.debug(
                        f"Applied adapter method 'adapt_{decorator_type}' for framework '{framework}'"
                    )
                else:
                    # If adapter returned original function, it means it declined to adapt
                    # So we should fall back to standard Traceloop decorator
                    logger.debug(
                        f"Adapter '{type(adapter).__name__}' declined to adapt '{decorator_type}' (returned original function). Falling back."
                    )
            else:
                logger.debug(
                    f"Adapter '{type(adapter).__name__}' has no method 'adapt_{decorator_type}'. Falling back."
                )

        except ValueError:
            # Re-raise ValueError (from _validate_user_id) - these are critical
            # validation errors that should propagate to the user, not be silently suppressed
            raise
        except Exception as e:
            logger.error(
                f"Error applying framework adapter: {e}. "
                f"Falling back to standard Traceloop decorator."
            )
            # Fallback will happen below since applied_adapter is False

    # After adapter processing, check if we have a FunctionTool for tool decorators
    # This makes FunctionTool objects callable for direct function calls while
    # preserving Agent SDK compatibility
    # Guard with applied_adapter to ensure adapted_func_or_class is defined
    if decorator_type == "tool" and applied_adapter and callable(func_or_class):
        # Check if the adapted result is a FunctionTool from OpenAI Agents SDK
        is_function_tool = (
            hasattr(adapted_func_or_class, "on_invoke_tool")
            and type(adapted_func_or_class).__name__ == "FunctionTool"
        )

        if is_function_tool:
            # Wrap FunctionTool to make it callable directly
            # This preserves the FunctionTool object for Agent SDK compatibility
            # while making it callable for direct function calls
            original_func = func_or_class

            @functools.wraps(original_func)
            def callable_wrapper(*args: Any, **kwargs: Any) -> Any:
                # Call the original function, not the FunctionTool
                return original_func(*args, **kwargs)

            # Preserve FunctionTool attributes for Agent SDK compatibility
            callable_wrapper._function_tool = adapted_func_or_class  # type: ignore[attr-defined]

            # Replace adapted_func_or_class with the callable wrapper
            adapted_func_or_class = callable_wrapper
            applied_adapter = True  # Mark as adapted to prevent fallback

    # Fallback to standard Traceloop decorator ONLY if adapter wasn't applied successfully
    if not applied_adapter:
        if fallback_decorator:
            try:
                logger.debug(
                    f"Falling back to Traceloop decorator 'traceloop_{decorator_type}'"
                )

                # Validate user_id at decoration time (consistent with adapter path)
                # This ensures early failure if user_id is missing, rather than
                # failing at execution time inside the wrapper
                _validate_user_id(
                    decorator_type=decorator_type,
                    func_or_class=func_or_class,
                    ctx_attrs=kwargs.get("context_attributes", {}),
                )

                # Separate Klira-specific context args from args meant for the traceloop decorator
                traceloop_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["context_attributes", "tlp_span_kind"]
                }

                # Apply the Traceloop decorator with *only* its expected arguments
                decorated_by_traceloop = fallback_decorator(
                    name=name, **traceloop_kwargs
                )(func_or_class)

                # Wrap the Traceloop decorator to add Klira context *before* it runs
                # This is only needed if we didn't use a Klira adapter
                @functools.wraps(
                    func_or_class
                )  # Keep original signature info if possible
                def context_wrapper(*args: Any, **wrapper_kwargs: Any) -> Any:
                    """Wrapper to ensure the context is set properly."""

                    # Identify the correct span kind for context using the original kwargs
                    tlp_span_kind = kwargs.get("tlp_span_kind")
                    if not tlp_span_kind:
                        kind_map = {
                            "workflow": TraceloopSpanKindValues.WORKFLOW,
                            "task": TraceloopSpanKindValues.TASK,
                            "agent": TraceloopSpanKindValues.AGENT,
                            "tool": TraceloopSpanKindValues.TOOL,
                        }
                        tlp_span_kind = kind_map.get(decorator_type)

                    # Get Klira context attributes passed to the original decorator call from original kwargs
                    klira_ctx_attrs = kwargs.get("context_attributes", {})
                    _add_klira_context(klira_ctx_attrs, tlp_span_kind)

                    # Call the function that Traceloop decorated
                    return decorated_by_traceloop(*args, **wrapper_kwargs)

                # Ensure name property is preserved
                context_wrapper.__name__ = func_name
                if hasattr(func_or_class, "__annotations__"):
                    context_wrapper.__annotations__ = func_or_class.__annotations__

                adapted_func_or_class = cast(Any, context_wrapper)

            except ValueError:
                # Re-raise ValueError (from _validate_user_id) - these are critical
                # validation errors that should propagate to the user
                raise
            except Exception as e:
                logger.error(
                    f"Error applying Traceloop fallback decorator 'traceloop_{decorator_type}': {e}. Returning original function.",
                    exc_info=True,
                )
                adapted_func_or_class = (
                    func_or_class  # Revert to original on fallback error
                )
        else:
            # If no adapter and no fallback, validate user_id before returning original function
            # This ensures consistent validation across all code paths
            _validate_user_id(
                decorator_type=decorator_type,
                func_or_class=func_or_class,
                ctx_attrs=kwargs.get("context_attributes", {}),
            )

            # Return the original function with a warning
            logger.warning(
                f"Klira Warning: No adapter method '{adapter_method_name}' found for '{framework}' and no Traceloop fallback available for decorator type '{decorator_type}'. Returning original function/class without tracing."
            )
            adapted_func_or_class = func_or_class

    # Final check to ensure name is preserved
    if original_name and hasattr(adapted_func_or_class, "__name__"):
        try:
            adapted_func_or_class.__name__ = original_name
        except (AttributeError, TypeError):
            pass  # Couldn't set name, not critical

    # **NEW: Wrap with unified trace runtime detection**
    # This wrapper checks at EXECUTION time whether we're in a unified trace
    # and routes to either child span creation or the standard adapted function
    return _wrap_with_unified_trace_detection(
        decorator_type=decorator_type,
        adapted_func=adapted_func_or_class,
        original_func=func_or_class,
        name=name or func_name,
        **kwargs,
    )


# --- Context-aware Decorator Definitions ---
# These functions now primarily gather context and call the core _apply_klira_decorator


def workflow_with_context(
    name: Optional[str] = None,
    version: Optional[int] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
    **other_kwargs: Any,  # Catch any other traceloop args
) -> Callable[[Any], Any]:
    """Decorator factory for a workflow entity.

    Applies framework-specific adaptation or falls back to Traceloop workflow decorator.
    Adds Klira context attributes (user_id, organization_id, project_id) if falling back.
    """
    ctx_attrs = {}
    if user_id:
        ctx_attrs["user_id"] = user_id
    if organization_id:
        ctx_attrs["organization_id"] = organization_id
    if project_id:
        ctx_attrs["project_id"] = project_id

    def decorator(func_or_class: Any) -> Any:
        # Pass context attributes and span kind for potential fallback use
        return _apply_klira_decorator(
            "workflow",
            func_or_class,
            name=name,
            version=version,
            context_attributes=ctx_attrs,
            tlp_span_kind=TraceloopSpanKindValues.WORKFLOW,
            **other_kwargs,
        )

    return decorator


def agent_with_context(
    name: Optional[str] = None,
    version: Optional[int] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    **other_kwargs: Any,
) -> Callable[[Any], Any]:
    """Decorator factory for an agent entity."""
    effective_agent_id = agent_id  # Use provided agent_id
    # We don't default agent_id to name here anymore, adapters might handle naming better

    ctx_attrs = {}
    if user_id:
        ctx_attrs["user_id"] = user_id
    if organization_id:
        ctx_attrs["organization_id"] = organization_id
    if project_id:
        ctx_attrs["project_id"] = project_id
    if effective_agent_id:
        ctx_attrs["agent_id"] = effective_agent_id

    def decorator(func_or_class: Any) -> Any:
        return _apply_klira_decorator(
            "agent",
            func_or_class,
            name=name,
            version=version,
            context_attributes=ctx_attrs,
            tlp_span_kind=TraceloopSpanKindValues.AGENT,
            **other_kwargs,
        )

    return decorator


def tool_with_context(
    name: Optional[str] = None,
    version: Optional[int] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    **other_kwargs: Any,
) -> Callable[[Any], Any]:
    """Decorator factory for a tool entity."""
    effective_tool_id = tool_id

    ctx_attrs = {}
    if user_id:
        ctx_attrs["user_id"] = user_id
    if organization_id:
        ctx_attrs["organization_id"] = organization_id
    if project_id:
        ctx_attrs["project_id"] = project_id
    if agent_id:
        ctx_attrs["agent_id"] = agent_id  # Context for fallback
    if effective_tool_id:
        ctx_attrs["tool_id"] = effective_tool_id

    def decorator(func_or_class: Any) -> Any:
        return _apply_klira_decorator(
            "tool",
            func_or_class,  # Can be function or class
            name=name,
            version=version,
            context_attributes=ctx_attrs,
            tlp_span_kind=TraceloopSpanKindValues.TOOL,
            **other_kwargs,
        )

    return decorator


def task_with_context(
    name: Optional[str] = None,
    version: Optional[int] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **other_kwargs: Any,
) -> Callable[[Any], Any]:
    """Decorator factory for a task entity."""
    effective_task_id = task_id

    ctx_attrs = {}
    if user_id:
        ctx_attrs["user_id"] = user_id
    if organization_id:
        ctx_attrs["organization_id"] = organization_id
    if project_id:
        ctx_attrs["project_id"] = project_id
    if effective_task_id:
        ctx_attrs["task_id"] = effective_task_id

    def decorator(func_or_class: Any) -> Any:
        return _apply_klira_decorator(
            "task",
            func_or_class,
            name=name,
            version=version,
            context_attributes=ctx_attrs,
            tlp_span_kind=TraceloopSpanKindValues.TASK,
            **other_kwargs,
        )

    return decorator
