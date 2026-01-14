"""Decorators for automatic event tracking.

This module provides the @track decorator for automatic monitoring of functions.
"""

import functools
import time
import asyncio
import inspect
from typing import Any, Callable, Optional, Dict
from .models import Event
from .utils import safe_serialize, format_error_message, get_iso_timestamp


def create_track_decorator(monitor_instance):
    """Create a track decorator bound to a monitor instance.

    Args:
        monitor_instance: AgentMonitor or AsyncAgentMonitor instance

    Returns:
        Track decorator function
    """

    def track(
        event_type: str = "function_call",
        capture_input: bool = True,
        capture_output: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Decorator to automatically track function execution.

        This decorator captures function inputs, outputs, execution time,
        and any errors that occur during execution.

        Args:
            event_type: Type of event (default: "function_call")
            capture_input: Whether to capture function inputs (default: True)
            capture_output: Whether to capture function outputs (default: True)
            metadata: Additional metadata to attach to the event

        Returns:
            Decorated function

        Example:
            >>> @monitor.track()
            ... def my_function(x: int) -> int:
            ...     return x * 2
            >>> result = my_function(5)  # Automatically tracked
        """

        def decorator(func: Callable) -> Callable:
            # Check if function is async
            is_async = asyncio.iscoroutinefunction(func)

            if is_async:
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return await _execute_tracked(
                        func, args, kwargs, event_type,
                        capture_input, capture_output, metadata,
                        is_async=True
                    )
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return _execute_tracked(
                        func, args, kwargs, event_type,
                        capture_input, capture_output, metadata,
                        is_async=False
                    )
                return sync_wrapper

        def _execute_tracked(
            func, args, kwargs, event_type,
            capture_input, capture_output, metadata,
            is_async=False
        ):
            """Execute function with tracking."""
            # Start timing
            start_time = time.time()
            start_timestamp = get_iso_timestamp()

            # Capture input
            input_data = None
            if capture_input:
                input_data = _capture_function_input(func, args, kwargs)

            # Apply redaction if configured
            if monitor_instance.config.redact_keys and input_data:
                from .utils import redact_sensitive_data
                input_data = redact_sensitive_data(input_data, monitor_instance.config.redact_keys)

            # Execute function
            error = None
            output_data = None
            status = "success"
            error_message = None

            try:
                if is_async:
                    # Async execution
                    result = asyncio.create_task(func(*args, **kwargs))
                    # Wait for completion
                    loop = asyncio.get_event_loop()
                    output = loop.run_until_complete(result)
                else:
                    # Sync execution
                    output = func(*args, **kwargs)

                # Capture output
                if capture_output:
                    output_data = safe_serialize(output)

                # Apply redaction if configured
                if monitor_instance.config.redact_keys and output_data:
                    from .utils import redact_sensitive_data
                    output_data = redact_sensitive_data(output_data, monitor_instance.config.redact_keys)

            except Exception as e:
                error = e
                status = "failure"
                error_message = format_error_message(e)
                monitor_instance.logger.debug(f"Function {func.__name__} raised error: {error_message}")

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
                    agent_id=monitor_instance.config.agent_id,
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
                monitor_instance._add_event(event)

                # Re-raise error if one occurred
                if error:
                    raise error

                return output

        return decorator

    return track


def _capture_function_input(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Capture function input arguments.

    Args:
        func: Function being called
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary containing captured input
    """
    # Get function signature
    try:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Convert to serializable format
        input_dict = {}
        for param_name, param_value in bound_args.arguments.items():
            input_dict[param_name] = safe_serialize(param_value)

        return input_dict

    except Exception as e:
        # Fallback: just capture args and kwargs as-is
        return {
            "args": safe_serialize(args) if args else None,
            "kwargs": safe_serialize(kwargs) if kwargs else None
        }


async def _execute_async_tracked(
    func, args, kwargs, monitor_instance, event_type,
    capture_input, capture_output, metadata
):
    """Execute async function with tracking."""
    # Start timing
    start_time = time.time()
    start_timestamp = get_iso_timestamp()

    # Capture input
    input_data = None
    if capture_input:
        input_data = _capture_function_input(func, args, kwargs)

    # Apply redaction if configured
    if monitor_instance.config.redact_keys and input_data:
        from .utils import redact_sensitive_data
        input_data = redact_sensitive_data(input_data, monitor_instance.config.redact_keys)

    # Execute function
    error = None
    output_data = None
    status = "success"
    error_message = None

    try:
        # Async execution
        output = await func(*args, **kwargs)

        # Capture output
        if capture_output:
            output_data = safe_serialize(output)

        # Apply redaction if configured
        if monitor_instance.config.redact_keys and output_data:
            from .utils import redact_sensitive_data
            output_data = redact_sensitive_data(output_data, monitor_instance.config.redact_keys)

    except Exception as e:
        error = e
        status = "failure"
        error_message = format_error_message(e)
        monitor_instance.logger.debug(f"Function {func.__name__} raised error: {error_message}")

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
            agent_id=monitor_instance.config.agent_id,
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
        await monitor_instance._add_event_async(event)

        # Re-raise error if one occurred
        if error:
            raise error

        return output
