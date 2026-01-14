"""Adapter for patching the OpenAI Chat Completion API."""

import logging
from typing import Any, Dict, Optional

from klira.sdk.adapters.llm_base_adapter import BaseLLMAdapter

# Try to import OpenAI client for patching
try:
    import openai

    OPENAI_CLIENT_AVAILABLE = True
except ImportError:
    openai = None  # type: ignore[assignment]
    OPENAI_CLIENT_AVAILABLE = False

# Try to import OTel context
try:
    from opentelemetry import context as otel_context
except ImportError:
    otel_context = None  # type: ignore[assignment]

logger = logging.getLogger("klira.adapters.openai_completion")


class OpenAICompletionAdapter(BaseLLMAdapter):
    """Patches OpenAI Chat Completion API calls for guideline injection."""

    is_available = OPENAI_CLIENT_AVAILABLE

    def __init__(self) -> None:
        super().__init__()
        from typing import Callable

        self.original_create: Optional[Callable[..., Any]] = None
        self.original_acreate: Optional[Callable[..., Any]] = None
        self._patched: bool = False

    def patch(self) -> None:
        """Patch the OpenAI chat.completions.create method."""
        if self._patched:
            logger.debug("OpenAI client already patched")
            return

        logger.debug(
            "OpenAICompletionAdapter: Attempting to patch openai.chat.completions methods..."
        )

        # Get the original method directly from openai
        original_create = openai.chat.completions.create
        self.original_create = original_create

        # Define wrapper function
        def patched_create(*args: Any, **kwargs: Any) -> Any:
            from klira.sdk.tracing.tracing import get_tracer as get_traceloop_tracer
            from opentelemetry.trace import StatusCode
            from opentelemetry import trace as otel_trace

            # Extract model and parameters
            model = kwargs.get("model", "unknown")
            temperature = kwargs.get("temperature")
            max_tokens = kwargs.get("max_tokens")

            # Check if we're in a unified trace context
            if self._is_in_unified_trace():
                # Use OpenTelemetry tracer directly to create child span
                tracer = otel_trace.get_tracer("klira")
            else:
                # Use Traceloop tracer for standard behavior
                tracer = get_traceloop_tracer()

            # Create LLM request span
            with tracer.start_as_current_span("klira.llm.request") as llm_span:
                try:
                    # Extract messages from args/kwargs
                    messages = kwargs.get("messages") or (
                        args[0].get("messages")
                        if args and isinstance(args[0], dict)
                        else []
                    )

                    # Store original messages before augmentation
                    import copy

                    original_messages = copy.deepcopy(messages) if messages else None

                    # Set request attributes
                    self._create_llm_request_span(
                        llm_span,
                        provider="openai",
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                    # Add augmentation tracking if guidelines present (pass original messages)
                    self._add_augmentation_attributes(
                        llm_span, original_messages=original_messages
                    )

                    if messages:
                        # Find the first system message
                        system_msg = next(
                            (m for m in messages if m.get("role") == "system"), None
                        )
                        if system_msg and isinstance(system_msg.get("content"), str):
                            from klira.sdk.guardrails.engine import GuardrailsEngine

                            guidelines = GuardrailsEngine.get_current_guidelines()

                            if guidelines:
                                # Build augmentation text
                                augmentation_text = "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                augmentation_text += "\n".join(
                                    [f"• {g}" for g in guidelines]
                                )

                                # Inject into system prompt
                                system_msg["content"] += augmentation_text

                                # Clear context to prevent double-injection
                                GuardrailsEngine.clear_current_guidelines()

                                # Debug logging
                                logger.info(
                                    f"Injected {len(guidelines)} policy guidelines into system prompt"
                                )
                except Exception as e:
                    logger.error(f"Policy injection error: {str(e)}")

                try:
                    # Call the original method
                    result = original_create(*args, **kwargs)

                    # Add response attributes
                    self._add_llm_response_attributes(llm_span, result, "openai")

                    llm_span.set_status(StatusCode.OK)

                except Exception as e:
                    llm_span.set_status(StatusCode.ERROR, str(e))
                    llm_span.record_exception(e)
                    raise

                # Apply outbound guardrails evaluation
                result = self._apply_outbound_guardrails(result)

                return result

        # Apply patch directly to openai
        openai.chat.completions.create = patched_create  # type: ignore[method-assign]
        logger.info(
            "Successfully patched openai.chat.completions.create for augmentation."
        )

        # Also patch the async variant if available
        try:
            # Check if acreate exists before attempting to patch it
            if hasattr(openai.chat.completions, "acreate"):
                original_acreate = openai.chat.completions.acreate
                self.original_acreate = original_acreate

                async def patched_acreate(*args: Any, **kwargs: Any) -> Any:
                    from klira.sdk.tracing.tracing import (
                        get_tracer as get_traceloop_tracer,
                    )
                    from opentelemetry.trace import StatusCode
                    from opentelemetry import trace as otel_trace

                    # Extract model and parameters
                    model = kwargs.get("model", "unknown")
                    temperature = kwargs.get("temperature")
                    max_tokens = kwargs.get("max_tokens")

                    # Check if we're in a unified trace context
                    if self._is_in_unified_trace():
                        # Use OpenTelemetry tracer directly to create child span
                        tracer = otel_trace.get_tracer("klira")
                    else:
                        # Use Traceloop tracer for standard behavior
                        tracer = get_traceloop_tracer()

                    # Create LLM request span
                    with tracer.start_as_current_span("klira.llm.request") as llm_span:
                        try:
                            # Extract messages from args/kwargs
                            messages = kwargs.get("messages") or (
                                args[0].get("messages")
                                if args and isinstance(args[0], dict)
                                else []
                            )

                            # Store original messages before augmentation
                            import copy

                            original_messages = (
                                copy.deepcopy(messages) if messages else None
                            )

                            # Set request attributes
                            self._create_llm_request_span(
                                llm_span,
                                provider="openai",
                                model=model,
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )

                            # Add augmentation tracking if guidelines present (pass original messages)
                            self._add_augmentation_attributes(
                                llm_span, original_messages=original_messages
                            )

                            if messages:
                                system_msg = next(
                                    (m for m in messages if m.get("role") == "system"),
                                    None,
                                )
                                if system_msg and isinstance(
                                    system_msg.get("content"), str
                                ):
                                    from klira.sdk.guardrails.engine import (
                                        GuardrailsEngine,
                                    )

                                    guidelines = (
                                        GuardrailsEngine.get_current_guidelines()
                                    )
                                    if guidelines:
                                        augmentation_text = (
                                            "\n\nIMPORTANT POLICY DIRECTIVES:\n"
                                        )
                                        augmentation_text += "\n".join(
                                            [f"• {g}" for g in guidelines]
                                        )
                                        system_msg["content"] += augmentation_text
                                        GuardrailsEngine.clear_current_guidelines()
                                        logger.info(
                                            f"Injected {len(guidelines)} policy guidelines into async system prompt"
                                        )
                        except Exception as e:
                            logger.error(
                                f"Policy injection error in async completion: {str(e)}"
                            )

                        try:
                            result = await original_acreate(*args, **kwargs)

                            # Add response attributes
                            self._add_llm_response_attributes(
                                llm_span, result, "openai"
                            )

                            llm_span.set_status(StatusCode.OK)

                        except Exception as e:
                            llm_span.set_status(StatusCode.ERROR, str(e))
                            llm_span.record_exception(e)
                            raise

                        # Apply outbound guardrails evaluation
                        result = await self._apply_outbound_guardrails_async(result)

                        return result

                openai.chat.completions.acreate = patched_acreate
                logger.info(
                    "Successfully patched async openai.chat.completions.acreate for augmentation."
                )
            else:
                logger.debug(
                    "OpenAI async completions (acreate) not found, skipping patch."
                )
        except Exception as e:
            logger.debug(f"Failed to patch async completions: {e}")

        self._patched = True

    def _apply_outbound_guardrails(self, result: Any) -> Any:
        """Apply outbound guardrails to OpenAI completion results (synchronous)."""
        try:
            # Import here to avoid circular imports
            from klira.sdk.guardrails.engine import GuardrailsEngine

            # Extract content from OpenAI response
            response_text = self._extract_response_content(result)
            if not response_text.strip():
                return result

            # Create evaluation context
            context = {
                "llm_client": "openai",
                "function_name": "openai.chat.completions.create",
            }

            # Get guardrails engine and evaluate
            engine = GuardrailsEngine.get_instance()

            # Run async evaluation in sync context using asyncio
            import asyncio

            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, we can't use run_until_complete
                    # Return the result without evaluation and log a warning
                    logger.warning(
                        "Cannot run outbound guardrails evaluation for OpenAI completion in sync context within async loop. "
                        "Consider using async methods."
                    )
                    return result
                else:
                    # We can safely run the async evaluation
                    decision = loop.run_until_complete(
                        engine.evaluate(response_text, context, direction="outbound")
                    )
            except RuntimeError:
                # No event loop, create one
                decision = asyncio.run(
                    engine.evaluate(response_text, context, direction="outbound")
                )

            if not decision.allowed:
                logger.warning(
                    f"OpenAI completion outbound guardrails blocked response: {decision.reason}"
                )
                # Return a modified response with blocked content
                return self._create_blocked_response(
                    result, decision.reason or "Content policy violation detected"
                )

            return result

        except Exception as e:
            logger.error(
                f"Error applying outbound guardrails for OpenAI completion: {e}",
                exc_info=True,
            )
            # Fail open - return original result
            return result

    async def _apply_outbound_guardrails_async(self, result: Any) -> Any:
        """Apply outbound guardrails to OpenAI completion results (asynchronous)."""
        try:
            # Import here to avoid circular imports
            from klira.sdk.guardrails.engine import GuardrailsEngine

            # Extract content from OpenAI response
            response_text = self._extract_response_content(result)
            if not response_text.strip():
                return result

            # Create evaluation context
            context = {
                "llm_client": "openai",
                "function_name": "openai.chat.completions.acreate",
            }

            # Get guardrails engine and evaluate
            engine = GuardrailsEngine.get_instance()
            decision = await engine.evaluate(
                response_text, context, direction="outbound"
            )

            if not decision.allowed:
                logger.warning(
                    f"OpenAI async completion outbound guardrails blocked response: {decision.reason}"
                )
                # Return a modified response with blocked content
                return self._create_blocked_response(
                    result, decision.reason or "Content policy violation detected"
                )

            return result

        except Exception as e:
            logger.error(
                f"Error applying outbound guardrails for OpenAI async completion: {e}",
                exc_info=True,
            )
            # Fail open - return original result
            return result

    def _extract_response_content(self, result: Any) -> str:
        """Extract text content from OpenAI response object."""
        try:
            # Handle different OpenAI response formats
            if hasattr(result, "choices") and result.choices:
                choice = result.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return str(choice.message.content) if choice.message.content else ""
                elif hasattr(choice, "text"):
                    return str(choice.text) if choice.text else ""

            # Fallback: try to convert to string
            return str(result) if result else ""

        except Exception as e:
            logger.debug(f"Error extracting content from OpenAI response: {e}")
            return ""

    def _create_blocked_response(self, original_result: Any, reason: str) -> Any:
        """Create a blocked response that matches the original response format."""
        try:
            blocked_message = (
                f"[BLOCKED BY GUARDRAILS] - {reason}"
                if reason
                else "[BLOCKED BY GUARDRAILS] - Content policy violation detected"
            )

            # Try to modify the original response in place
            if hasattr(original_result, "choices") and original_result.choices:
                choice = original_result.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    choice.message.content = blocked_message
                    return original_result
                elif hasattr(choice, "text"):
                    choice.text = blocked_message
                    return original_result

            # Fallback: return the blocked message as string
            return blocked_message

        except Exception as e:
            logger.error(f"Error creating blocked response: {e}")
            # Ultimate fallback
            return "[BLOCKED BY GUARDRAILS] - Content policy violation detected"

    def _extract_prompt_text(self, messages: Any, provider: str) -> str:
        """Extract prompt text from OpenAI messages."""
        if isinstance(messages, list):
            # Combine all message contents
            parts = []
            for msg in messages:
                if isinstance(msg, dict) and "content" in msg:
                    parts.append(f"{msg.get('role', 'user')}: {msg['content']}")
            return "\n".join(parts)
        return str(messages)

    def _extract_response_text(self, response: Any, provider: str) -> str:
        """Extract response text from OpenAI response."""
        try:
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return str(choice.message.content) if choice.message.content else ""
            return ""
        except Exception as e:
            logger.debug(f"Error extracting OpenAI response text: {e}")
            return ""

    def _extract_token_usage(
        self, response: Any, provider: str
    ) -> Optional[Dict[str, int]]:
        """Extract token usage from OpenAI response."""
        try:
            if hasattr(response, "usage"):
                return {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                }
            return None
        except Exception as e:
            logger.debug(f"Error extracting OpenAI token usage: {e}")
            return None

    def _extract_finish_reason(self, response: Any, provider: str) -> Optional[str]:
        """Extract finish reason from OpenAI response."""
        try:
            if hasattr(response, "choices") and response.choices:
                return response.choices[0].finish_reason
            return None
        except Exception as e:
            logger.debug(f"Error extracting OpenAI finish reason: {e}")
            return None

    def _extract_response_model(self, response: Any, provider: str) -> Optional[str]:
        """Extract model name from OpenAI response."""
        try:
            if hasattr(response, "model") and response.model is not None:
                return str(response.model)
            return None
        except Exception as e:
            logger.debug(f"Error extracting OpenAI response model: {e}")
            return None

    def unpatch_llm_client(self) -> bool:
        """Restore original OpenAI client methods."""
        if not OPENAI_CLIENT_AVAILABLE or not self._patched:
            return False

        try:
            # Restore completions.create
            if self.original_create:
                openai.chat.completions.create = self.original_create  # type: ignore[method-assign]
                self.original_create = None

            # Restore async create
            if self.original_acreate:
                openai.chat.completions.acreate = self.original_acreate  # type: ignore[attr-defined]
                self.original_acreate = None

            self._patched = False
            logger.info("Successfully unpatched OpenAI client methods")
            return True

        except Exception as e:
            logger.error(f"Failed to unpatch OpenAI client: {e}")
            return False

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI client."""
        if not OPENAI_CLIENT_AVAILABLE:
            return {"available": False, "reason": "openai not installed"}

        try:
            return {
                "available": True,
                "library": "openai",
                "version": getattr(openai, "__version__", "unknown"),
                "patched": self._patched,
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}
