# AgentMonitor Python SDK - Quick Start Guide

Get up and running in < 5 minutes!

## Step 1: Install (30 seconds)

```bash
# Basic installation
pip install agentmonitor

# With async support
pip install agentmonitor[async]

# For development
git clone https://github.com/agentmonitor/sdk-python.git
cd sdk-python
pip install -e ".[dev]"
```

## Step 2: Initialize Monitor (30 seconds)

```python
from agentmonitor import AgentMonitor

monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",  # Your API key
    agent_id="my_first_agent",                                # Your agent name
    api_url="http://localhost:3002/api/v1"                    # Local dev server
)
```

## Step 3: Add Decorator (30 seconds)

```python
@monitor.track()
def my_ai_function(user_input: str) -> str:
    """Your AI agent function."""
    # Your AI logic here
    response = f"AI says: {user_input.upper()}"
    return response
```

## Step 4: Call Your Function (30 seconds)

```python
# Just call your function normally!
result = my_ai_function("hello world")
print(result)  # Output: AI says: HELLO WORLD

# Events are automatically captured:
# - Input: {"user_input": "hello world"}
# - Output: {"value": "AI says: HELLO WORLD"}
# - Execution time: ~0ms
# - Status: success
```

## Step 5: Flush Events (30 seconds)

```python
# Before your app exits, flush pending events
monitor.flush()

print("Check your dashboard at http://localhost:3003")
```

## Complete Example

```python
from agentmonitor import AgentMonitor

# 1. Initialize
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="demo_agent",
    api_url="http://localhost:3002/api/v1"
)

# 2. Decorate your functions
@monitor.track()
def chat_bot(message: str) -> str:
    return f"Bot: {message}"

@monitor.track(event_type="query", metadata={"model": "gpt-4"})
def ask_question(question: str) -> dict:
    return {
        "question": question,
        "answer": "42",
        "confidence": 0.99
    }

# 3. Use your functions
if __name__ == "__main__":
    # Call functions normally
    chat_bot("Hello!")
    chat_bot("How are you?")
    ask_question("What is AI?")

    # Flush before exit
    monitor.flush()
    print("Done! Check http://localhost:3003")
```

## Run It!

```bash
python your_script.py
```

You should see:
```
Done! Check http://localhost:3003
```

Open `http://localhost:3003` in your browser to see your events!

## What Just Happened?

The SDK automatically captured:

1. **Function inputs**: All parameters
2. **Function outputs**: Return values
3. **Execution time**: In milliseconds
4. **Errors**: If any exceptions occurred
5. **Metadata**: Custom tags you added

All this data is:
- **Batched** (10 events per API call)
- **Sent in background** (doesn't block your app)
- **Retried automatically** (if API is temporarily down)
- **Logged safely** (never crashes your app)

## Next Steps

### Pattern 1: Context Manager (for fine control)

```python
with monitor.track_event("expensive_operation") as event:
    result = call_external_api()

    # Set additional fields
    event.set_output({"result": result})
    event.set_cost(0.05)  # $0.05
    event.set_metadata(api="openai", model="gpt-4")
```

### Pattern 2: Manual Tracking (for legacy code)

```python
monitor.log_event(
    event_type="user_action",
    input_data={"action": "login", "user_id": "123"},
    output_data={"status": "success"},
    metadata={"ip": "192.168.1.1"}
)
```

### Pattern 3: Async Support

```python
from agentmonitor import AsyncAgentMonitor

async_monitor = AsyncAgentMonitor(
    api_key="...",
    agent_id="async_agent",
    api_url="http://localhost:3002/api/v1"
)

@async_monitor.track()
async def async_function(data):
    result = await async_operation(data)
    return result

# Don't forget to flush
await async_monitor.flush()
await async_monitor.stop()
```

## Configuration Options

```python
monitor = AgentMonitor(
    api_key="...",                   # Required
    agent_id="...",                  # Required
    api_url="...",                   # Optional (default: production)
    batch_size=10,                   # Optional (1-100)
    flush_interval=5.0,              # Optional (seconds)
    retry_attempts=3,                # Optional (0-10)
    timeout=30,                      # Optional (seconds)
    debug=False,                     # Optional (enable logging)
    enabled=True,                    # Optional (disable for tests)
    redact_keys=["password"],        # Optional (data privacy)
    on_error=error_callback          # Optional (error handling)
)
```

## Common Use Cases

### Use Case 1: Track LLM API Calls

```python
@monitor.track(event_type="llm_call")
def call_openai(prompt: str) -> str:
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt
    )
    return response.choices[0].text
```

### Use Case 2: Track with Cost

```python
with monitor.track_event("llm_call") as event:
    response = openai.Completion.create(model="gpt-4", prompt=prompt)

    event.set_output({"text": response.choices[0].text})
    event.set_cost(response.usage.total_tokens * 0.00002)  # Calculate cost
    event.set_metadata(
        model="gpt-4",
        tokens=response.usage.total_tokens
    )
```

### Use Case 3: Track Agent Decisions

```python
@monitor.track(event_type="decision")
def choose_action(state: dict) -> str:
    # Your decision logic
    action = decide_best_action(state)
    return action
```

### Use Case 4: Track Multi-Step Pipeline

```python
@monitor.track(event_type="preprocess")
def preprocess(data):
    return clean(data)

@monitor.track(event_type="inference")
def inference(data):
    return model.predict(data)

@monitor.track(event_type="postprocess")
def postprocess(result):
    return format(result)

# Each step is tracked separately
result = postprocess(inference(preprocess(raw_data)))
```

## Troubleshooting

### Events not showing up?

1. **Check API URL**: Make sure backend is running on `http://localhost:3002`
2. **Call flush()**: Events are batched, call `monitor.flush()` to send immediately
3. **Enable debug**: Use `debug=True` to see what's happening

```python
monitor = AgentMonitor(..., debug=True)
```

### Import errors?

```bash
# Make sure agentmonitor is installed
pip install agentmonitor

# Or install in development mode
pip install -e .
```

### Authentication errors?

API key must be at least 32 characters:
```python
# Valid
api_key = "demo_key_1234567890abcdefghijklmnopqrstuvwxyz"

# Invalid
api_key = "short"  # Too short!
```

## Examples

Run the included examples:

```bash
# Basic usage
python examples/basic_usage.py

# Async usage
python examples/async_usage.py

# Context managers
python examples/context_manager.py

# Manual tracking
python examples/manual_tracking.py

# Error handling
python examples/error_handling.py

# Advanced decorators
python examples/decorator_advanced.py
```

## Need Help?

- **Documentation**: See [README.md](README.md) for complete docs
- **Examples**: Check the `examples/` directory
- **Issues**: https://github.com/agentmonitor/sdk-python/issues
- **Email**: support@agentmonitor.io

## Summary

You learned:
1. How to install the SDK
2. How to initialize the monitor
3. How to use the `@track()` decorator
4. How to flush events
5. Three different usage patterns

**Total time**: < 5 minutes

Now go build amazing AI agents with confidence!

---

Happy monitoring! 🚀
