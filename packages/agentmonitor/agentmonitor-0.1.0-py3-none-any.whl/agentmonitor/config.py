"""Configuration management for AgentMonitor SDK.

This module handles SDK configuration and validation.
"""

from dataclasses import dataclass
from typing import List, Optional
from .exceptions import ConfigError
from .utils import validate_api_key, validate_agent_id


# Default API URL
DEFAULT_API_URL = "https://api.agentmonitor.io/api/v1"

# Default batch settings
DEFAULT_BATCH_SIZE = 10
DEFAULT_FLUSH_INTERVAL = 5.0

# Default retry settings
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30


@dataclass
class AgentMonitorConfig:
    """Configuration for AgentMonitor client.

    Attributes:
        api_key: API key for authentication (minimum 32 characters)
        agent_id: Identifier for the agent being monitored
        api_url: Base URL for the API (default: https://api.agentmonitor.io/api/v1)
        batch_size: Number of events to batch before flushing (default: 10)
        flush_interval: Seconds between automatic flushes (default: 5.0)
        retry_attempts: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 30)
        debug: Enable debug logging (default: False)
        enabled: Enable tracking (default: True)
        redact_keys: List of keys to redact from event data (default: [])
    """
    api_key: str
    agent_id: str
    api_url: str = DEFAULT_API_URL
    batch_size: int = DEFAULT_BATCH_SIZE
    flush_interval: float = DEFAULT_FLUSH_INTERVAL
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    timeout: int = DEFAULT_TIMEOUT
    debug: bool = False
    enabled: bool = True
    redact_keys: List[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Initialize redact_keys if None
        if self.redact_keys is None:
            self.redact_keys = []

        # Validate API key
        if not validate_api_key(self.api_key):
            raise ConfigError(
                "Invalid API key. API key must be at least 32 characters long. "
                "Get your API key from the AgentMonitor dashboard."
            )

        # Validate agent ID
        if not validate_agent_id(self.agent_id):
            raise ConfigError(
                "Invalid agent_id. Agent ID must be a non-empty string."
            )

        # Validate API URL
        if not self.api_url or not isinstance(self.api_url, str):
            raise ConfigError("Invalid api_url. Must be a non-empty string.")

        # Ensure API URL doesn't end with slash
        self.api_url = self.api_url.rstrip('/')

        # Validate batch size
        if not isinstance(self.batch_size, int) or self.batch_size < 1 or self.batch_size > 100:
            raise ConfigError(
                "Invalid batch_size. Must be an integer between 1 and 100."
            )

        # Validate flush interval
        if not isinstance(self.flush_interval, (int, float)) or self.flush_interval < 0.1:
            raise ConfigError(
                "Invalid flush_interval. Must be a number >= 0.1 seconds."
            )

        # Validate retry attempts
        if not isinstance(self.retry_attempts, int) or self.retry_attempts < 0 or self.retry_attempts > 10:
            raise ConfigError(
                "Invalid retry_attempts. Must be an integer between 0 and 10."
            )

        # Validate timeout
        if not isinstance(self.timeout, (int, float)) or self.timeout < 1:
            raise ConfigError(
                "Invalid timeout. Must be a number >= 1 second."
            )

    @property
    def ingest_url(self) -> str:
        """Get the full URL for single event ingestion.

        Returns:
            Full URL for /events/ingest endpoint
        """
        return f"{self.api_url}/events/ingest"

    @property
    def batch_url(self) -> str:
        """Get the full URL for batch event ingestion.

        Returns:
            Full URL for /events/batch endpoint
        """
        return f"{self.api_url}/events/batch"

    @property
    def headers(self) -> dict:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary of headers including authentication
        """
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def __repr__(self) -> str:
        """String representation with redacted API key."""
        # Redact API key for security
        redacted_key = self.api_key[:8] + "..." + self.api_key[-4:]
        return (
            f"AgentMonitorConfig("
            f"api_key='{redacted_key}', "
            f"agent_id='{self.agent_id}', "
            f"api_url='{self.api_url}', "
            f"batch_size={self.batch_size}, "
            f"flush_interval={self.flush_interval}, "
            f"enabled={self.enabled})"
        )
