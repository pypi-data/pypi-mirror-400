"""Utility functions for AgentMonitor SDK.

This module provides helper functions for logging, serialization, and data handling.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


def setup_logger(name: str, debug: bool = False) -> logging.Logger:
    """Set up a logger for the SDK.

    Args:
        name: Logger name
        debug: Enable debug logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Only add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG if debug else logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format.

    Returns:
        ISO 8601 formatted timestamp string (UTC)
    """
    return datetime.utcnow().isoformat() + "Z"


def serialize_value(value: Any) -> Any:
    """Serialize a value for JSON encoding.

    Handles common Python types that aren't JSON-serializable by default.

    Args:
        value: Value to serialize

    Returns:
        JSON-serializable value
    """
    if isinstance(value, datetime):
        return value.isoformat()
    elif hasattr(value, '__dict__'):
        return str(value)
    elif isinstance(value, (set, frozenset)):
        return list(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    else:
        return value


def safe_serialize(data: Any) -> Dict[str, Any]:
    """Safely serialize data to JSON-compatible format.

    Args:
        data: Data to serialize (dict, list, primitive, or object)

    Returns:
        JSON-serializable dictionary
    """
    if data is None:
        return {}

    if isinstance(data, dict):
        return {k: serialize_value(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return {'items': [serialize_value(item) for item in data]}
    elif isinstance(data, (str, int, float, bool)):
        return {'value': data}
    else:
        return {'value': serialize_value(data)}


def redact_sensitive_data(data: Dict[str, Any], redact_keys: List[str]) -> Dict[str, Any]:
    """Redact sensitive fields from data.

    Args:
        data: Dictionary to redact from
        redact_keys: List of keys to redact (case-insensitive)

    Returns:
        Dictionary with redacted values
    """
    if not data or not redact_keys:
        return data

    redact_keys_lower = [key.lower() for key in redact_keys]
    result = {}

    for key, value in data.items():
        if key.lower() in redact_keys_lower:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = redact_sensitive_data(value, redact_keys)
        elif isinstance(value, list):
            result[key] = [
                redact_sensitive_data(item, redact_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result


def validate_api_key(api_key: str) -> bool:
    """Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    # API key must be at least 32 characters
    if len(api_key) < 32:
        return False

    return True


def validate_agent_id(agent_id: str) -> bool:
    """Validate agent ID format.

    Args:
        agent_id: Agent ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not agent_id or not isinstance(agent_id, str):
        return False

    # Agent ID should be non-empty
    if len(agent_id.strip()) == 0:
        return False

    return True


def format_error_message(error: Exception) -> str:
    """Format an exception as a clean error message.

    Args:
        error: Exception to format

    Returns:
        Formatted error message string
    """
    error_type = type(error).__name__
    error_msg = str(error)
    return f"{error_type}: {error_msg}" if error_msg else error_type


def truncate_data(data: Any, max_length: int = 1000) -> Any:
    """Truncate large data structures.

    Args:
        data: Data to truncate
        max_length: Maximum length for strings

    Returns:
        Truncated data
    """
    if isinstance(data, str) and len(data) > max_length:
        return data[:max_length] + "... [truncated]"
    elif isinstance(data, dict):
        return {k: truncate_data(v, max_length) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [truncate_data(item, max_length) for item in data]
    else:
        return data
