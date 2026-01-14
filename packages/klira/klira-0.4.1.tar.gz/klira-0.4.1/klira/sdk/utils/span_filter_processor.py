"""Span processor to filter out None values from span attributes before export.

This prevents OpenTelemetry encoding errors when attributes are set to None.
"""

import logging
from typing import Optional
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter

logger = logging.getLogger(__name__)


class NoneAttributeFilterProcessor(SpanProcessor):
    """Span processor that filters out None values from span attributes.

    This prevents OpenTelemetry encoding errors when attributes are set to None,
    particularly for gen_ai.response.model and other attributes that might be
    extracted from response objects with None values.
    """

    def __init__(self, exporter: SpanExporter) -> None:
        """Initialize the filter processor with an exporter.

        Args:
            exporter: The span exporter to use after filtering
        """
        self._exporter = exporter

    def on_start(
        self, span: ReadableSpan, parent_context: Optional[object] = None
    ) -> None:
        """Called when a span is started."""
        # No filtering needed on start
        pass

    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends. Filters None values before exporting."""
        # Filter out None values from attributes
        if hasattr(span, "attributes") and span.attributes:
            filtered_attributes = {}
            for key, value in span.attributes.items():
                if value is not None:
                    filtered_attributes[key] = value

            # Replace attributes with filtered version
            # Note: ReadableSpan.attributes is immutable (BoundedAttributes)
            # We can only modify internal _attributes on SDK Span implementation
            if hasattr(span, "_attributes"):
                span._attributes = filtered_attributes

        # Export the span
        self._exporter.export([span])

    def shutdown(self) -> None:
        """Shutdown the processor and exporter."""
        self._exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush the exporter.

        Args:
            timeout_millis: Timeout in milliseconds (default: 30000)

        Returns:
            True if flush succeeded, False otherwise
        """
        if hasattr(self._exporter, "force_flush"):
            return self._exporter.force_flush(timeout_millis)
        return True
