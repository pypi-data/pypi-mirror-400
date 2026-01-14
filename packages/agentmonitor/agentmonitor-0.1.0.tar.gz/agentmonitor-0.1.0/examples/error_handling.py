"""Error handling example.

This example demonstrates how AgentMonitor gracefully handles errors
without crashing your application.

Run this example:
    python examples/error_handling.py
"""

from agentmonitor import AgentMonitor
from agentmonitor.exceptions import ConfigError, APIError

# Initialize monitor
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="error_demo_agent",
    api_url="http://localhost:3002/api/v1"
)


@monitor.track()
def function_that_fails(x: int) -> int:
    """Example function that raises an error."""
    if x < 0:
        raise ValueError("x must be non-negative")
    return x * 2


@monitor.track()
def function_with_type_error():
    """Example function with type error."""
    # This will raise TypeError
    return "string" + 5


@monitor.track()
def function_with_zero_division():
    """Example function with division by zero."""
    return 10 / 0


def demonstrate_error_tracking():
    """Show how errors are automatically tracked."""
    print("\n1. Automatic error tracking:")

    # Test 1: ValueError
    try:
        function_that_fails(-5)
    except ValueError as e:
        print(f"   Caught ValueError: {e}")
        print("   (Error was automatically tracked)")

    # Test 2: TypeError
    try:
        function_with_type_error()
    except TypeError as e:
        print(f"   Caught TypeError: {e}")
        print("   (Error was automatically tracked)")

    # Test 3: ZeroDivisionError
    try:
        function_with_zero_division()
    except ZeroDivisionError as e:
        print(f"   Caught ZeroDivisionError: {e}")
        print("   (Error was automatically tracked)")


def demonstrate_graceful_degradation():
    """Show that SDK never crashes your app."""
    print("\n2. Graceful degradation:")

    # Even with wrong API URL, app continues
    bad_monitor = AgentMonitor(
        api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
        agent_id="test",
        api_url="http://invalid-url-that-does-not-exist.com/api/v1",
        retry_attempts=1  # Fail fast for demo
    )

    @bad_monitor.track()
    def normal_function(x):
        return x * 2

    # Function still works even if monitoring fails
    result = normal_function(5)
    print(f"   Function returned: {result}")
    print("   (App continued despite API failure)")


def demonstrate_disabled_tracking():
    """Show how to disable tracking for testing."""
    print("\n3. Disabled tracking for testing:")

    # Create monitor with tracking disabled
    test_monitor = AgentMonitor(
        api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
        agent_id="test",
        api_url="http://localhost:3002/api/v1",
        enabled=False  # Disable tracking
    )

    @test_monitor.track()
    def test_function(x):
        return x * 2

    result = test_function(5)
    print(f"   Function returned: {result}")
    print("   (No events were sent - tracking disabled)")


def demonstrate_error_callback():
    """Show how to handle errors with callbacks."""
    print("\n4. Error callbacks:")

    errors_caught = []

    def error_handler(error: Exception):
        """Custom error handler."""
        errors_caught.append(error)
        print(f"   Custom handler caught: {type(error).__name__}")

    # Monitor with error callback
    callback_monitor = AgentMonitor(
        api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
        agent_id="callback_test",
        api_url="http://invalid-url.com/api/v1",
        retry_attempts=0,
        on_error=error_handler
    )

    @callback_monitor.track()
    def sample_function():
        return "test"

    sample_function()
    callback_monitor.flush()

    print(f"   Total errors caught by callback: {len(errors_caught)}")


def demonstrate_configuration_validation():
    """Show configuration validation."""
    print("\n5. Configuration validation:")

    # Test 1: Invalid API key
    try:
        bad_monitor = AgentMonitor(
            api_key="short",  # Too short
            agent_id="test",
            api_url="http://localhost:3002/api/v1"
        )
    except ConfigError as e:
        print(f"   Caught ConfigError: {e}")

    # Test 2: Invalid agent_id
    try:
        bad_monitor = AgentMonitor(
            api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
            agent_id="",  # Empty
            api_url="http://localhost:3002/api/v1"
        )
    except ConfigError as e:
        print(f"   Caught ConfigError: {e}")

    print("   Configuration validation works correctly")


def demonstrate_partial_failures():
    """Show that SDK handles partial failures."""
    print("\n6. Handling partial failures:")

    @monitor.track()
    def step1():
        return "success"

    @monitor.track()
    def step2():
        raise RuntimeError("Step 2 failed")

    @monitor.track()
    def step3():
        return "success"

    # Run pipeline
    try:
        step1()
        step2()  # This fails
    except RuntimeError:
        pass  # Continue

    step3()  # This still runs

    print("   Pipeline continued after partial failure")
    print("   (All events tracked, including the failure)")


def main():
    """Main function demonstrating error handling."""
    print("=" * 60)
    print("AgentMonitor - Error Handling Example")
    print("=" * 60)

    demonstrate_error_tracking()
    demonstrate_graceful_degradation()
    demonstrate_disabled_tracking()
    demonstrate_error_callback()
    demonstrate_configuration_validation()
    demonstrate_partial_failures()

    # Flush all events
    print("\n7. Flushing events to API...")
    monitor.flush()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see events for agent 'error_demo_agent'")
    print("Including several error events that were automatically captured")
    print("=" * 60)


if __name__ == "__main__":
    main()
