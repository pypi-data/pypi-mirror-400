"""Unified trace exporter for batching spans into single API calls.

This module provides a custom OTLP span exporter that batches all spans
from a single trace into one API call to the Klira backend, reducing
API overhead by ~80-90%.

The exporter uses OpenTelemetry's standard OTLP protobuf format and adds
Bearer token authentication for the Klira API.
"""

import logging
from typing import Optional, Dict, Any, Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExporter,
    SpanExportResult,
    BatchSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


logger = logging.getLogger(__name__)


class KliraOTLPSpanExporter(SpanExporter):
    """Custom OTLP span exporter that sends batched spans to Klira API.

    This exporter extends the standard OTLP HTTP exporter with:
    - Bearer token authentication for Klira API
    - Automatic endpoint configuration
    - Custom headers for Klira-specific metadata

    The exporter works with OpenTelemetry's BatchSpanProcessor to automatically
    batch spans from the same trace into a single API call.

    Example:
        >>> from klira.sdk.telemetry.unified_exporter import KliraOTLPSpanExporter
        >>> from opentelemetry.sdk.trace.export import BatchSpanProcessor
        >>>
        >>> exporter = KliraOTLPSpanExporter(
        ...     api_key="klira_...",
        ...     endpoint="https://api.getklira.com/v1/traces"
        ... )
        >>> processor = BatchSpanProcessor(
        ...     exporter,
        ...     max_export_batch_size=512,  # Batch up to 512 spans
        ...     schedule_delay_millis=5000   # Wait 5s before sending
        ... )
    """

    def __init__(
        self,
        api_key: str,
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        **kwargs: Any,
    ):
        """Initialize the Klira OTLP span exporter.

        Args:
            api_key: Klira API key (required, must start with 'klira_')
            endpoint: OTLP endpoint URL. Defaults to https://api.getklira.com/v1/traces
            headers: Additional HTTP headers to send with requests
            timeout: Request timeout in seconds (default: 10)
            **kwargs: Additional arguments passed to OTLPSpanExporter

        Raises:
            ValueError: If api_key is missing or has invalid format
        """
        if not api_key:
            raise ValueError("api_key is required for KliraOTLPSpanExporter")
        if not api_key.startswith("klira_"):
            raise ValueError("api_key must start with 'klira_'")

        # Set default endpoint if not provided
        if endpoint is None:
            endpoint = "https://api.getklira.com/v1/traces"

        # Prepare headers with Bearer token authentication
        final_headers = headers.copy() if headers else {}
        final_headers["Authorization"] = f"Bearer {api_key}"

        # Initialize the underlying OTLP exporter
        # The OTLPSpanExporter handles all the protobuf encoding and HTTP transport
        self._otlp_exporter = OTLPSpanExporter(
            endpoint=endpoint, headers=final_headers, timeout=timeout, **kwargs
        )

        logger.debug(f"KliraOTLPSpanExporter initialized with endpoint: {endpoint}")

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to Klira API using OTLP protobuf format.

        This method is called by BatchSpanProcessor with a batch of spans.
        All spans in the batch will be sent in a single HTTP request.

        Args:
            spans: Sequence of spans to export

        Returns:
            SpanExportResult indicating success or failure
        """
        if not spans:
            logger.debug("No spans to export")
            return SpanExportResult.SUCCESS

        logger.debug(f"Exporting batch of {len(spans)} spans to Klira API")

        try:
            # Delegate to underlying OTLP exporter
            result = self._otlp_exporter.export(spans)

            if result == SpanExportResult.SUCCESS:
                logger.debug(f"Successfully exported {len(spans)} spans to Klira API")
            else:
                logger.warning(f"Failed to export {len(spans)} spans: {result}")

            return result
        except Exception as e:
            logger.error(f"Error exporting spans to Klira API: {e}", exc_info=True)
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            True if flush succeeded, False otherwise
        """
        try:
            return self._otlp_exporter.force_flush(timeout_millis)
        except Exception as e:
            logger.error(f"Error force flushing spans: {e}", exc_info=True)
            return False

    def shutdown(self) -> None:
        """Shutdown the exporter and release resources."""
        try:
            self._otlp_exporter.shutdown()
            logger.debug("KliraOTLPSpanExporter shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down exporter: {e}", exc_info=True)


def create_klira_batch_processor(
    api_key: str,
    endpoint: Optional[str] = None,
    max_export_batch_size: int = 512,
    schedule_delay_millis: int = 3600000,
    max_queue_size: int = 2048,
    export_timeout_millis: int = 30000,
    **kwargs: Any,
) -> "BatchSpanProcessor":
    """Create a BatchSpanProcessor configured for unified trace batching.

    This is a convenience function that creates a KliraOTLPSpanExporter and
    wraps it in a BatchSpanProcessor with optimal batching parameters.

    By default, batch export is triggered by force_flush() when workflow completes
    (via UserMessageTraceContext.__exit__), not on schedule. This ensures zero
    latency impact and sends all spans in one API call when the workflow finishes.

    Args:
        api_key: Klira API key (required)
        endpoint: OTLP endpoint URL. Defaults to https://api.getklira.com/v1/traces
        max_export_batch_size: Maximum number of spans to batch (default: 512)
        schedule_delay_millis: Delay before sending batch in ms (default: 3600000 = 1 hour, effectively never)
        max_queue_size: Maximum queue size for buffered spans (default: 2048)
        export_timeout_millis: Timeout for export operation in ms (default: 30000)
        **kwargs: Additional arguments passed to KliraOTLPSpanExporter

    Returns:
        BatchSpanProcessor configured with KliraOTLPSpanExporter

    Example:
        >>> from klira.sdk.telemetry.unified_exporter import create_klira_batch_processor
        >>>
        >>> # Create processor with default batching parameters
        >>> processor = create_klira_batch_processor(api_key="klira_...")
        >>>
        >>> # Add to tracer provider
        >>> from opentelemetry import trace
        >>> provider = trace.get_tracer_provider()
        >>> provider.add_span_processor(processor)
    """
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # Create the exporter
    exporter = KliraOTLPSpanExporter(
        api_key=api_key,
        endpoint=endpoint,
        timeout=export_timeout_millis // 1000,  # Convert to seconds
        **kwargs,
    )

    # Wrap in BatchSpanProcessor with configured parameters
    processor = BatchSpanProcessor(
        span_exporter=exporter,
        max_export_batch_size=max_export_batch_size,
        schedule_delay_millis=schedule_delay_millis,
        max_queue_size=max_queue_size,
        export_timeout_millis=export_timeout_millis,
    )

    logger.info(
        f"Created unified trace batch processor: "
        f"batch_size={max_export_batch_size}, "
        f"delay={schedule_delay_millis}ms, "
        f"queue_size={max_queue_size}"
    )

    return processor
