"""User message trace context for unified tracing architecture."""

import uuid
from typing import Optional, Any
from opentelemetry import context, trace
from opentelemetry.trace import Status, StatusCode, Span

from klira.sdk.config import get_config


class UserMessageTraceContext:
    """
    Manages the root trace context for a user message.

    This context manager creates a unified root trace that all operations
    (workflows, agents, tasks, tools, LLM calls, guardrails) attach to as child spans.

    Key Benefits:
    - One trace per user message (instead of 6+ fragmented traces)
    - Clear hierarchical span structure
    - Proper OpenTelemetry context propagation
    - Reduced API calls (all spans batched in one trace)
    - Better observability and correlation

    Example:
        >>> from klira.sdk.tracing import start_user_message_trace
        >>>
        >>> with start_user_message_trace(
        ...     user_id="user_123",
        ...     conversation_id="conv_456"
        ... ) as trace_ctx:
        ...     # All decorated functions within this block
        ...     # will create child spans of the root trace
        ...     result = my_agent.run(user_message)
    """

    def __init__(
        self,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize the user message trace context.

        Args:
            user_id: User identifier (required)
            conversation_id: Conversation identifier (required)
            message_id: Unique message identifier (auto-generated if not provided)
            organization_id: Organization identifier (optional)
            project_id: Project identifier (optional)
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.message_id = message_id or str(uuid.uuid4())
        self.organization_id = organization_id
        self.project_id = project_id

        # Will be set in __enter__
        self.root_span: Optional[Span] = None
        self.token: Optional[Any] = None
        self._tracer = trace.get_tracer("klira")

    def __enter__(self) -> "UserMessageTraceContext":
        """
        Start the root trace and set context.

        Creates a root span named "klira.user.message" and attaches it to the
        OpenTelemetry context so all child operations inherit it.

        Returns:
            Self for context manager pattern
        """
        # Create root span for this user message
        self.root_span = self._tracer.start_span("klira.user.message")

        # Set required attributes on root span
        self.root_span.set_attribute("klira.user_id", self.user_id)
        self.root_span.set_attribute("klira.conversation_id", self.conversation_id)
        self.root_span.set_attribute("klira.message_id", self.message_id)
        self.root_span.set_attribute("klira.entity_type", "user_message")

        # Add evals_run if in eval mode
        config = get_config()
        if config and config.is_eval_mode() and config.evals_run is not None:
            self.root_span.set_attribute("klira.evals_run", config.evals_run)

        # PROD-254 Phase 2: Removed redundant organization_id and project_id
        # These are already extracted from API key metadata by the platform
        # Removing saves ~96 bytes per span and ~1.75 TB/year at scale

        # Attach context so child spans inherit it
        # This is the KEY to making all subsequent operations become child spans
        self.token = context.attach(trace.set_span_in_context(self.root_span))

        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """
        End the root trace.

        Sets span status based on whether an exception occurred,
        records the exception if present, detaches the context,
        and triggers batch export of all spans.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if not self.root_span:
            return

        # Set span status based on exception
        if exc_val:
            self.root_span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            self.root_span.record_exception(exc_val)
        else:
            self.root_span.set_status(Status(StatusCode.OK))

        # End the root span
        self.root_span.end()

        # Detach the context
        if self.token is not None:
            context.detach(self.token)

        # Trigger batch export of all spans in this trace asynchronously
        # This ensures all spans are sent in a single API call when workflow completes
        # WITHOUT blocking the user's response
        try:
            from klira.sdk import Klira

            Klira.flush_traces_async()  # Non-blocking async flush
        except Exception:
            # Don't fail if flush fails - traces will be exported on shutdown
            pass

    def get_trace_id(self) -> Optional[str]:
        """
        Get the trace ID of the root span.

        Returns:
            Trace ID as hex string, or None if span not started
        """
        if not self.root_span:
            return None

        span_context = self.root_span.get_span_context()
        if not span_context.is_valid:
            return None

        # Convert trace_id to hex string
        return format(span_context.trace_id, "032x")

    def get_span_id(self) -> Optional[str]:
        """
        Get the span ID of the root span.

        Returns:
            Span ID as hex string, or None if span not started
        """
        if not self.root_span:
            return None

        span_context = self.root_span.get_span_context()
        if not span_context.is_valid:
            return None

        # Convert span_id to hex string
        return format(span_context.span_id, "016x")


def start_user_message_trace(
    user_id: str,
    conversation_id: str,
    message_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> UserMessageTraceContext:
    """
    Start a unified trace for a user message.

    This is a convenience function that creates a UserMessageTraceContext
    to be used as a context manager. All operations within the context will
    be part of the same unified trace.

    Args:
        user_id: User identifier (required)
        conversation_id: Conversation identifier (required)
        message_id: Unique message identifier (auto-generated if not provided)
        organization_id: Organization identifier (optional)
        project_id: Project identifier (optional)

    Returns:
        UserMessageTraceContext instance ready to be used as context manager

    Example:
        >>> from klira.sdk.tracing import start_user_message_trace
        >>> from klira.sdk.decorators import workflow, agent
        >>>
        >>> @workflow(name="customer_support")
        >>> def handle_query(query: str):
        ...     return process_query(query)
        >>>
        >>> @agent(name="support_agent")
        >>> def process_query(query: str):
        ...     return "Response"
        >>>
        >>> # Use unified tracing
        >>> with start_user_message_trace(
        ...     user_id="user_123",
        ...     conversation_id="conv_456"
        ... ):
        ...     response = handle_query("How do I reset my password?")
        ...
        >>> # Result: 1 unified trace with workflow → agent hierarchy
        >>> # Instead of 2 separate root traces
    """
    return UserMessageTraceContext(
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        organization_id=organization_id,
        project_id=project_id,
    )
