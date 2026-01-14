"""Async/await usage example.

This example demonstrates how to use AgentMonitor with async functions.

Run this example:
    python examples/async_usage.py
"""

import asyncio
from agentmonitor import AsyncAgentMonitor

# Initialize async monitor
monitor = AsyncAgentMonitor(
    api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    agent_id="async_demo_agent",
    api_url="http://localhost:3002/api/v1"
)


@monitor.track()
async def fetch_data(query: str) -> dict:
    """Simulate async data fetching."""
    # Simulate async I/O
    await asyncio.sleep(0.5)

    return {
        "query": query,
        "results": [f"Result {i}" for i in range(3)],
        "status": "success"
    }


@monitor.track(event_type="analysis", metadata={"model": "gpt-4"})
async def analyze_data(data: dict) -> dict:
    """Simulate async data analysis."""
    # Simulate processing
    await asyncio.sleep(0.3)

    return {
        "input_size": len(data.get("results", [])),
        "analysis": "Data looks good",
        "confidence": 0.92
    }


async def main():
    """Main async function."""
    print("=" * 60)
    print("AgentMonitor - Async Usage Example")
    print("=" * 60)

    # Example 1: Simple async function
    print("\n1. Fetching data asynchronously:")
    data = await fetch_data("user query")
    print(f"   Fetched: {data['status']}")

    # Example 2: Multiple async calls
    print("\n2. Running multiple async operations:")
    tasks = [
        fetch_data("query 1"),
        fetch_data("query 2"),
        fetch_data("query 3")
    ]
    results = await asyncio.gather(*tasks)
    print(f"   Completed {len(results)} operations")

    # Example 3: Chained async operations
    print("\n3. Chained async operations:")
    data = await fetch_data("test query")
    analysis = await analyze_data(data)
    print(f"   Analysis confidence: {analysis['confidence']}")

    # Example 4: Context manager
    print("\n4. Using async context manager:")
    async with monitor.track_event("custom_operation") as event:
        await asyncio.sleep(0.2)
        result = {"status": "completed"}
        event.set_output(result)
        event.set_metadata(operation="custom")

    # Flush pending events
    print("\n5. Flushing events to API...")
    await monitor.flush()

    # Close monitor
    await monitor.stop()

    print("\n" + "=" * 60)
    print("Success! Check your dashboard at http://localhost:3003")
    print("You should see events for agent 'async_demo_agent'")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
