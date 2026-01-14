"""Basic usage example with decorator pattern.

This example demonstrates the simplest way to use AgentMonitor:
1. Initialize the monitor
2. Add @monitor.track() decorator to your functions
3. Call flush() before exiting

Run this example:
    python examples/basic_usage.py
"""

from agentmonitor import AgentMonitor

# Initialize monitor with your API key and agent ID
monitor = AgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="demo_agent",
    api_url="http://localhost:3002/api/v1"
)


@monitor.track()
def chat_with_user(message: str) -> str:
    """Simulate AI chat function.

    The decorator automatically captures:
    - Input: message parameter
    - Output: return value
    - Execution time
    - Any errors that occur
    """
    # Simulate some AI processing
    response = f"AI response to: {message}"
    return response


@monitor.track(event_type="query", metadata={"model": "gpt-4"})
def ask_question(question: str) -> dict:
    """Example with custom event type and metadata."""
    return {
        "question": question,
        "answer": f"The answer to '{question}' is 42",
        "confidence": 0.95
    }


def main():
    """Main function demonstrating basic usage."""
    print("=" * 60)
    print("AgentMonitor - Basic Usage Example")
    print("=" * 60)

    # Example 1: Simple chat
    print("\n1. Simple chat tracking:")
    for i in range(3):
        message = f"Hello, this is message {i + 1}"
        result = chat_with_user(message)
        print(f"   User: {message}")
        print(f"   AI: {result}")

    # Example 2: Question answering
    print("\n2. Question answering with metadata:")
    questions = [
        "What is the meaning of life?",
        "How does AI work?",
    ]

    for question in questions:
        result = ask_question(question)
        print(f"   Q: {question}")
        print(f"   A: {result['answer']}")

    # Flush pending events before exit
    print("\n3. Flushing events to API...")
    monitor.flush()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see 5 events for agent 'demo_agent'")
    print("=" * 60)


if __name__ == "__main__":
    main()
