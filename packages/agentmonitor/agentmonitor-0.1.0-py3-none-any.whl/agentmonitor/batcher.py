"""Event batching and background flushing for AgentMonitor SDK.

This module handles automatic batching of events and background flushing
to the API using a separate thread.
"""

import queue
import threading
import time
import requests
from typing import List, Optional, Callable
from .models import Event
from .config import AgentMonitorConfig
from .exceptions import APIError, AuthenticationError, NetworkError
from .utils import setup_logger


class BatchQueue:
    """Thread-safe queue for batching and sending events.

    This class manages a background thread that automatically flushes events
    to the API when the batch size is reached or after a time interval.

    Attributes:
        config: AgentMonitor configuration
        on_error: Optional callback for error handling
    """

    def __init__(
        self,
        config: AgentMonitorConfig,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Initialize the batch queue.

        Args:
            config: AgentMonitor configuration
            on_error: Optional callback function for error handling
        """
        self.config = config
        self.on_error = on_error
        self.logger = setup_logger(__name__, debug=config.debug)

        # Thread-safe queue
        self._queue: queue.Queue = queue.Queue()

        # Background thread
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._started = False
        self._lock = threading.Lock()

    def start(self):
        """Start the background flushing thread."""
        with self._lock:
            if self._started:
                return

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._flush_loop, daemon=True)
            self._thread.start()
            self._started = True
            self.logger.debug("BatchQueue background thread started")

    def stop(self):
        """Stop the background thread and flush remaining events."""
        with self._lock:
            if not self._started:
                return

            self.logger.debug("Stopping BatchQueue background thread")
            self._stop_event.set()

            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5.0)

            self._started = False

        # Flush any remaining events
        self.flush()

    def add_event(self, event: Event):
        """Add an event to the queue.

        Args:
            event: Event to add
        """
        if not self.config.enabled:
            self.logger.debug("Tracking disabled, skipping event")
            return

        try:
            self._queue.put_nowait(event)
            self.logger.debug(f"Event added to queue: {event.event_type}")

            # Check if we should flush immediately
            if self._queue.qsize() >= self.config.batch_size:
                self.logger.debug("Batch size reached, triggering immediate flush")
                # Signal the thread to wake up and flush
                self._wake_up_thread()

        except queue.Full:
            self.logger.warning("Event queue is full, dropping event")
            if self.on_error:
                self.on_error(Exception("Event queue is full"))

    def _wake_up_thread(self):
        """Wake up the background thread for immediate flush."""
        # This is handled by the queue size check in _flush_loop
        pass

    def flush(self):
        """Flush all pending events immediately (blocking)."""
        if self._queue.empty():
            self.logger.debug("Queue is empty, nothing to flush")
            return

        events = []
        while not self._queue.empty():
            try:
                event = self._queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break

        if events:
            self.logger.debug(f"Flushing {len(events)} events")
            self._send_batch(events)

    def _flush_loop(self):
        """Background thread loop for periodic flushing."""
        self.logger.debug("Flush loop started")

        while not self._stop_event.is_set():
            # Wait for flush interval or until stopped
            if self._stop_event.wait(timeout=self.config.flush_interval):
                break  # Stop event was set

            # Check if we have events to flush
            if not self._queue.empty():
                # Collect events up to batch size
                events = []
                batch_size = self.config.batch_size

                while len(events) < batch_size and not self._queue.empty():
                    try:
                        event = self._queue.get_nowait()
                        events.append(event)
                    except queue.Empty:
                        break

                if events:
                    self.logger.debug(f"Periodic flush: {len(events)} events")
                    self._send_batch(events)

        self.logger.debug("Flush loop stopped")

    def _send_batch(self, events: List[Event]):
        """Send a batch of events to the API with retry logic.

        Args:
            events: List of events to send
        """
        if not events:
            return

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
                response = requests.post(
                    self.config.batch_url,
                    json=payload,
                    headers=self.config.headers,
                    timeout=self.config.timeout
                )

                if response.status_code == 200 or response.status_code == 201:
                    self.logger.info(f"Successfully sent batch of {len(events)} events")
                    return
                elif response.status_code == 401 or response.status_code == 403:
                    error = AuthenticationError(
                        f"Authentication failed: {response.text}",
                        status_code=response.status_code
                    )
                    self.logger.error(f"Authentication error: {error}")
                    if self.on_error:
                        self.on_error(error)
                    return  # Don't retry auth errors
                else:
                    error = APIError(
                        f"API request failed: {response.text}",
                        status_code=response.status_code,
                        response_body=response.text
                    )
                    self.logger.warning(f"API error (attempt {retry_count + 1}/{max_retries + 1}): {error}")

                    if retry_count < max_retries:
                        retry_count += 1
                        time.sleep(backoff_seconds)
                        backoff_seconds *= 2  # Exponential backoff
                    else:
                        self.logger.error(f"Failed to send batch after {max_retries + 1} attempts")
                        if self.on_error:
                            self.on_error(error)
                        return

            except requests.exceptions.Timeout as e:
                error = NetworkError(f"Request timeout: {e}")
                self.logger.warning(f"Timeout error (attempt {retry_count + 1}/{max_retries + 1}): {error}")

                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    self.logger.error(f"Failed to send batch after {max_retries + 1} attempts (timeout)")
                    if self.on_error:
                        self.on_error(error)
                    return

            except requests.exceptions.RequestException as e:
                error = NetworkError(f"Network error: {e}")
                self.logger.warning(f"Network error (attempt {retry_count + 1}/{max_retries + 1}): {error}")

                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    self.logger.error(f"Failed to send batch after {max_retries + 1} attempts (network error)")
                    if self.on_error:
                        self.on_error(error)
                    return

            except Exception as e:
                error = APIError(f"Unexpected error: {e}")
                self.logger.error(f"Unexpected error sending batch: {error}")
                if self.on_error:
                    self.on_error(error)
                return  # Don't retry unexpected errors

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop()
        except:
            pass  # Ignore errors during cleanup
