"""Advanced decorator usage examples.

This example demonstrates advanced decorator patterns including:
- Custom event types
- Metadata customization
- Selective input/output capture
- Multiple monitors

Run this example:
    python examples/decorator_advanced.py
"""

import time
from agentmonitor import AgentMonitor

# Initialize monitor
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="advanced_demo_agent",
    api_url="http://localhost:3002/api/v1"
)


# Example 1: Custom event types
@monitor.track(event_type="query")
def search_function(query: str) -> list:
    """Search with custom event type."""
    time.sleep(0.1)
    return [f"result_{i}" for i in range(3)]


@monitor.track(event_type="decision")
def routing_function(input_data: dict) -> str:
    """Route with custom event type."""
    return "route_A" if input_data.get("priority") == "high" else "route_B"


# Example 2: Metadata customization
@monitor.track(metadata={"model": "gpt-4", "version": "1.0"})
def llm_function(prompt: str) -> str:
    """Function with static metadata."""
    time.sleep(0.2)
    return f"Response to: {prompt}"


@monitor.track(metadata={"component": "preprocessor", "stage": "input"})
def preprocessing_function(raw_data: str) -> str:
    """Preprocessing with metadata."""
    return raw_data.upper()


# Example 3: Selective capture
@monitor.track(capture_input=False, capture_output=True)
def sensitive_input_function(api_key: str, user_id: str) -> dict:
    """Don't capture sensitive inputs."""
    return {"status": "processed", "user_id": user_id}


@monitor.track(capture_input=True, capture_output=False)
def sensitive_output_function(query: str) -> dict:
    """Don't capture sensitive outputs."""
    return {"secret_token": "abc123", "result": "data"}


# Example 4: Nested functions
@monitor.track(event_type="parent_operation")
def parent_function(data: str) -> dict:
    """Parent function that calls child."""
    result1 = child_function_1(data)
    result2 = child_function_2(result1)
    return {"final": result2}


@monitor.track(event_type="child_op_1")
def child_function_1(data: str) -> str:
    """First child function."""
    return data.upper()


@monitor.track(event_type="child_op_2")
def child_function_2(data: str) -> str:
    """Second child function."""
    return data + "_processed"


# Example 5: Class methods
class AIAgent:
    """Example AI agent class."""

    def __init__(self, name: str):
        self.name = name

    @monitor.track(event_type="agent_query")
    def query(self, question: str) -> dict:
        """Agent query method."""
        time.sleep(0.1)
        return {
            "agent": self.name,
            "answer": f"Answer to: {question}",
            "confidence": 0.9
        }

    @monitor.track(event_type="agent_action")
    def perform_action(self, action: str) -> str:
        """Agent action method."""
        return f"{self.name} performed: {action}"


# Example 6: Multiple decorators (stacking)
def timing_decorator(func):
    """Custom timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"   [{func.__name__}] took {elapsed:.3f}s")
        return result
    return wrapper


@timing_decorator
@monitor.track(event_type="timed_operation")
def complex_operation(data: str) -> str:
    """Function with multiple decorators."""
    time.sleep(0.2)
    return data.upper()


# Example 7: Data redaction
redacting_monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="redacting_agent",
    api_url="http://localhost:3002/api/v1",
    redact_keys=["password", "api_key", "secret"]
)


@redacting_monitor.track()
def process_user_data(username: str, password: str, api_key: str) -> dict:
    """Function that handles sensitive data."""
    return {
        "username": username,
        "authenticated": True,
        "api_key": api_key  # Will be redacted
    }


def main():
    """Main function demonstrating advanced patterns."""
    print("=" * 60)
    print("AgentMonitor - Advanced Decorator Examples")
    print("=" * 60)

    # 1. Custom event types
    print("\n1. Custom event types:")
    search_function("test query")
    routing_function({"priority": "high"})
    print("   Logged with custom event types")

    # 2. Metadata customization
    print("\n2. Metadata customization:")
    llm_function("What is AI?")
    preprocessing_function("raw data")
    print("   Logged with custom metadata")

    # 3. Selective capture
    print("\n3. Selective input/output capture:")
    sensitive_input_function("secret_key_123", "user_456")
    sensitive_output_function("public query")
    print("   Logged with selective capture")

    # 4. Nested functions
    print("\n4. Nested function tracking:")
    result = parent_function("test")
    print(f"   Result: {result}")
    print("   Logged parent and child operations")

    # 5. Class methods
    print("\n5. Class method tracking:")
    agent = AIAgent("Agent-007")
    agent.query("What is machine learning?")
    agent.perform_action("analyze_data")
    print("   Logged agent methods")

    # 6. Multiple decorators
    print("\n6. Multiple decorators (stacking):")
    complex_operation("test data")
    print("   Logged with timing decorator")

    # 7. Data redaction
    print("\n7. Data redaction:")
    process_user_data("john_doe", "secret_password", "sk-abc123")
    redacting_monitor.flush()
    print("   Logged with sensitive data redacted")

    # Flush all events
    print("\n8. Flushing events to API...")
    monitor.flush()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see events for agent 'advanced_demo_agent'")
    print("=" * 60)


if __name__ == "__main__":
    main()
