"""Built-in Analytics Processors for Klira SDK.

This module provides ready-to-use analytics processors for common use cases:
- Console logging processor
- File output processor
- Metrics aggregation processor
- Performance monitoring processor

Note: Analytics data is sent to Klira platform via OpenTelemetry (OTLP),
not through custom processors. The processors here are for local development,
debugging, and custom analytics pipelines.
"""

import json
import logging
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Callable
import threading
import statistics

from . import AnalyticsProcessor, AnalyticsEvent, Metric, EventType, MetricType

logger = logging.getLogger(__name__)


class ConsoleAnalyticsProcessor(AnalyticsProcessor):
    """Analytics processor that outputs to console/logs."""

    def __init__(
        self,
        log_events: bool = True,
        log_metrics: bool = True,
        log_level: int = logging.INFO,
        event_format: str = "simple",
        metric_format: str = "simple",
    ):
        """Initialize console processor.

        Args:
            log_events: Whether to log events
            log_metrics: Whether to log metrics
            log_level: Logging level to use
            event_format: Format for events ("simple", "detailed", "json")
            metric_format: Format for metrics ("simple", "detailed", "json")
        """
        self.log_events = log_events
        self.log_metrics = log_metrics
        self.log_level = log_level
        self.event_format = event_format
        self.metric_format = metric_format

        # Create dedicated logger
        self.analytics_logger = logging.getLogger("klira.analytics.console")
        if not self.analytics_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.analytics_logger.addHandler(handler)
            self.analytics_logger.setLevel(log_level)

    @property
    def name(self) -> str:
        return "console"

    def process_event(self, event: AnalyticsEvent) -> None:
        """Process a single event."""
        if not self.log_events:
            return

        if self.event_format == "json":
            message = json.dumps(event.to_dict(), indent=2)
        elif self.event_format == "detailed":
            message = (
                f"Event: {event.event_type} | "
                f"ID: {event.event_id} | "
                f"Session: {event.session_id} | "
                f"Data: {event.data} | "
                f"Context: {event.context}"
            )
        else:  # simple
            message = f"Event: {event.event_type}"
            if event.data:
                message += f" | Data: {event.data}"

        self.analytics_logger.log(self.log_level, message)

    def process_metric(self, metric: Metric) -> None:
        """Process a single metric."""
        if not self.log_metrics:
            return

        if self.metric_format == "json":
            message = json.dumps(metric.to_dict(), indent=2)
        elif self.metric_format == "detailed":
            message = (
                f"Metric: {metric.name} = {metric.value} | "
                f"Type: {metric.metric_type.value} | "
                f"Unit: {metric.unit} | "
                f"Tags: {metric.tags}"
            )
        else:  # simple
            unit_str = f" {metric.unit}" if metric.unit else ""
            message = f"Metric: {metric.name} = {metric.value}{unit_str}"

        self.analytics_logger.log(self.log_level, message)

    def flush(self) -> None:
        """Flush any pending data."""
        # Console output is immediate, nothing to flush
        pass

    def close(self) -> None:
        """Close and cleanup resources."""
        # Nothing to close for console output
        pass


class FileAnalyticsProcessor(AnalyticsProcessor):
    """Analytics processor that writes to files."""

    def __init__(
        self,
        output_dir: str = "./klira_analytics",
        events_file: str = "events.jsonl",
        metrics_file: str = "metrics.jsonl",
        buffer_size: int = 1000,
        auto_flush_interval: int = 60,
        create_daily_files: bool = False,
    ):
        """Initialize file processor.

        Args:
            output_dir: Directory to write files
            events_file: Name of events file
            metrics_file: Name of metrics file
            buffer_size: Number of items to buffer before writing
            auto_flush_interval: Seconds between auto-flushes
            create_daily_files: Whether to create new files daily
        """
        self.output_dir = Path(output_dir)
        self.events_file = events_file
        self.metrics_file = metrics_file
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        self.create_daily_files = create_daily_files

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Buffers
        self.events_buffer: List[AnalyticsEvent] = []
        self.metrics_buffer: List[Metric] = []

        # Thread safety
        self._lock = threading.RLock()

        # Auto-flush
        self._last_flush = time.time()

        logger.info(f"File analytics processor initialized: {self.output_dir}")

    @property
    def name(self) -> str:
        return "file"

    def _get_file_path(self, base_filename: str) -> Path:
        """Get file path, potentially with date suffix."""
        if self.create_daily_files:
            date_str = datetime.now().strftime("%Y-%m-%d")
            name, ext = os.path.splitext(base_filename)
            filename = f"{name}_{date_str}{ext}"
        else:
            filename = base_filename

        return self.output_dir / filename

    def process_event(self, event: AnalyticsEvent) -> None:
        """Process a single event."""
        with self._lock:
            self.events_buffer.append(event)

            if len(self.events_buffer) >= self.buffer_size:
                self._flush_events()

    def process_metric(self, metric: Metric) -> None:
        """Process a single metric."""
        with self._lock:
            self.metrics_buffer.append(metric)

            if len(self.metrics_buffer) >= self.buffer_size:
                self._flush_metrics()

    def process_batch(
        self, events: List[AnalyticsEvent], metrics: List[Metric]
    ) -> None:
        """Process a batch of events and metrics."""
        with self._lock:
            self.events_buffer.extend(events)
            self.metrics_buffer.extend(metrics)

            # Check if we should flush
            if (
                len(self.events_buffer) >= self.buffer_size
                or len(self.metrics_buffer) >= self.buffer_size
                or time.time() - self._last_flush > self.auto_flush_interval
            ):
                self.flush()

    def _flush_events(self) -> None:
        """Flush events buffer to file."""
        if not self.events_buffer:
            return

        events_path = self._get_file_path(self.events_file)

        try:
            with open(events_path, "a", encoding="utf-8") as f:
                for event in self.events_buffer:
                    f.write(json.dumps(event.to_dict()) + "\n")

            logger.debug(f"Flushed {len(self.events_buffer)} events to {events_path}")
            self.events_buffer.clear()

        except Exception as e:
            logger.error(f"Error writing events to file {events_path}: {e}")

    def _flush_metrics(self) -> None:
        """Flush metrics buffer to file."""
        if not self.metrics_buffer:
            return

        metrics_path = self._get_file_path(self.metrics_file)

        try:
            with open(metrics_path, "a", encoding="utf-8") as f:
                for metric in self.metrics_buffer:
                    f.write(json.dumps(metric.to_dict()) + "\n")

            logger.debug(
                f"Flushed {len(self.metrics_buffer)} metrics to {metrics_path}"
            )
            self.metrics_buffer.clear()

        except Exception as e:
            logger.error(f"Error writing metrics to file {metrics_path}: {e}")

    def flush(self) -> None:
        """Flush all pending data."""
        with self._lock:
            self._flush_events()
            self._flush_metrics()
            self._last_flush = time.time()

    def close(self) -> None:
        """Close and cleanup resources."""
        self.flush()
        logger.info("File analytics processor closed")


class MetricsAggregationProcessor(AnalyticsProcessor):
    """Processor that aggregates metrics and generates summary statistics."""

    def __init__(
        self,
        aggregation_window_seconds: int = 300,  # 5 minutes
        keep_raw_data: bool = False,
        export_interval_seconds: int = 60,
    ):
        """Initialize metrics aggregation processor.

        Args:
            aggregation_window_seconds: Time window for aggregation
            keep_raw_data: Whether to keep raw metric data
            export_interval_seconds: How often to export aggregated data
        """
        self.aggregation_window_seconds = aggregation_window_seconds
        self.keep_raw_data = keep_raw_data
        self.export_interval_seconds = export_interval_seconds

        # Storage for raw and aggregated data
        self.raw_metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}

        # Time-based windows
        self.metric_windows: Dict[str, deque[Metric]] = defaultdict(lambda: deque())

        # Thread safety
        self._lock = threading.RLock()

        # Last export time
        self._last_export = time.time()

    @property
    def name(self) -> str:
        return "metrics_aggregation"

    def process_event(self, event: AnalyticsEvent) -> None:
        """Process events (ignored by this processor)."""
        pass

    def process_metric(self, metric: Metric) -> None:
        """Process a single metric."""
        with self._lock:
            metric_key = f"{metric.name}#{metric.metric_type.value}"

            # Add to raw data if keeping
            if self.keep_raw_data:
                self.raw_metrics[metric_key].append(metric)

            # Add to time window
            self.metric_windows[metric_key].append(metric)

            # Clean old data from window
            self._clean_window(metric_key)

            # Update aggregation
            self._update_aggregation(metric_key)

            # Export if needed
            if time.time() - self._last_export > self.export_interval_seconds:
                self._export_aggregations()

    def _clean_window(self, metric_key: str) -> None:
        """Remove old metrics from the time window."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            seconds=self.aggregation_window_seconds
        )
        window = self.metric_windows[metric_key]

        while window and window[0].timestamp < cutoff_time:
            window.popleft()

    def _update_aggregation(self, metric_key: str) -> None:
        """Update aggregated statistics for a metric."""
        window = self.metric_windows[metric_key]
        if not window:
            return

        values = [m.value for m in window]

        aggregation = {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "last_value": values[-1],
            "window_start": window[0].timestamp.isoformat(),
            "window_end": window[-1].timestamp.isoformat(),
        }

        # Add more statistics if we have enough data
        if len(values) >= 2:
            aggregation["stdev"] = statistics.stdev(values)

        if len(values) >= 3:
            aggregation["median"] = statistics.median(values)

        # Add percentiles for larger datasets
        if len(values) >= 10:
            sorted_values = sorted(values)
            aggregation["p50"] = statistics.median(sorted_values)
            aggregation["p90"] = sorted_values[int(0.9 * len(sorted_values))]
            aggregation["p95"] = sorted_values[int(0.95 * len(sorted_values))]
            aggregation["p99"] = sorted_values[int(0.99 * len(sorted_values))]

        self.aggregated_metrics[metric_key] = aggregation

    def _export_aggregations(self) -> None:
        """Export aggregated metrics (override this method to customize export)."""
        # Default implementation just logs the aggregations
        for metric_key, aggregation in self.aggregated_metrics.items():
            logger.info(f"Aggregated metric {metric_key}: {aggregation}")

        self._last_export = time.time()

    def get_aggregations(self) -> Dict[str, Dict[str, Any]]:
        """Get current aggregated metrics."""
        with self._lock:
            return self.aggregated_metrics.copy()

    def get_raw_metrics(self) -> Dict[str, List[Metric]]:
        """Get raw metrics (if kept)."""
        if not self.keep_raw_data:
            return {}

        with self._lock:
            return {k: list(v) for k, v in self.raw_metrics.items()}

    def flush(self) -> None:
        """Flush any pending data."""
        self._export_aggregations()

    def close(self) -> None:
        """Close and cleanup resources."""
        self.flush()
        logger.info("Metrics aggregation processor closed")


class PerformanceMonitoringProcessor(AnalyticsProcessor):
    """Processor that monitors performance and generates alerts."""

    def __init__(
        self,
        latency_threshold_ms: float = 5000,
        error_rate_threshold: float = 0.1,
        memory_threshold_mb: float = 1000,
        monitoring_window_seconds: int = 300,
    ):
        """Initialize performance monitoring processor.

        Args:
            latency_threshold_ms: Latency threshold for alerts
            error_rate_threshold: Error rate threshold (0.0-1.0)
            memory_threshold_mb: Memory usage threshold
            monitoring_window_seconds: Window for rate calculations
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.error_rate_threshold = error_rate_threshold
        self.memory_threshold_mb = memory_threshold_mb
        self.monitoring_window_seconds = monitoring_window_seconds

        # Performance tracking
        self.request_latencies: deque[tuple[datetime, float]] = deque()
        self.error_events: deque[datetime] = deque()
        self.total_events: deque[datetime] = deque()
        self.memory_usage: deque[tuple[datetime, float]] = deque()

        # Thread safety
        self._lock = threading.RLock()

        # Alert callbacks
        self._alert_callbacks: List[Callable[[Dict[str, Any]], None]] = []

    @property
    def name(self) -> str:
        return "performance_monitoring"

    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback for performance alerts."""
        self._alert_callbacks.append(callback)

    def process_event(self, event: AnalyticsEvent) -> None:
        """Process a single event."""
        with self._lock:
            current_time = datetime.now(timezone.utc)

            # Track all events
            self.total_events.append(current_time)

            # Track error events
            if isinstance(event.event_type, EventType) and (
                event.event_type.value.endswith(".failed")
                or event.event_type
                in [EventType.ERROR_OCCURRED, EventType.EXCEPTION_RAISED]
            ):
                self.error_events.append(current_time)

            # Track latency if available
            if event.duration_ms is not None:
                self.request_latencies.append((current_time, event.duration_ms))

                # Check latency threshold
                if event.duration_ms > self.latency_threshold_ms:
                    self._trigger_alert(
                        "high_latency",
                        {
                            "event": event.event_type,
                            "latency_ms": event.duration_ms,
                            "threshold_ms": self.latency_threshold_ms,
                        },
                    )

            # Track memory usage if available
            if event.memory_usage_mb is not None:
                self.memory_usage.append((current_time, event.memory_usage_mb))

                # Check memory threshold
                if event.memory_usage_mb > self.memory_threshold_mb:
                    self._trigger_alert(
                        "high_memory",
                        {
                            "memory_mb": event.memory_usage_mb,
                            "threshold_mb": self.memory_threshold_mb,
                        },
                    )

            # Clean old data and check error rate
            self._clean_old_data(current_time)
            self._check_error_rate()

    def process_metric(self, metric: Metric) -> None:
        """Process a single metric."""
        # Monitor specific performance metrics
        if metric.name == "latency" and metric.metric_type == MetricType.TIMER:
            if metric.value > self.latency_threshold_ms:
                self._trigger_alert(
                    "metric_high_latency",
                    {
                        "metric_name": metric.name,
                        "value": metric.value,
                        "threshold": self.latency_threshold_ms,
                    },
                )

        elif metric.name == "memory_usage" and metric.metric_type == MetricType.GAUGE:
            if metric.value > self.memory_threshold_mb:
                self._trigger_alert(
                    "metric_high_memory",
                    {
                        "metric_name": metric.name,
                        "value": metric.value,
                        "threshold": self.memory_threshold_mb,
                    },
                )

    def _clean_old_data(self, current_time: datetime) -> None:
        """Remove data outside the monitoring window."""
        cutoff_time = current_time - timedelta(seconds=self.monitoring_window_seconds)

        # Clean latencies
        while self.request_latencies and self.request_latencies[0][0] < cutoff_time:
            self.request_latencies.popleft()

        # Clean error events
        while self.error_events and self.error_events[0] < cutoff_time:
            self.error_events.popleft()

        # Clean total events
        while self.total_events and self.total_events[0] < cutoff_time:
            self.total_events.popleft()

        # Clean memory usage
        while self.memory_usage and self.memory_usage[0][0] < cutoff_time:
            self.memory_usage.popleft()

    def _check_error_rate(self) -> None:
        """Check if error rate exceeds threshold."""
        if len(self.total_events) == 0:
            return

        error_rate = len(self.error_events) / len(self.total_events)

        if error_rate > self.error_rate_threshold:
            self._trigger_alert(
                "high_error_rate",
                {
                    "error_rate": error_rate,
                    "threshold": self.error_rate_threshold,
                    "error_count": len(self.error_events),
                    "total_count": len(self.total_events),
                },
            )

    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger a performance alert."""
        alert = {
            "type": alert_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

        logger.warning(f"Performance alert: {alert_type} - {data}")

        # Call alert callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        with self._lock:
            stats = {
                "total_events": len(self.total_events),
                "error_events": len(self.error_events),
                "error_rate": len(self.error_events) / len(self.total_events)
                if self.total_events
                else 0,
            }

            if self.request_latencies:
                latencies = [lat for _, lat in self.request_latencies]
                stats.update(
                    {
                        "avg_latency_ms": statistics.mean(latencies),
                        "min_latency_ms": min(latencies),
                        "max_latency_ms": max(latencies),
                        "latency_count": len(latencies),
                    }
                )

                if len(latencies) >= 2:
                    stats["latency_stdev_ms"] = statistics.stdev(latencies)

            if self.memory_usage:
                memory_values = [mem for _, mem in self.memory_usage]
                stats.update(
                    {
                        "avg_memory_mb": statistics.mean(memory_values),
                        "min_memory_mb": min(memory_values),
                        "max_memory_mb": max(memory_values),
                        "current_memory_mb": memory_values[-1],
                    }
                )

            return stats

    def flush(self) -> None:
        """Flush any pending data."""
        pass

    def close(self) -> None:
        """Close and cleanup resources."""
        logger.info("Performance monitoring processor closed")


# Convenience function to create common processor configurations
def create_standard_processors(
    output_dir: str = "./klira_analytics",
) -> List[AnalyticsProcessor]:
    """Create a standard set of analytics processors.

    Note: KliraHubProcessor was removed as of v0.1.x. Analytics data is now
    sent exclusively via OpenTelemetry to /v1/traces, /v1/metrics, etc.

    Args:
        output_dir: Directory for file output

    Returns:
        List of configured processors (Console, File, Metrics, Performance)
    """
    return [
        ConsoleAnalyticsProcessor(event_format="simple", metric_format="simple"),
        FileAnalyticsProcessor(output_dir=output_dir),
        MetricsAggregationProcessor(),
        PerformanceMonitoringProcessor(),
    ]
