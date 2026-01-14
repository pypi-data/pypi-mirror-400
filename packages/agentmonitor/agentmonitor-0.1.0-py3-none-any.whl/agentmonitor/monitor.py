import time
import json
import functools
import threading
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from contextlib import contextmanager

import requests


class EventContext:
    """Context for tracking a single event"""

    def __init__(self, event_type: str):
        self.event_type = event_type
        self.input_data = None
        self.output_data = None
        self.metadata = {}
        self.cost_usd = None
        self.error_message = None
        self.status = "success"
        self.start_time = time.time()

    def set_input(self, data: Any):
        """Set input data for the event"""
        self.input_data = self._serialize(data)

    def set_output(self, data: Any):
        """Set output data for the event"""
        self.output_data = self._serialize(data)

    def set_metadata(self, key: str, value: Any):
        """Set metadata for the event"""
        self.metadata[key] = value

    def set_cost(self, cost: float):
        """Set cost in USD"""
        self.cost_usd = cost

    def set_error(self, error: Exception):
        """Set error information"""
        self.status = "failure"
        self.error_message = str(error)

    def get_latency(self) -> int:
        """Get latency in milliseconds"""
        return int((time.time() - self.start_time) * 1000)

    def _serialize(self, data: Any) -> Any:
        """Serialize data for JSON"""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._serialize(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        else:
            return str(data)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API"""
        event = {
            "event_type": self.event_type,
            "status": self.status,
            "latency_ms": self.get_latency(),
        }

        if self.input_data is not None:
            event["input_data"] = self.input_data

        if self.output_data is not None:
            event["output_data"] = self.output_data

        if self.metadata:
            event["metadata"] = self.metadata

        if self.cost_usd is not None:
            event["cost_usd"] = self.cost_usd

        if self.error_message:
            event["error_message"] = self.error_message

        return event


class AgentMonitor:
    """Main monitor class for tracking AI agent events"""

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        api_url: str = "http://localhost:3001",
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        self.api_key = api_key
        self.agent_id = agent_id
        self.api_url = api_url.rstrip("/")
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._event_queue = []
        self._queue_lock = threading.Lock()
        self._flush_timer = None

        # Start the flush timer
        self._start_flush_timer()

    def _start_flush_timer(self):
        """Start the periodic flush timer"""
        if self._flush_timer:
            self._flush_timer.cancel()

        self._flush_timer = threading.Timer(self.flush_interval, self._auto_flush)
        self._flush_timer.daemon = True
        self._flush_timer.start()

    def _auto_flush(self):
        """Automatically flush events on timer"""
        self.flush()
        self._start_flush_timer()

    def track(self, event_type: Optional[str] = None) -> Callable:
        """
        Decorator to track function execution

        Args:
            event_type: Custom event type name. If not provided, uses function name.

        Example:
            @monitor.track()
            def my_function(x, y):
                return x + y
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_event_type = event_type or func.__name__

                ctx = EventContext(func_event_type)

                # Capture inputs
                if args or kwargs:
                    ctx.set_input({"args": args, "kwargs": kwargs})

                try:
                    result = func(*args, **kwargs)
                    ctx.set_output(result)
                    return result
                except Exception as e:
                    ctx.set_error(e)
                    raise
                finally:
                    self._queue_event(ctx)

            return wrapper

        return decorator

    @contextmanager
    def track_context(self, event_type: str):
        """
        Context manager for tracking events

        Example:
            with monitor.track_context("custom_event") as ctx:
                result = do_something()
                ctx.set_output(result)
                ctx.set_cost(0.05)
        """
        ctx = EventContext(event_type)
        try:
            yield ctx
        except Exception as e:
            ctx.set_error(e)
            raise
        finally:
            self._queue_event(ctx)

    def _queue_event(self, ctx: EventContext):
        """Add event to queue and flush if needed"""
        event = ctx.to_dict()
        event["agent_id"] = self.agent_id

        with self._queue_lock:
            self._event_queue.append(event)

            if len(self._event_queue) >= self.batch_size:
                self._flush_events()

    def _flush_events(self):
        """Flush events to API (called with lock held)"""
        if not self._event_queue:
            return

        events_to_send = self._event_queue[:]
        self._event_queue.clear()

        # Send in background thread
        thread = threading.Thread(target=self._send_events, args=(events_to_send,))
        thread.daemon = True
        thread.start()

    def _send_events(self, events: list):
        """Send events to API"""
        try:
            url = f"{self.api_url}/api/v1/events/batch"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            payload = {"events": events}

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            print(f"Successfully sent {len(events)} events to monitor")
        except Exception as e:
            print(f"Failed to send events to monitor: {e}")

    def flush(self):
        """Manually flush all queued events"""
        with self._queue_lock:
            self._flush_events()

    def shutdown(self):
        """Shutdown the monitor and flush remaining events"""
        if self._flush_timer:
            self._flush_timer.cancel()

        self.flush()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.shutdown()
        except:
            pass
