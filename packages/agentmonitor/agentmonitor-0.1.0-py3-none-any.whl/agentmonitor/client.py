"""Synchronous client for AgentMonitor SDK.

This module provides the main AgentMonitor class for tracking agent events.
"""

import time
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager
from .config import AgentMonitorConfig
from .models import Event
from .batcher import BatchQueue
from .decorators import create_track_decorator
from .utils import setup_logger, safe_serialize, get_iso_timestamp, redact_sensitive_data
from .exceptions import ConfigError


class TrackedEvent:
    """Context manager for tracking events.

    This class is returned by track_event() and allows manual control
    over event attributes.
    """

    def __init__(self, monitor_instance, event_type: str, input_data: Optional[Dict] = None):
        """Initialize tracked event.

        Args:
            monitor_instance: AgentMonitor instance
            event_type: Type of event
            input_data: Initial input data
        """
        self.monitor = monitor_instance
        self.event_type = event_type
        self.input_data = input_data
        self.output_data = None
        self.metadata = {}
        self.cost_usd = None
        self.status = "success"
        self.error_message = None
        self.start_time = None
        self.start_timestamp = None

    def set_output(self, output_data: Any):
        """Set output data for the event.

        Args:
            output_data: Output data to track
        """
        self.output_data = safe_serialize(output_data)

    def set_metadata(self, **kwargs):
        """Set metadata fields.

        Args:
            **kwargs: Metadata key-value pairs
        """
        self.metadata.update(kwargs)

    def set_cost(self, cost_usd: float):
        """Set cost in USD.

        Args:
            cost_usd: Cost in US dollars
        """
        self.cost_usd = cost_usd

    def set_status(self, status: str):
        """Set event status.

        Args:
            status: Status string ("success" or "failure")
        """
        self.status = status

    def set_error(self, error_message: str):
        """Set error message and status.

        Args:
            error_message: Error message
        """
        self.status = "failure"
        self.error_message = error_message

    def __enter__(self):
        """Enter context manager."""
        self.start_time = time.time()
        self.start_timestamp = get_iso_timestamp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and log event."""
        # Calculate latency
        latency_ms = None
        if self.start_time:
            latency_ms = int((time.time() - self.start_time) * 1000)

        # Handle exception
        if exc_val:
            self.status = "failure"
            self.error_message = f"{type(exc_val).__name__}: {str(exc_val)}"

        # Apply redaction
        input_data = self.input_data
        output_data = self.output_data
        if self.monitor.config.redact_keys:
            if input_data:
                input_data = redact_sensitive_data(input_data, self.monitor.config.redact_keys)
            if output_data:
                output_data = redact_sensitive_data(output_data, self.monitor.config.redact_keys)

        # Create event
        event = Event.create(
            agent_id=self.monitor.config.agent_id,
            event_type=self.event_type,
            timestamp=self.start_timestamp,
            input_data=input_data,
            output_data=output_data,
            metadata=self.metadata if self.metadata else None,
            cost_usd=self.cost_usd,
            latency_ms=latency_ms,
            status=self.status,
            error_message=self.error_message
        )

        # Log event
        self.monitor._add_event(event)

        # Don't suppress exceptions
        return False


class AgentMonitor:
    """Main client for tracking agent events.

    This class provides multiple ways to track events:
    1. Decorator: @monitor.track()
    2. Context manager: with monitor.track_event(...)
    3. Manual: monitor.log_event(...)

    Example:
        >>> monitor = AgentMonitor(
        ...     api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
        ...     agent_id="my_agent",
        ...     api_url="http://localhost:3002/api/v1"
        ... )
        >>> @monitor.track()
        ... def my_function(x):
        ...     return x * 2
        >>> result = my_function(5)
        >>> monitor.flush()
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        api_url: str = "https://api.agentmonitor.io/api/v1",
        batch_size: int = 10,
        flush_interval: float = 5.0,
        retry_attempts: int = 3,
        timeout: int = 30,
        debug: bool = False,
        enabled: bool = True,
        redact_keys: Optional[List[str]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Initialize AgentMonitor client.

        Args:
            api_key: API key for authentication (minimum 32 characters)
            agent_id: Identifier for the agent being monitored
            api_url: Base URL for the API
            batch_size: Number of events to batch before flushing
            flush_interval: Seconds between automatic flushes
            retry_attempts: Maximum number of retry attempts
            timeout: Request timeout in seconds
            debug: Enable debug logging
            enabled: Enable tracking (set False to disable)
            redact_keys: List of keys to redact from event data
            on_error: Optional callback for error handling

        Raises:
            ConfigError: If configuration is invalid
        """
        # Create config
        self.config = AgentMonitorConfig(
            api_key=api_key,
            agent_id=agent_id,
            api_url=api_url,
            batch_size=batch_size,
            flush_interval=flush_interval,
            retry_attempts=retry_attempts,
            timeout=timeout,
            debug=debug,
            enabled=enabled,
            redact_keys=redact_keys or []
        )

        # Setup logger
        self.logger = setup_logger(__name__, debug=debug)

        # Initialize batch queue
        self._batch_queue = BatchQueue(self.config, on_error=on_error)
        self._batch_queue.start()

        self.logger.info(f"AgentMonitor initialized for agent '{agent_id}'")

    def track(
        self,
        event_type: str = "function_call",
        capture_input: bool = True,
        capture_output: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Decorator to automatically track function execution.

        Args:
            event_type: Type of event (default: "function_call")
            capture_input: Whether to capture function inputs
            capture_output: Whether to capture function outputs
            metadata: Additional metadata to attach to the event

        Returns:
            Decorator function

        Example:
            >>> @monitor.track(event_type="query")
            ... def ask_question(question: str) -> str:
            ...     return f"Answer to: {question}"
        """
        decorator_factory = create_track_decorator(self)
        return decorator_factory(
            event_type=event_type,
            capture_input=capture_input,
            capture_output=capture_output,
            metadata=metadata
        )

    def track_event(
        self,
        event_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> TrackedEvent:
        """Create a context manager for tracking an event.

        Args:
            event_type: Type of event
            input_data: Initial input data

        Returns:
            TrackedEvent context manager

        Example:
            >>> with monitor.track_event("action") as event:
            ...     result = perform_action()
            ...     event.set_output({"result": result})
            ...     event.set_metadata(model="gpt-4")
        """
        return TrackedEvent(self, event_type, input_data)

    def log_event(
        self,
        event_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cost_usd: Optional[float] = None,
        latency_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        """Manually log an event.

        Args:
            event_type: Type of event
            input_data: Input data
            output_data: Output data
            metadata: Additional metadata
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            status: Event status ("success" or "failure")
            error_message: Error message if status is "failure"
            timestamp: Override timestamp (ISO 8601 format)

        Example:
            >>> monitor.log_event(
            ...     event_type="decision",
            ...     input_data={"query": "test"},
            ...     output_data={"answer": "response"},
            ...     metadata={"model": "gpt-4"}
            ... )
        """
        # Apply redaction
        if self.config.redact_keys:
            if input_data:
                input_data = redact_sensitive_data(input_data, self.config.redact_keys)
            if output_data:
                output_data = redact_sensitive_data(output_data, self.config.redact_keys)

        # Create event
        event = Event.create(
            agent_id=self.config.agent_id,
            event_type=event_type,
            timestamp=timestamp,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message
        )

        # Add to queue
        self._add_event(event)

    def _add_event(self, event: Event):
        """Add event to batch queue (internal method).

        Args:
            event: Event to add
        """
        self._batch_queue.add_event(event)

    def flush(self):
        """Flush all pending events immediately (blocking).

        This method will block until all events are sent to the API.
        Call this before your application exits to ensure all events are sent.

        Example:
            >>> monitor.flush()
        """
        self.logger.debug("Flushing pending events")
        self._batch_queue.flush()

    def close(self):
        """Close the monitor and cleanup resources.

        This will stop the background thread and flush any pending events.
        After calling close(), the monitor should not be used.

        Example:
            >>> monitor.close()
        """
        self.logger.info("Closing AgentMonitor")
        self._batch_queue.stop()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup

    def __repr__(self) -> str:
        """String representation."""
        return f"AgentMonitor(agent_id='{self.config.agent_id}', enabled={self.config.enabled})"
