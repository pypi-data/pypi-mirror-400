"""Tracing module for Klira AI SDK."""

from traceloop.sdk.tracing import (
    get_tracer,
    set_workflow_name,
)

# Import local functions
from .tracing import (
    set_conversation_context,
    set_hierarchy_context,
    clear_hierarchy_context,
    set_organization,
    set_project,
    get_current_context,
    set_association_properties,
    set_external_prompt_tracing_context,
    create_span,
    create_span_as_current,
    set_span_attribute,
    get_current_span,
)

# Import unified trace context
from .user_message_context import (
    UserMessageTraceContext,
    start_user_message_trace,
)

__all__ = [
    "get_tracer",
    "set_workflow_name",
    "set_conversation_context",
    "set_hierarchy_context",
    "clear_hierarchy_context",
    "set_organization",
    "set_project",
    "get_current_context",
    "set_association_properties",
    "set_external_prompt_tracing_context",
    "create_span",
    "create_span_as_current",
    "set_span_attribute",
    "get_current_span",
    # Unified trace context
    "UserMessageTraceContext",
    "start_user_message_trace",
]
