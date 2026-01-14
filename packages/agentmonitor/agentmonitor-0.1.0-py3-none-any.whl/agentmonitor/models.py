"""Data models for AgentMonitor SDK.

This module defines the core data structures used by the SDK.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
import json


@dataclass
class EventMetadata:
    """Metadata for an event.

    Attributes:
        model: Model name (e.g., "gpt-4")
        user_id: User identifier
        session_id: Session identifier
        tags: List of tags
        custom: Additional custom fields
    """
    model: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[list] = None
    custom: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, filtering None values."""
        result = {}
        if self.model is not None:
            result['model'] = self.model
        if self.user_id is not None:
            result['user_id'] = self.user_id
        if self.session_id is not None:
            result['session_id'] = self.session_id
        if self.tags is not None:
            result['tags'] = self.tags
        if self.custom is not None:
            result.update(self.custom)
        return result


@dataclass
class Event:
    """An event to be tracked.

    This class represents a single monitoring event that will be sent to
    the AgentMonitor API.

    Attributes:
        agent_id: Identifier for the agent
        event_type: Type of event (e.g., "query", "action", "decision")
        timestamp: ISO 8601 timestamp
        input_data: Input data for the event
        output_data: Output data from the event
        metadata: Additional metadata
        cost_usd: Cost in USD
        latency_ms: Latency in milliseconds
        status: Event status ("success" or "error")
        error_message: Error message if status is "error"
    """
    agent_id: str
    event_type: str
    timestamp: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    cost_usd: Optional[float] = None
    latency_ms: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None

    @classmethod
    def create(
        cls,
        agent_id: str,
        event_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cost_usd: Optional[float] = None,
        latency_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> "Event":
        """Create a new Event with automatic timestamp.

        Args:
            agent_id: Identifier for the agent
            event_type: Type of event
            input_data: Input data
            output_data: Output data
            metadata: Additional metadata
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            status: Event status
            error_message: Error message if status is "error"
            timestamp: Override timestamp (ISO 8601 format)

        Returns:
            New Event instance
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"

        return cls(
            agent_id=agent_id,
            event_type=event_type,
            timestamp=timestamp,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API submission.

        Returns:
            Dictionary representation with None values filtered out
        """
        result = {
            'agent_id': self.agent_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'status': self.status
        }

        if self.input_data is not None:
            result['input_data'] = self.input_data
        if self.output_data is not None:
            result['output_data'] = self.output_data
        if self.metadata is not None:
            result['metadata'] = self.metadata
        if self.cost_usd is not None:
            result['cost_usd'] = self.cost_usd
        if self.latency_ms is not None:
            result['latency_ms'] = self.latency_ms
        if self.error_message is not None:
            result['error_message'] = self.error_message

        return result

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())
