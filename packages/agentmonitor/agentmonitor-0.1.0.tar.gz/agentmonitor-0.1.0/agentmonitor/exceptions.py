"""Custom exceptions for AgentMonitor SDK.

This module defines the exception hierarchy used by the SDK.
"""


class AgentMonitorError(Exception):
    """Base exception for all AgentMonitor errors.

    All custom exceptions in the SDK inherit from this base class.
    """
    pass


class ConfigError(AgentMonitorError):
    """Configuration error.

    Raised when the SDK is configured incorrectly.

    Examples:
        - Invalid API key format
        - Missing required parameters
        - Invalid configuration values
    """
    pass


class AuthenticationError(AgentMonitorError):
    """Authentication error.

    Raised when API key authentication fails.

    Attributes:
        status_code: HTTP status code (typically 401 or 403)
        message: Error message
    """
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.status_code = status_code


class APIError(AgentMonitorError):
    """API request error.

    Raised when an API request fails.

    Attributes:
        status_code: HTTP status code
        message: Error message
        response_body: Response body from the API
    """
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        msg = super().__str__()
        if self.status_code:
            msg += f" (status code: {self.status_code})"
        if self.response_body:
            msg += f" - Response: {self.response_body}"
        return msg


class NetworkError(AgentMonitorError):
    """Network error.

    Raised when a network request fails (timeout, connection error, etc.).
    """
    pass


class ValidationError(AgentMonitorError):
    """Validation error.

    Raised when event data fails validation before sending to API.
    """
    pass
