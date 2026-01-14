"""AgentMonitor SDK for Python.

A developer-friendly SDK for monitoring AI agents in production.

Quick Start:
    >>> from agentmonitor import AgentMonitor
    >>>
    >>> monitor = AgentMonitor(
    ...     api_key="demo_key_1234567890abcdefghijklmnopqrstuvwxyz",
    ...     agent_id="my_agent",
    ...     api_url="http://localhost:3002/api/v1"
    ... )
    >>>
    >>> @monitor.track()
    ... def my_agent_function(query: str) -> str:
    ...     return f"Response to: {query}"
    >>>
    >>> result = my_agent_function("Hello")
    >>> monitor.flush()

For async support:
    >>> from agentmonitor import AsyncAgentMonitor
    >>>
    >>> monitor = AsyncAgentMonitor(api_key="...", agent_id="...")
    >>>
    >>> @monitor.track()
    ... async def async_function(data):
    ...     return await process(data)
"""

from .client import AgentMonitor, TrackedEvent
from .models import Event, EventMetadata
from .config import AgentMonitorConfig
from .exceptions import (
    AgentMonitorError,
    APIError,
    AuthenticationError,
    ConfigError,
    NetworkError,
    ValidationError
)

# Optional async support
try:
    from .async_client import AsyncAgentMonitor, AsyncTrackedEvent
    _async_available = True
except ImportError:
    _async_available = False
    AsyncAgentMonitor = None
    AsyncTrackedEvent = None

__version__ = "0.1.0"
__author__ = "AgentMonitor Team"
__license__ = "MIT"

__all__ = [
    # Main clients
    "AgentMonitor",
    # Context managers
    "TrackedEvent",
    # Models
    "Event",
    "EventMetadata",
    # Config
    "AgentMonitorConfig",
    # Exceptions
    "AgentMonitorError",
    "APIError",
    "AuthenticationError",
    "ConfigError",
    "NetworkError",
    "ValidationError",
]

# Add async exports if available
if _async_available:
    __all__.extend(["AsyncAgentMonitor", "AsyncTrackedEvent"])
