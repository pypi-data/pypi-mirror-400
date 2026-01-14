# AgentMonitor Python SDK

[![PyPI version](https://badge.fury.io/py/agentmonitor.svg)](https://badge.fury.io/py/agentmonitor)
[![Python Support](https://img.shields.io/pypi/pyversions/agentmonitor.svg)](https://pypi.org/project/agentmonitor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready SDK for monitoring AI agents. Track events, measure performance, analyze costs, and gain insights into your AI systems.

## Features

- **Zero Boilerplate**: One decorator and it works
- **Automatic Tracking**: Input, output, timing, and errors captured automatically
- **Batching**: 10x reduction in API calls with smart batching
- **Async Support**: Full async/await compatibility
- **Reliable**: Never crashes your application
- **Type Safe**: Complete type hints for excellent IDE support
- **Flexible**: Decorator, context manager, or manual tracking

## Quick Start (< 5 minutes)

### Installation

```bash
pip install agentmonitor
```

For async support:
```bash
pip install agentmonitor[async]
```

### Basic Usage

```python
from agentmonitor import AgentMonitor

# Initialize monitor
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="my_agent",
    api_url="http://localhost:3002/api/v1"
)

# Track any function with a decorator
@monitor.track()
def chat_with_user(message: str) -> str:
    """Your AI function."""
    response = "AI response to: " + message
    return response

# Call your function normally
result = chat_with_user("Hello!")

# Flush events before exit
monitor.flush()
```

That's it! Events are now flowing to your dashboard at `http://localhost:3003`.

## Usage Patterns

### 1. Decorator Pattern (Recommended)

The simplest way to track functions:

```python
@monitor.track()
def my_agent_function(input_data):
    # Your AI logic here
    return process(input_data)
```

With custom event type and metadata:

```python
@monitor.track(
    event_type="query",
    metadata={"model": "gpt-4", "version": "1.0"}
)
def ask_question(question: str) -> str:
    return generate_answer(question)
```

### 2. Context Manager Pattern

For fine-grained control:

```python
with monitor.track_event("llm_call") as event:
    result = call_llm(prompt)

    # Set output and metadata
    event.set_output({"response": result})
    event.set_cost(0.0042)  # Track cost in USD
    event.set_metadata(model="gpt-4", tokens=150)
```

### 3. Manual Tracking

For legacy code or maximum control:

```python
monitor.log_event(
    event_type="decision",
    input_data={"query": "user input"},
    output_data={"answer": "AI response"},
    metadata={"model": "gpt-4"},
    cost_usd=0.01,
    latency_ms=250,
    status="success"
)
```

### 4. Async Support

Full async/await compatibility:

```python
from agentmonitor import AsyncAgentMonitor

monitor = AsyncAgentMonitor(
    api_key="...",
    agent_id="async_agent",
    api_url="http://localhost:3002/api/v1"
)

@monitor.track()
async def async_function(data):
    result = await async_operation(data)
    return result

# Use async context manager
async with monitor.track_event("async_op") as event:
    result = await perform_async_work()
    event.set_output(result)

# Don't forget to flush
await monitor.flush()
await monitor.stop()
```

## Configuration

### All Options

```python
monitor = AgentMonitor(
    api_key="your_key",              # Required: Your API key (min 32 chars)
    agent_id="my_agent",             # Required: Agent identifier
    api_url="http://...",            # Optional: API URL (default: production)
    batch_size=10,                   # Optional: Events per batch (1-100)
    flush_interval=5.0,              # Optional: Seconds between flushes
    retry_attempts=3,                # Optional: Max retry attempts (0-10)
    timeout=30,                      # Optional: Request timeout in seconds
    debug=False,                     # Optional: Enable debug logging
    enabled=True,                    # Optional: Disable tracking (for testing)
    redact_keys=["password", "api_key"],  # Optional: Keys to redact
    on_error=error_callback          # Optional: Error callback function
)
```

### Configuration Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | **Required** | API key for authentication (minimum 32 characters) |
| `agent_id` | `str` | **Required** | Identifier for your agent |
| `api_url` | `str` | `https://api.agentmonitor.io/api/v1` | Base URL for the API |
| `batch_size` | `int` | `10` | Number of events to batch before flushing (1-100) |
| `flush_interval` | `float` | `5.0` | Seconds between automatic flushes |
| `retry_attempts` | `int` | `3` | Maximum number of retry attempts (0-10) |
| `timeout` | `int` | `30` | Request timeout in seconds |
| `debug` | `bool` | `False` | Enable debug logging |
| `enabled` | `bool` | `True` | Enable/disable tracking (useful for tests) |
| `redact_keys` | `List[str]` | `[]` | List of keys to redact from data |
| `on_error` | `Callable` | `None` | Callback for error handling |

## Advanced Features

### Error Handling

Errors are automatically captured and tracked:

```python
@monitor.track()
def risky_function(x):
    if x < 0:
        raise ValueError("x must be positive")
    return x * 2

try:
    risky_function(-1)
except ValueError:
    pass  # Error was automatically tracked with status="error"
```

### Data Redaction

Protect sensitive information:

```python
monitor = AgentMonitor(
    api_key="...",
    agent_id="...",
    redact_keys=["password", "api_key", "ssn", "credit_card"]
)

@monitor.track()
def process_user(username, password, api_key):
    # password and api_key will be redacted as "[REDACTED]"
    return {"status": "processed"}
```

### Selective Capture

Control what gets tracked:

```python
# Don't capture sensitive inputs
@monitor.track(capture_input=False, capture_output=True)
def process_sensitive(api_key, user_data):
    return process(user_data)

# Don't capture outputs containing secrets
@monitor.track(capture_input=True, capture_output=False)
def generate_token(user_id):
    return {"token": "secret_abc123"}
```

### Class Methods

Track methods in classes:

```python
class AIAgent:
    @monitor.track(event_type="agent_query")
    def query(self, question: str) -> dict:
        return {
            "answer": self.generate_answer(question),
            "confidence": 0.92
        }
```

### Disable Tracking (for Testing)

```python
# Disable tracking in tests
test_monitor = AgentMonitor(
    api_key="...",
    agent_id="...",
    enabled=False  # No events will be sent
)
```

### Error Callbacks

Handle errors your way:

```python
def my_error_handler(error: Exception):
    print(f"AgentMonitor error: {error}")
    # Log to your error tracking system

monitor = AgentMonitor(
    api_key="...",
    agent_id="...",
    on_error=my_error_handler
)
```

## API Reference

### AgentMonitor

Main synchronous client for tracking events.

#### Methods

##### `track(event_type="function_call", capture_input=True, capture_output=True, metadata=None)`

Decorator for automatic function tracking.

**Parameters:**
- `event_type` (str): Type of event (default: "function_call")
- `capture_input` (bool): Capture function inputs (default: True)
- `capture_output` (bool): Capture function outputs (default: True)
- `metadata` (dict): Additional metadata to attach

**Returns:** Decorated function

##### `track_event(event_type, input_data=None)`

Create a context manager for manual tracking.

**Parameters:**
- `event_type` (str): Type of event
- `input_data` (dict): Initial input data

**Returns:** TrackedEvent context manager

##### `log_event(**kwargs)`

Manually log an event.

**Parameters:**
- `event_type` (str): Type of event
- `input_data` (dict): Input data
- `output_data` (dict): Output data
- `metadata` (dict): Additional metadata
- `cost_usd` (float): Cost in USD
- `latency_ms` (int): Latency in milliseconds
- `status` (str): "success" or "error"
- `error_message` (str): Error message if status is "error"
- `timestamp` (str): Override timestamp (ISO 8601)

##### `flush()`

Flush all pending events immediately (blocking).

##### `close()`

Close the monitor and cleanup resources.

### AsyncAgentMonitor

Asynchronous client with the same API as `AgentMonitor`, but all methods are async.

### Exceptions

- `AgentMonitorError`: Base exception
- `ConfigError`: Configuration error
- `APIError`: API request error
- `AuthenticationError`: Authentication error
- `NetworkError`: Network error
- `ValidationError`: Validation error

## Examples

See the [`examples/`](examples/) directory for complete examples:

- [`basic_usage.py`](examples/basic_usage.py) - Simple decorator example
- [`async_usage.py`](examples/async_usage.py) - Async/await example
- [`context_manager.py`](examples/context_manager.py) - Context manager patterns
- [`manual_tracking.py`](examples/manual_tracking.py) - Manual event logging
- [`error_handling.py`](examples/error_handling.py) - Error handling patterns
- [`decorator_advanced.py`](examples/decorator_advanced.py) - Advanced decorator features

Run an example:
```bash
python examples/basic_usage.py
```

## Performance

### Batching Benefits

Without batching: 100 events = 100 API calls
With batching (size=10): 100 events = 10 API calls

**10x reduction in network overhead!**

### Background Processing

Events are sent in a background thread, so your application isn't blocked:

- Minimal overhead: < 1ms per tracked call
- Automatic flushing every 5 seconds (configurable)
- Thread-safe queue implementation
- Graceful shutdown with pending event handling

## Troubleshooting

### Events not appearing in dashboard

1. Check API URL is correct:
   ```python
   monitor = AgentMonitor(
       api_key="...",
       agent_id="...",
       api_url="http://localhost:3002/api/v1"  # Check this!
   )
   ```

2. Call `flush()` before exit:
   ```python
   monitor.flush()  # Sends pending events
   ```

3. Enable debug logging:
   ```python
   monitor = AgentMonitor(..., debug=True)
   ```

### Authentication errors

Ensure your API key is at least 32 characters:
```python
# Valid
api_key = "demo_key_1234567890abcdefghijklmnopqrstuvwxyz"

# Invalid (too short)
api_key = "short_key"
```

### Network errors

The SDK retries automatically with exponential backoff (1s, 2s, 4s). If the API is down, events will be logged but your app will continue running.

### Import errors

Ensure the package is installed:
```bash
pip install agentmonitor
```

For async support:
```bash
pip install agentmonitor[async]
```

## Development

### Setup

```bash
git clone https://github.com/agentmonitor/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=agentmonitor --cov-report=html
```

### Code Formatting

```bash
black agentmonitor/
flake8 agentmonitor/
mypy agentmonitor/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://docs.agentmonitor.io
- **Issues**: https://github.com/agentmonitor/sdk-python/issues
- **Email**: support@agentmonitor.io

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

Made with love by the AgentMonitor team. Happy monitoring!
