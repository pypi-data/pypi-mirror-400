"""Asynchronous client for AgentMonitor SDK.

This module provides the AsyncAgentMonitor class for async/await tracking.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Callable
import aiohttp
from .config import AgentMonitorConfig
from .models import Event
from .utils import setup_logger, safe_serialize, get_iso_timestamp, redact_sensitive_data, format_error_message
from .exceptions import ConfigError, APIError, AuthenticationError, NetworkError


class AsyncTrackedEvent:
    """Async context manager for tracking events."""

    def __init__(self, monitor_instance, event_type: str, input_data: Optional[Dict] = None):
        """Initialize tracked event.

        Args:
            monitor_instance: AsyncAgentMonitor instance
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
        """Set output data for the event."""
        self.output_data = safe_serialize(output_data)

    def set_metadata(self, **kwargs):
        """Set metadata fields."""
        self.metadata.update(kwargs)

    def set_cost(self, cost_usd: float):
        """Set cost in USD."""
        self.cost_usd = cost_usd

    def set_status(self, status: str):
        """Set event status."""
        self.status = status

    def set_error(self, error_message: str):
        """Set error message and status."""
        self.status = "failure"
        self.error_message = error_message

    async def __aenter__(self):
        """Enter async context manager."""
        self.start_time = time.time()
        self.start_timestamp = get_iso_timestamp()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and log event."""
        # Calculate latency
        latency_ms = None
        if self.start_time:
            latency_ms = int((time.time() - self.start_time) * 1000)

        # Handle exception
        if exc_val:
            self.status = "failure"
            self.error_message = format_error_message(exc_val)

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
        await self.monitor._add_event_async(event)

        # Don't suppress exceptions
        return False


class AsyncAgentMonitor:
    """Asynchronous client for tracking agent events.

    This class provides async/await support for event tracking.

    Example:
        >>> monitor = AsyncAgentMonitor(
        ...     api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
        ...     agent_id="my_agent",
        ...     api_url="http://localhost:3002/api/v1"
        ... )
        >>> @monitor.track()
        ... async def my_async_function(x):
        ...     await asyncio.sleep(0.1)
        ...     return x * 2
        >>> result = await my_async_function(5)
        >>> await monitor.flush()
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
        """Initialize AsyncAgentMonitor client.

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

        # Event queue
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._flush_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._on_error = on_error
        self._started = False

        self.logger.info(f"AsyncAgentMonitor initialized for agent '{agent_id}'")

    async def start(self):
        """Start the background flushing task."""
        if self._started:
            return

        # Create aiohttp session
        self._session = aiohttp.ClientSession()

        # Start background flush task
        self._flush_task = asyncio.create_task(self._flush_loop())
        self._started = True
        self.logger.debug("AsyncAgentMonitor background task started")

    async def stop(self):
        """Stop the background task and flush remaining events."""
        if not self._started:
            return

        self.logger.debug("Stopping AsyncAgentMonitor background task")

        # Cancel flush task
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Flush remaining events
        await self.flush()

        # Close session
        if self._session:
            await self._session.close()

        self._started = False

    def track(
        self,
        event_type: str = "function_call",
        capture_input: bool = True,
        capture_output: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Decorator to automatically track async function execution.

        Args:
            event_type: Type of event (default: "function_call")
            capture_input: Whether to capture function inputs
            capture_output: Whether to capture function outputs
            metadata: Additional metadata to attach to the event

        Returns:
            Decorator function

        Example:
            >>> @monitor.track(event_type="query")
            ... async def ask_question(question: str) -> str:
            ...     await asyncio.sleep(0.1)
            ...     return f"Answer to: {question}"
        """
        def decorator(func):
            import functools
            import inspect

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Ensure monitor is started
                if not self._started:
                    await self.start()

                # Start timing
                start_time = time.time()
                start_timestamp = get_iso_timestamp()

                # Capture input
                input_data = None
                if capture_input:
                    input_data = self._capture_function_input(func, args, kwargs)

                # Apply redaction
                if self.config.redact_keys and input_data:
                    input_data = redact_sensitive_data(input_data, self.config.redact_keys)

                # Execute function
                error = None
                output_data = None
                status = "success"
                error_message = None

                try:
                    output = await func(*args, **kwargs)

                    # Capture output
                    if capture_output:
                        output_data = safe_serialize(output)

                    # Apply redaction
                    if self.config.redact_keys and output_data:
                        output_data = redact_sensitive_data(output_data, self.config.redact_keys)

                except Exception as e:
                    error = e
                    status = "failure"
                    error_message = format_error_message(e)
                    self.logger.debug(f"Function {func.__name__} raised error: {error_message}")

                finally:
                    # Calculate latency
                    end_time = time.time()
                    latency_ms = int((end_time - start_time) * 1000)

                    # Build metadata
                    event_metadata = {
                        "function_name": func.__name__,
                        "module": func.__module__,
                    }
                    if metadata:
                        event_metadata.update(metadata)

                    # Create and log event
                    event = Event.create(
                        agent_id=self.config.agent_id,
                        event_type=event_type,
                        timestamp=start_timestamp,
                        input_data=input_data,
                        output_data=output_data,
                        metadata=event_metadata,
                        latency_ms=latency_ms,
                        status=status,
                        error_message=error_message
                    )

                    # Add event to queue
                    await self._add_event_async(event)

                    # Re-raise error if one occurred
                    if error:
                        raise error

                    return output

            return wrapper

        return decorator

    def _capture_function_input(self, func, args, kwargs):
        """Capture function input arguments."""
        import inspect
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            input_dict = {}
            for param_name, param_value in bound_args.arguments.items():
                input_dict[param_name] = safe_serialize(param_value)

            return input_dict

        except Exception:
            return {
                "args": safe_serialize(args) if args else None,
                "kwargs": safe_serialize(kwargs) if kwargs else None
            }

    def track_event(
        self,
        event_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> AsyncTrackedEvent:
        """Create an async context manager for tracking an event.

        Args:
            event_type: Type of event
            input_data: Initial input data

        Returns:
            AsyncTrackedEvent context manager

        Example:
            >>> async with monitor.track_event("action") as event:
            ...     result = await perform_action()
            ...     event.set_output({"result": result})
            ...     event.set_metadata(model="gpt-4")
        """
        return AsyncTrackedEvent(self, event_type, input_data)

    async def log_event(
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
        """Manually log an event (async).

        Args:
            event_type: Type of event
            input_data: Input data
            output_data: Output data
            metadata: Additional metadata
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            status: Event status ("success" or "error")
            error_message: Error message if status is "error"
            timestamp: Override timestamp (ISO 8601 format)
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
        await self._add_event_async(event)

    async def _add_event_async(self, event: Event):
        """Add event to async queue (internal method)."""
        if not self.config.enabled:
            self.logger.debug("Tracking disabled, skipping event")
            return

        # Ensure monitor is started
        if not self._started:
            await self.start()

        await self._event_queue.put(event)
        self.logger.debug(f"Event added to async queue: {event.event_type}")

    async def flush(self):
        """Flush all pending events immediately (async)."""
        if self._event_queue.empty():
            self.logger.debug("Async queue is empty, nothing to flush")
            return

        events = []
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                events.append(event)
            except asyncio.QueueEmpty:
                break

        if events:
            self.logger.debug(f"Flushing {len(events)} events (async)")
            await self._send_batch_async(events)

    async def _flush_loop(self):
        """Background task loop for periodic flushing."""
        self.logger.debug("Async flush loop started")

        try:
            while True:
                # Wait for flush interval
                await asyncio.sleep(self.config.flush_interval)

                # Check if we have events to flush
                if not self._event_queue.empty():
                    events = []
                    batch_size = self.config.batch_size

                    while len(events) < batch_size and not self._event_queue.empty():
                        try:
                            event = self._event_queue.get_nowait()
                            events.append(event)
                        except asyncio.QueueEmpty:
                            break

                    if events:
                        self.logger.debug(f"Periodic flush (async): {len(events)} events")
                        await self._send_batch_async(events)

        except asyncio.CancelledError:
            self.logger.debug("Async flush loop cancelled")
            raise

    async def _send_batch_async(self, events: List[Event]):
        """Send a batch of events to the API with retry logic (async)."""
        if not events:
            return

        # Ensure session exists
        if not self._session:
            self._session = aiohttp.ClientSession()

        # Convert events to API format
        payload = {
            "events": [event.to_dict() for event in events]
        }

        # Retry with exponential backoff
        retry_count = 0
        max_retries = self.config.retry_attempts
        backoff_seconds = 1

        while retry_count <= max_retries:
            try:
                async with self._session.post(
                    self.config.batch_url,
                    json=payload,
                    headers=self.config.headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status in (200, 201):
                        self.logger.info(f"Successfully sent batch of {len(events)} events (async)")
                        return
                    elif response.status in (401, 403):
                        text = await response.text()
                        error = AuthenticationError(
                            f"Authentication failed: {text}",
                            status_code=response.status
                        )
                        self.logger.error(f"Authentication error (async): {error}")
                        if self._on_error:
                            self._on_error(error)
                        return  # Don't retry auth errors
                    else:
                        text = await response.text()
                        error = APIError(
                            f"API request failed: {text}",
                            status_code=response.status,
                            response_body=text
                        )
                        self.logger.warning(f"API error (async, attempt {retry_count + 1}/{max_retries + 1}): {error}")

                        if retry_count < max_retries:
                            retry_count += 1
                            await asyncio.sleep(backoff_seconds)
                            backoff_seconds *= 2
                        else:
                            self.logger.error(f"Failed to send batch (async) after {max_retries + 1} attempts")
                            if self._on_error:
                                self._on_error(error)
                            return

            except asyncio.TimeoutError as e:
                error = NetworkError(f"Request timeout: {e}")
                self.logger.warning(f"Timeout error (async, attempt {retry_count + 1}/{max_retries + 1}): {error}")

                if retry_count < max_retries:
                    retry_count += 1
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    self.logger.error(f"Failed to send batch (async) after {max_retries + 1} attempts (timeout)")
                    if self._on_error:
                        self._on_error(error)
                    return

            except aiohttp.ClientError as e:
                error = NetworkError(f"Network error: {e}")
                self.logger.warning(f"Network error (async, attempt {retry_count + 1}/{max_retries + 1}): {error}")

                if retry_count < max_retries:
                    retry_count += 1
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    self.logger.error(f"Failed to send batch (async) after {max_retries + 1} attempts (network error)")
                    if self._on_error:
                        self._on_error(error)
                    return

            except Exception as e:
                error = APIError(f"Unexpected error: {e}")
                self.logger.error(f"Unexpected error sending batch (async): {error}")
                if self._on_error:
                    self._on_error(error)
                return  # Don't retry unexpected errors

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    def __repr__(self) -> str:
        """String representation."""
        return f"AsyncAgentMonitor(agent_id='{self.config.agent_id}', enabled={self.config.enabled})"
