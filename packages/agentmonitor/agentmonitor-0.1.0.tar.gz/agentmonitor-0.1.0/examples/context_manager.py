"""Context manager usage example.

This example demonstrates how to use context managers for manual event tracking
with fine-grained control.

Run this example:
    python examples/context_manager.py
"""

import time
from agentmonitor import AgentMonitor

# Initialize monitor
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="context_demo_agent",
    api_url="http://localhost:3002/api/v1"
)


def process_with_cost_tracking():
    """Example: Track operation cost."""
    print("\n1. Tracking operation with cost:")

    with monitor.track_event(
        event_type="llm_call",
        input_data={"prompt": "Translate 'hello' to Spanish"}
    ) as event:
        # Simulate LLM call
        time.sleep(0.3)
        result = "Hola"

        # Set output and cost
        event.set_output({"translation": result})
        event.set_cost(0.0042)  # $0.0042
        event.set_metadata(model="gpt-4", tokens=50)

    print("   Tracked LLM call with cost")


def process_with_custom_metadata():
    """Example: Track with custom metadata."""
    print("\n2. Tracking with custom metadata:")

    with monitor.track_event(
        event_type="decision",
        input_data={"scenario": "route_selection"}
    ) as event:
        # Make a decision
        time.sleep(0.1)
        decision = "route_A"

        # Set output and metadata
        event.set_output({"route": decision})
        event.set_metadata(
            algorithm="optimization_v2",
            confidence=0.87,
            alternatives=["route_B", "route_C"]
        )

    print("   Tracked decision with metadata")


def process_with_error_handling():
    """Example: Handle errors within context manager."""
    print("\n3. Error handling in context manager:")

    try:
        with monitor.track_event(
            event_type="risky_operation",
            input_data={"action": "process_user_input"}
        ) as event:
            # Simulate some processing
            time.sleep(0.1)

            # Something goes wrong
            raise ValueError("Invalid input format")

    except ValueError as e:
        print(f"   Caught error: {e}")
        print("   (Error was automatically tracked)")


def multi_step_pipeline():
    """Example: Track multi-step pipeline."""
    print("\n4. Multi-step pipeline:")

    # Step 1: Data preprocessing
    with monitor.track_event(
        event_type="preprocessing",
        input_data={"raw_data": "user input"}
    ) as event:
        time.sleep(0.1)
        processed = "CLEANED_DATA"
        event.set_output({"processed": processed})

    # Step 2: Model inference
    with monitor.track_event(
        event_type="inference",
        input_data={"data": processed}
    ) as event:
        time.sleep(0.2)
        prediction = "category_A"
        event.set_output({"prediction": prediction})
        event.set_cost(0.01)
        event.set_metadata(model="classifier_v3")

    # Step 3: Post-processing
    with monitor.track_event(
        event_type="postprocessing",
        input_data={"prediction": prediction}
    ) as event:
        time.sleep(0.05)
        final_result = {"result": prediction, "formatted": True}
        event.set_output(final_result)

    print("   Tracked 3-step pipeline")


def conditional_tracking():
    """Example: Conditional event tracking."""
    print("\n5. Conditional tracking:")

    for i in range(3):
        with monitor.track_event(
            event_type="conditional_check",
            input_data={"iteration": i}
        ) as event:
            # Simulate condition check
            passed = i % 2 == 0

            event.set_output({"passed": passed})
            event.set_metadata(iteration=i)

            if not passed:
                event.set_status("error")
                event.set_error("Condition check failed")

    print("   Tracked conditional checks")


def main():
    """Main function demonstrating context manager patterns."""
    print("=" * 60)
    print("AgentMonitor - Context Manager Example")
    print("=" * 60)

    process_with_cost_tracking()
    process_with_custom_metadata()
    process_with_error_handling()
    multi_step_pipeline()
    conditional_tracking()

    # Flush all events
    print("\n6. Flushing events to API...")
    monitor.flush()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see events for agent 'context_demo_agent'")
    print("=" * 60)


if __name__ == "__main__":
    main()
