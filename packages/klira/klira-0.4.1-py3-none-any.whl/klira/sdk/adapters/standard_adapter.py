"""
Standard framework adapter for custom agents using @workflow + @guardrails pattern.

This adapter provides guardrails functionality for custom Python functions and methods
that don't use a recognized LLM framework (OpenAI Agents, LangChain, etc.) but still
want decorator-based policy enforcement with direct LLM API calls.
"""

import asyncio
import concurrent.futures
import logging
from typing import Any, Dict, Optional, Tuple

from klira.sdk.adapters.framework_adapter import KliraFrameworkAdapter
from klira.sdk.guardrails.engine import GuardrailsEngine

# Try to import OTel context
try:
    from opentelemetry import context as otel_context

    OTEL_CONTEXT_AVAILABLE = True
except ImportError:
    otel_context = None  # type: ignore[assignment]
    OTEL_CONTEXT_AVAILABLE = False

logger = logging.getLogger(__name__)


class StandardFrameworkAdapter(KliraFrameworkAdapter):
    """
    Framework adapter for standard Python code (custom agents).

    This adapter enables @guardrails decorator functionality for custom agents that:
    - Use @workflow class decorator
    - Use @guardrails method decorator
    - Call LLM APIs directly (Anthropic, OpenAI, etc.)
    - Don't use a recognized framework (OpenAI Agents SDK, LangChain, etc.)

    The adapter coordinates with LLM client adapters to ensure guidelines are
    properly generated, stored, and injected into API calls.
    """

    FRAMEWORK_NAME = "standard"

    def __init__(self) -> None:
        """Initialize the standard framework adapter."""
        super().__init__()
        logger.debug("Initialized StandardFrameworkAdapter")

    def adapt_workflow(
        self, func: Any, name: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Adapt a workflow function for the standard framework.

        For standard/custom agents, we don't modify the workflow function itself.
        Tracing and instrumentation is handled by the @workflow decorator directly.

        Args:
            func: The workflow function or class
            name: Optional workflow name
            **kwargs: Additional configuration

        Returns:
            The original function unchanged
        """
        logger.debug(
            f"StandardFrameworkAdapter: adapt_workflow called for {name or func.__name__}"
        )
        return func

    def adapt_task(self, func: Any, name: Optional[str] = None, **kwargs: Any) -> Any:
        """
        Adapt a task function for the standard framework.

        For standard/custom agents, we don't modify the task function itself.

        Args:
            func: The task function
            name: Optional task name
            **kwargs: Additional configuration

        Returns:
            The original function unchanged
        """
        logger.debug(
            f"StandardFrameworkAdapter: adapt_task called for {name or func.__name__}"
        )
        return func

    def adapt_agent(self, func: Any, name: Optional[str] = None, **kwargs: Any) -> Any:
        """
        Adapt an agent function/class for the standard framework.

        For standard/custom agents, we don't modify the agent itself.

        Args:
            func: The agent function or class
            name: Optional agent name
            **kwargs: Additional configuration

        Returns:
            The original function/class unchanged
        """
        logger.debug(
            f"StandardFrameworkAdapter: adapt_agent called for {name or getattr(func, '__name__', 'unknown')}"
        )
        return func

    def adapt_tool(
        self, func_or_class: Any, name: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Adapt a tool function/class for the standard framework.

        For standard/custom agents, we don't modify the tool itself.

        Args:
            func_or_class: The tool function or class
            name: Optional tool name
            **kwargs: Additional configuration

        Returns:
            The original function/class unchanged
        """
        logger.debug(
            f"StandardFrameworkAdapter: adapt_tool called for {name or getattr(func_or_class, '__name__', 'unknown')}"
        )
        return func_or_class

    def apply_input_guardrails(
        self,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        func_name: str,
        injection_strategy: str = "auto",
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any], bool, str]:
        """
        Apply input guardrails to function arguments.

        Evaluates the input message against policies and generates guidelines
        if augmentation is needed. Guidelines are stored in context for LLM
        client adapters to retrieve and inject.

        Args:
            args: Positional arguments to the decorated function
            kwargs: Keyword arguments to the decorated function
            func_name: Name of the decorated function
            injection_strategy: Strategy for guideline injection (auto/instructions/completion)

        Returns:
            Tuple of (modified_args, modified_kwargs, blocked, reason)
            - modified_args/kwargs: Potentially modified arguments
            - blocked: True if input violates policy
            - reason: Explanation if blocked
        """
        # Note: This is the synchronous version. For async code, use _async_apply_input_guardrails

        try:
            # Extract message to evaluate
            message = self._extract_message_from_args(args, kwargs, func_name)

            if not message:
                logger.debug(
                    f"No message found in {func_name} args for input guardrails"
                )
                return args, kwargs, False, ""

            # Get guardrails engine
            engine = GuardrailsEngine.get_instance()

            # Prepare context
            context = {
                "function_name": func_name,
                "framework": "standard",
                "injection_strategy": injection_strategy,
            }

            # Execute the async process_message, handling existing event loops
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, run in a thread pool
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, engine.process_message(message, context)
                        )
                        result = future.result()
                else:
                    result = loop.run_until_complete(
                        engine.process_message(message, context)
                    )
            except RuntimeError:
                # No event loop available, create a new one
                result = asyncio.run(engine.process_message(message, context))

            # Check if blocked
            blocked = not result.get("allowed", True)
            reason_raw = result.get(
                "response", "Request blocked due to policy violation."
            )
            reason = (
                str(reason_raw)
                if reason_raw
                else "Request blocked due to policy violation."
            )

            if blocked:
                logger.warning(f"Input blocked by guardrails in {func_name}: {reason}")
                return args, kwargs, True, reason

            # Extract and store guidelines if augmentation occurred
            augmentation_result = result.get("augmentation_result", {})
            if augmentation_result:
                guidelines = augmentation_result.get("guidelines", [])
                if guidelines:
                    logger.debug(
                        f"Storing {len(guidelines)} guidelines for {func_name}"
                    )
                    # Store guidelines in OTel context for LLM adapters to retrieve
                    if otel_context and OTEL_CONTEXT_AVAILABLE:
                        try:
                            current_ctx = otel_context.get_current()
                            new_ctx = otel_context.set_value(
                                "klira.augmentation.guidelines",
                                guidelines,
                                current_ctx,
                            )
                            otel_context.attach(new_ctx)
                            logger.debug(
                                f"Stored {len(guidelines)} guidelines in OTel context"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to store guidelines in OTel context: {e}"
                            )

            return args, kwargs, False, ""

        except Exception as e:
            logger.error(
                f"Error in apply_input_guardrails for {func_name}: {e}", exc_info=True
            )
            # Fail open - allow execution
            return args, kwargs, False, ""

    async def _async_apply_input_guardrails(
        self,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        func_name: str,
        injection_strategy: str = "auto",
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any], bool, str]:
        """Async version of apply_input_guardrails."""
        try:
            # Extract message to evaluate
            message = self._extract_message_from_args(args, kwargs, func_name)

            if not message:
                logger.debug(
                    f"No message found in {func_name} args for input guardrails"
                )
                return args, kwargs, False, ""

            # Get guardrails engine
            engine = GuardrailsEngine.get_instance()

            # Prepare context
            context = {
                "function_name": func_name,
                "framework": "standard",
                "injection_strategy": injection_strategy,
            }

            # Evaluate message
            result = await engine.process_message(message, context)

            # Check if blocked
            blocked = not result.get("allowed", True)
            reason_raw = result.get(
                "response", "Request blocked due to policy violation."
            )
            reason = (
                str(reason_raw)
                if reason_raw
                else "Request blocked due to policy violation."
            )

            if blocked:
                logger.warning(f"Input blocked by guardrails in {func_name}: {reason}")
                return args, kwargs, True, reason

            # Extract and store guidelines if augmentation occurred
            augmentation_result = result.get("augmentation_result", {})
            if augmentation_result:
                guidelines = augmentation_result.get("guidelines", [])
                if guidelines:
                    logger.debug(
                        f"Storing {len(guidelines)} guidelines for {func_name}"
                    )
                    # Store guidelines in OTel context for LLM adapters to retrieve
                    if otel_context and OTEL_CONTEXT_AVAILABLE:
                        try:
                            current_ctx = otel_context.get_current()
                            new_ctx = otel_context.set_value(
                                "klira.augmentation.guidelines",
                                guidelines,
                                current_ctx,
                            )
                            otel_context.attach(new_ctx)
                            logger.debug(
                                f"Stored {len(guidelines)} guidelines in OTel context"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to store guidelines in OTel context: {e}"
                            )

            return args, kwargs, False, ""

        except Exception as e:
            logger.error(
                f"Error in _async_apply_input_guardrails for {func_name}: {e}",
                exc_info=True,
            )
            # Fail open - allow execution
            return args, kwargs, False, ""

    def apply_output_guardrails(
        self, result: Any, func_name: str
    ) -> Tuple[Any, bool, str]:
        """
        Apply output guardrails to function result.

        Evaluates the output against policies and blocks or modifies if needed.

        Args:
            result: The result returned by the decorated function
            func_name: Name of the decorated function

        Returns:
            Tuple of (modified_result, blocked, alternative_response)
            - modified_result: Potentially modified result
            - blocked: True if output violates policy
            - alternative_response: Replacement response if blocked
        """
        # Note: This is the synchronous version. For async code, use _async_apply_output_guardrails

        try:
            # Extract output text
            output_text = self._extract_output_text(result)

            if not output_text:
                logger.debug(
                    f"No output text found in {func_name} result for output guardrails"
                )
                return result, False, ""

            # Get guardrails engine
            engine = GuardrailsEngine.get_instance()

            # Prepare context
            context = {
                "function_name": func_name,
                "framework": "standard",
            }

            # Execute the async evaluate, handling existing event loops
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, run in a thread pool
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            engine.evaluate(
                                input_text=output_text,
                                context=context,
                                direction="outbound",
                            ),
                        )
                        decision = future.result()
                else:
                    decision = loop.run_until_complete(
                        engine.evaluate(
                            input_text=output_text,
                            context=context,
                            direction="outbound",
                        )
                    )
            except RuntimeError:
                # No event loop available, create a new one
                decision = asyncio.run(
                    engine.evaluate(
                        input_text=output_text, context=context, direction="outbound"
                    )
                )

            # Check if blocked
            blocked = not decision.allowed

            if blocked:
                logger.warning(
                    f"Output blocked by guardrails in {func_name}: {decision.reason}"
                )
                alternative = f"[BLOCKED BY GUARDRAILS] - {decision.reason}"
                return result, True, alternative

            return result, False, ""

        except Exception as e:
            logger.error(
                f"Error in apply_output_guardrails for {func_name}: {e}", exc_info=True
            )
            # Fail open - return original result
            return result, False, ""

    async def _async_apply_output_guardrails(
        self, result: Any, func_name: str
    ) -> Tuple[Any, bool, str]:
        """Async version of apply_output_guardrails."""
        try:
            # Extract output text
            output_text = self._extract_output_text(result)

            if not output_text:
                logger.debug(
                    f"No output text found in {func_name} result for output guardrails"
                )
                return result, False, ""

            # Get guardrails engine
            engine = GuardrailsEngine.get_instance()

            # Prepare context
            context = {
                "function_name": func_name,
                "framework": "standard",
            }

            # Evaluate output
            decision = await engine.evaluate(
                input_text=output_text, context=context, direction="outbound"
            )

            # Check if blocked
            blocked = not decision.allowed

            if blocked:
                logger.warning(
                    f"Output blocked by guardrails in {func_name}: {decision.reason}"
                )
                alternative = f"[BLOCKED BY GUARDRAILS] - {decision.reason}"
                return result, True, alternative

            return result, False, ""

        except Exception as e:
            logger.error(
                f"Error in _async_apply_output_guardrails for {func_name}: {e}",
                exc_info=True,
            )
            # Fail open - return original result
            return result, False, ""

    def apply_augmentation(
        self,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        guidelines: list[str],
        func_name: str,
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        """
        Apply augmentation by storing guidelines.

        For the standard adapter, we rely on LLM client adapters to retrieve
        and inject guidelines at API call time. This method primarily serves
        to ensure guidelines are available in context.

        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            guidelines: Policy guidelines to inject
            func_name: Function name

        Returns:
            Tuple of (args, kwargs) - unchanged for standard adapter
        """
        if guidelines:
            logger.debug(
                f"Guidelines already stored in context for {func_name}, "
                f"LLM client adapters will inject them at API call time"
            )

        # Return unchanged - LLM adapters handle injection
        return args, kwargs

    def _extract_message_from_args(
        self, args: Tuple[Any, ...], kwargs: Dict[str, Any], func_name: str
    ) -> Optional[str]:
        """
        Extract message text from function arguments.

        Tries common patterns:
        1. First positional arg if it's a string
        2. 'message', 'text', 'input', 'user_input', 'prompt' kwargs
        3. 'messages' kwarg (list of dicts with 'content')

        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            func_name: Function name (for logging)

        Returns:
            Extracted message text or None
        """
        # Try first positional arg if string
        # Note: For instance methods, args[0] is 'self', so check args[1] too
        if args and len(args) > 0:
            if isinstance(args[0], str):
                return args[0]
            elif len(args) > 1 and isinstance(args[1], str):
                # Instance method - args[0] is self, args[1] is the actual first arg
                return args[1]

        # Try common kwarg names
        for key in ["message", "text", "input", "user_input", "prompt", "query"]:
            if key in kwargs and isinstance(kwargs[key], str):
                return kwargs[key]

        # Try messages list (OpenAI/Anthropic format)
        if "messages" in kwargs:
            messages = kwargs["messages"]
            if isinstance(messages, list) and messages:
                # Get last user message
                for msg in reversed(messages):
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        content = msg.get("content")
                        if isinstance(content, str):
                            return content
                        elif isinstance(content, list):
                            # Handle list of content blocks
                            texts = [
                                block.get("text", "")
                                for block in content
                                if isinstance(block, dict) and "text" in block
                            ]
                            if texts:
                                return " ".join(texts)

        logger.debug(f"Could not extract message from {func_name} arguments")
        return None

    def _extract_output_text(self, result: Any) -> Optional[str]:
        """
        Extract text from function result.

        Handles:
        1. String results (direct text)
        2. Objects with 'text', 'content', 'output' attributes
        3. Dicts with 'text', 'content', 'output' keys
        4. Lists of content blocks

        Args:
            result: Function result

        Returns:
            Extracted text or None
        """
        # Direct string
        if isinstance(result, str):
            return result

        # Object attributes
        for attr in ["text", "content", "output", "response"]:
            if hasattr(result, attr):
                value = getattr(result, attr)
                if isinstance(value, str):
                    return value
                elif isinstance(value, list):
                    # Handle list of content blocks
                    texts = []
                    for item in value:
                        if isinstance(item, dict) and "text" in item:
                            texts.append(item["text"])
                        elif isinstance(item, str):
                            texts.append(item)
                        elif hasattr(item, "text"):
                            texts.append(item.text)
                    if texts:
                        return " ".join(texts)

        # Dict keys
        if isinstance(result, dict):
            for key in ["text", "content", "output", "response"]:
                if key in result and isinstance(result[key], str):
                    return result[key]

        # Fallback to str()
        try:
            return str(result)
        except Exception:
            return None
