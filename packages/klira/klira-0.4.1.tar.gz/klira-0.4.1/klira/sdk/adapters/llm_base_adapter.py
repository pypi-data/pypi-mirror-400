"""Abstract base class for LLM client adapters."""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional
from opentelemetry.trace import Span
from opentelemetry import trace, context

logger = logging.getLogger("klira.adapters.llm_base")


class BaseLLMAdapter(ABC):
    """Abstract base class for adapters that patch specific LLM client libraries."""

    # Indicates if the corresponding LLM library is available
    is_available: bool = False

    @abstractmethod
    def patch(self) -> None:
        """Apply patches to the underlying LLM client library for augmentation injection."""
        raise NotImplementedError

    # Shared helper methods for unified trace detection

    def _is_in_unified_trace(self) -> bool:
        """Check if we're currently in a unified trace context.

        Returns:
            True if currently in a unified trace context, False otherwise.
        """
        try:
            current_span = trace.get_current_span()
            if not current_span:
                return False

            span_context = current_span.get_span_context()
            if not span_context or not span_context.is_valid:
                return False

            # Check if the current span is a unified trace root
            # Note: Span interface doesn't expose name, but SDK implementation does
            if (
                hasattr(current_span, "name")
                and current_span.name == "klira.user.message"
            ):
                return True

            # Check if we're a descendant by looking for klira.user_id in context
            try:
                user_id_in_context = context.get_value("klira.user_id")
                if user_id_in_context:
                    return True
            except Exception:
                pass

            return False
        except Exception as e:
            logger.debug(f"Error checking unified trace context: {e}")
            return False

    # Shared helper methods for LLM span creation

    def _create_llm_request_span(
        self, span: Span, provider: str, model: str, messages: Any, **kwargs: Any
    ) -> None:
        """Create LLM request span with GenAI semantic conventions.

        Args:
            span: The OpenTelemetry span to set attributes on
            provider: LLM provider name (openai, anthropic, gemini, ollama)
            model: Model identifier
            messages: Messages/prompt data
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        """
        from klira.sdk.config import (
            is_prompt_logging_enabled,
            get_prompt_truncation_limit,
        )
        from klira.sdk.utils.span_utils import safe_set_span_attribute

        # Set provider and model
        safe_set_span_attribute(span, "gen_ai.system", provider)
        safe_set_span_attribute(span, "gen_ai.request.model", model)

        # Extract and log prompts if enabled
        if is_prompt_logging_enabled():
            prompt_text = self._extract_prompt_text(messages, provider)
            truncated_prompt = self._truncate_text(
                prompt_text, get_prompt_truncation_limit()
            )
            safe_set_span_attribute(span, "gen_ai.prompt", truncated_prompt)

        # Set request parameters
        if "temperature" in kwargs:
            safe_set_span_attribute(
                span, "gen_ai.request.temperature", kwargs["temperature"]
            )
        if "max_tokens" in kwargs:
            safe_set_span_attribute(
                span, "gen_ai.request.max_tokens", kwargs["max_tokens"]
            )
        if "top_p" in kwargs:
            safe_set_span_attribute(span, "gen_ai.request.top_p", kwargs["top_p"])

    def _add_llm_response_attributes(
        self, span: Span, response: Any, provider: str
    ) -> None:
        """Add LLM response attributes to span.

        Args:
            span: The OpenTelemetry span to set attributes on
            response: LLM response object
            provider: LLM provider name
        """
        from klira.sdk.config import (
            is_prompt_logging_enabled,
            get_response_truncation_limit,
        )
        from klira.sdk.utils.span_utils import safe_set_span_attribute

        # Extract response content
        if is_prompt_logging_enabled():
            response_text = self._extract_response_text(response, provider)
            truncated_response = self._truncate_text(
                response_text, get_response_truncation_limit()
            )
            safe_set_span_attribute(span, "gen_ai.response.text", truncated_response)

        # Extract model from response (if available)
        # This prevents OpenTelemetry from trying to set it to None
        response_model = self._extract_response_model(response, provider)
        if response_model:
            safe_set_span_attribute(span, "gen_ai.response.model", response_model)

        # Extract token usage
        token_usage = self._extract_token_usage(response, provider)
        if token_usage:
            if "input_tokens" in token_usage:
                safe_set_span_attribute(
                    span, "gen_ai.usage.input_tokens", token_usage["input_tokens"]
                )
            if "output_tokens" in token_usage:
                safe_set_span_attribute(
                    span, "gen_ai.usage.output_tokens", token_usage["output_tokens"]
                )

        # Extract finish reason
        finish_reason = self._extract_finish_reason(response, provider)
        if finish_reason:
            safe_set_span_attribute(
                span, "gen_ai.response.finish_reasons", [finish_reason]
            )

    def _extract_prompt_text(self, messages: Any, provider: str) -> str:
        """Extract prompt text from messages based on provider format.

        Override in subclass for provider-specific extraction.
        """
        return str(messages)

    def _extract_response_text(self, response: Any, provider: str) -> str:
        """Extract response text from response object based on provider format.

        Override in subclass for provider-specific extraction.
        """
        return str(response)

    def _extract_token_usage(
        self, response: Any, provider: str
    ) -> Optional[Dict[str, int]]:
        """Extract token usage from response object.

        Override in subclass for provider-specific extraction.
        Returns dict with 'input_tokens' and 'output_tokens' keys.
        """
        return None

    def _extract_response_model(self, response: Any, provider: str) -> Optional[str]:
        """Extract model name from response object.

        Override in subclass for provider-specific extraction.
        This prevents OpenTelemetry from trying to set gen_ai.response.model to None.

        Args:
            response: LLM response object
            provider: LLM provider name

        Returns:
            Model name string if found, None otherwise
        """
        # Default implementation: try to get model attribute if it exists and is not None
        try:
            if hasattr(response, "model") and response.model is not None:
                return str(response.model)
        except Exception:
            pass
        return None

    def _extract_finish_reason(self, response: Any, provider: str) -> Optional[str]:
        """Extract finish reason from response object.

        Override in subclass for provider-specific extraction.
        """
        return None

    def _truncate_text(self, text: str, limit: int) -> str:
        """Truncate text to specified limit with ellipsis."""
        if len(text) <= limit:
            return text
        return text[:limit] + "..."

    def _add_augmentation_attributes(
        self, span: Span, original_messages: Any = None
    ) -> None:
        """Add augmentation tracking attributes to span.

        Args:
            span: The span to add attributes to
            original_messages: Original messages before augmentation (optional)
        """
        from klira.sdk.guardrails.engine import GuardrailsEngine
        from klira.sdk.utils.span_utils import safe_set_span_attribute
        from klira.sdk.config import (
            is_prompt_logging_enabled,
            get_prompt_truncation_limit,
        )

        # Check if guidelines were injected
        guidelines = GuardrailsEngine.get_current_guidelines()
        if guidelines:
            safe_set_span_attribute(span, "llm.guardrails.augmented", True)
            safe_set_span_attribute(
                span, "llm.guardrails.policies_injected", len(guidelines)
            )
            safe_set_span_attribute(
                span, "llm.guardrails.policy_list", guidelines[:5]
            )  # First 5 policies

            # Store original prompt if available and logging enabled
            if original_messages is not None and is_prompt_logging_enabled():
                original_prompt = self._extract_prompt_text(
                    original_messages, "unknown"
                )
                truncated_original = self._truncate_text(
                    original_prompt, get_prompt_truncation_limit()
                )
                safe_set_span_attribute(
                    span, "gen_ai.prompt.original", truncated_original
                )
