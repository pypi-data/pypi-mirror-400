"""Manual event tracking example.

This example demonstrates how to manually log events without decorators
or context managers. Useful for legacy code or when you need full control.

Run this example:
    python examples/manual_tracking.py
"""

import time
from agentmonitor import AgentMonitor

# Initialize monitor
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="manual_demo_agent",
    api_url="http://localhost:3002/api/v1"
)


def legacy_function(input_text):
    """Example legacy function that can't be modified."""
    time.sleep(0.2)
    return {"processed": input_text.upper()}


def manual_tracking_simple():
    """Example: Simple manual tracking."""
    print("\n1. Simple manual event logging:")

    # Track a simple event
    monitor.log_event(
        event_type="manual_event",
        input_data={"message": "hello"},
        output_data={"response": "world"},
        metadata={"source": "manual_tracking"}
    )

    print("   Logged simple event")


def manual_tracking_with_timing():
    """Example: Manual tracking with timing."""
    print("\n2. Manual tracking with latency:")

    start_time = time.time()

    # Execute operation
    result = legacy_function("test data")

    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)

    # Log event with timing
    monitor.log_event(
        event_type="legacy_call",
        input_data={"data": "test data"},
        output_data=result,
        latency_ms=latency_ms,
        metadata={"function": "legacy_function"}
    )

    print(f"   Logged event with {latency_ms}ms latency")


def manual_tracking_with_cost():
    """Example: Track API calls with cost."""
    print("\n3. Tracking with cost information:")

    # Simulate API call
    prompt = "What is the weather?"
    response = "The weather is sunny"
    tokens = 25
    cost_per_token = 0.00002
    total_cost = tokens * cost_per_token

    # Log event
    monitor.log_event(
        event_type="api_call",
        input_data={"prompt": prompt},
        output_data={"response": response},
        cost_usd=total_cost,
        metadata={
            "model": "gpt-3.5-turbo",
            "tokens": tokens
        }
    )

    print(f"   Logged API call with ${total_cost:.6f} cost")


def manual_error_tracking():
    """Example: Manually track errors."""
    print("\n4. Manual error tracking:")

    try:
        # Simulate operation that fails
        raise ValueError("Invalid configuration")

    except ValueError as e:
        # Log error event
        monitor.log_event(
            event_type="error_event",
            input_data={"operation": "configuration"},
            status="error",
            error_message=str(e),
            metadata={"severity": "high"}
        )

        print(f"   Logged error: {e}")


def batch_tracking():
    """Example: Track multiple events in batch."""
    print("\n5. Batch event tracking:")

    events_to_track = [
        {"user": "alice", "action": "login"},
        {"user": "bob", "action": "query"},
        {"user": "charlie", "action": "logout"}
    ]

    for event_data in events_to_track:
        monitor.log_event(
            event_type="user_action",
            input_data=event_data,
            output_data={"status": "success"},
            metadata={"timestamp": time.time()}
        )

    print(f"   Logged {len(events_to_track)} events")


def conditional_tracking():
    """Example: Conditionally track events."""
    print("\n6. Conditional event tracking:")

    for i in range(5):
        # Only track certain events
        if i % 2 == 0:
            monitor.log_event(
                event_type="filtered_event",
                input_data={"iteration": i},
                output_data={"tracked": True},
                metadata={"filter": "even_only"}
            )

    print("   Logged filtered events (even numbers only)")


def structured_logging():
    """Example: Track structured data."""
    print("\n7. Structured data tracking:")

    # Complex structured data
    monitor.log_event(
        event_type="structured_data",
        input_data={
            "query": {
                "text": "Find restaurants",
                "filters": {
                    "cuisine": "italian",
                    "price_range": "$$$"
                },
                "location": {
                    "lat": 37.7749,
                    "lon": -122.4194
                }
            }
        },
        output_data={
            "results": [
                {"name": "Restaurant A", "rating": 4.5},
                {"name": "Restaurant B", "rating": 4.8}
            ],
            "count": 2
        },
        metadata={
            "search_engine": "v2",
            "cache_hit": False
        }
    )

    print("   Logged structured event")


def main():
    """Main function demonstrating manual tracking."""
    print("=" * 60)
    print("AgentMonitor - Manual Tracking Example")
    print("=" * 60)

    manual_tracking_simple()
    manual_tracking_with_timing()
    manual_tracking_with_cost()
    manual_error_tracking()
    batch_tracking()
    conditional_tracking()
    structured_logging()

    # Flush all events
    print("\n8. Flushing events to API...")
    monitor.flush()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see events for agent 'manual_demo_agent'")
    print("=" * 60)


if __name__ == "__main__":
    main()
