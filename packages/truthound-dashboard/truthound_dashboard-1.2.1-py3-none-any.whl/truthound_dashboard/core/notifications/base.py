"""Base classes for the notification system.

This module provides abstract base classes and protocols for implementing
notification channels with a pluggable architecture.

Design Patterns:
    - Strategy Pattern: Each channel type implements a common interface
    - Registry Pattern: Channels are registered and discovered dynamically
    - Template Method: Common notification flow with customizable steps

Example:
    @ChannelRegistry.register("custom")
    class CustomChannel(BaseNotificationChannel):
        @classmethod
        def get_config_schema(cls) -> dict:
            return {"url": {"type": "string", "required": True}}

        async def send(self, message: str, **kwargs) -> bool:
            # Custom implementation
            return True
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar


class NotificationStatus(str, Enum):
    """Status of a notification delivery attempt."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class NotificationResult:
    """Result of a notification delivery attempt.

    Attributes:
        success: Whether the notification was delivered successfully.
        channel_id: ID of the channel used.
        channel_type: Type of the channel (slack, email, etc.).
        message: The message that was sent.
        error: Error message if delivery failed.
        sent_at: Timestamp of the delivery attempt.
        metadata: Additional metadata about the delivery.
    """

    success: bool
    channel_id: str
    channel_type: str
    message: str
    error: str | None = None
    sent_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationEvent:
    """Base class for notification events.

    Events represent triggering conditions for notifications.
    Subclasses define specific event types with their data.

    Attributes:
        event_type: Type identifier for the event.
        source_id: Optional source ID related to the event.
        source_name: Optional source name for display.
        timestamp: When the event occurred.
        data: Additional event-specific data.
    """

    event_type: str
    source_id: str | None = None
    source_name: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


class BaseNotificationChannel(ABC):
    """Abstract base class for notification channels.

    Each channel type (Slack, Email, Webhook, etc.) implements this
    interface to provide consistent notification delivery.

    Class Attributes:
        channel_type: Unique identifier for this channel type.

    Instance Attributes:
        channel_id: Database ID of the channel configuration.
        name: Human-readable channel name.
        config: Channel-specific configuration.
        is_active: Whether the channel is active.

    Example:
        class SlackChannel(BaseNotificationChannel):
            channel_type = "slack"

            async def send(self, message: str, **kwargs) -> bool:
                webhook_url = self.config["webhook_url"]
                # Send to Slack...
                return True
    """

    channel_type: ClassVar[str] = "base"

    def __init__(
        self,
        channel_id: str,
        name: str,
        config: dict[str, Any],
        is_active: bool = True,
    ) -> None:
        """Initialize the channel.

        Args:
            channel_id: Database ID of the channel.
            name: Human-readable channel name.
            config: Channel-specific configuration.
            is_active: Whether the channel is active.
        """
        self.channel_id = channel_id
        self.name = name
        self.config = config
        self.is_active = is_active

    @classmethod
    @abstractmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get the configuration schema for this channel type.

        Returns a JSON Schema-like dictionary describing required
        and optional configuration fields.

        Returns:
            Configuration schema dictionary.

        Example:
            return {
                "webhook_url": {
                    "type": "string",
                    "required": True,
                    "description": "Slack webhook URL",
                },
            }
        """
        ...

    @classmethod
    def validate_config(cls, config: dict[str, Any]) -> list[str]:
        """Validate channel configuration.

        Args:
            config: Configuration to validate.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []
        schema = cls.get_config_schema()

        for field_name, field_schema in schema.items():
            if field_schema.get("required", False) and field_name not in config:
                errors.append(f"Missing required field: {field_name}")
            elif field_name in config:
                expected_type = field_schema.get("type")
                value = config[field_name]

                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field '{field_name}' must be a string")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"Field '{field_name}' must be an integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field '{field_name}' must be a boolean")
                elif expected_type == "array" and not isinstance(value, list):
                    errors.append(f"Field '{field_name}' must be an array")
                elif expected_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field '{field_name}' must be an object")

        return errors

    @abstractmethod
    async def send(
        self,
        message: str,
        event: NotificationEvent | None = None,
        **kwargs: Any,
    ) -> bool:
        """Send a notification through this channel.

        Args:
            message: The message to send.
            event: Optional event that triggered this notification.
            **kwargs: Additional channel-specific options.

        Returns:
            True if the notification was sent successfully.
        """
        ...

    async def send_with_result(
        self,
        message: str,
        event: NotificationEvent | None = None,
        **kwargs: Any,
    ) -> NotificationResult:
        """Send notification and return detailed result.

        This is a template method that wraps send() with error handling
        and result construction.

        Args:
            message: The message to send.
            event: Optional event that triggered this notification.
            **kwargs: Additional channel-specific options.

        Returns:
            NotificationResult with delivery details.
        """
        try:
            success = await self.send(message, event=event, **kwargs)
            return NotificationResult(
                success=success,
                channel_id=self.channel_id,
                channel_type=self.channel_type,
                message=message,
                error=None if success else "Send returned False",
                metadata={"event_type": event.event_type if event else None},
            )
        except Exception as e:
            return NotificationResult(
                success=False,
                channel_id=self.channel_id,
                channel_type=self.channel_type,
                message=message,
                error=str(e),
                metadata={"event_type": event.event_type if event else None},
            )

    def format_message(self, event: NotificationEvent) -> str:
        """Format a notification message for this channel.

        Override to customize message formatting per channel type.

        Args:
            event: The event to format.

        Returns:
            Formatted message string.
        """
        return self._default_format(event)

    def _default_format(self, event: NotificationEvent) -> str:
        """Default message formatting."""
        source_info = f" for {event.source_name}" if event.source_name else ""
        return f"[{event.event_type}]{source_info}: {event.data}"


class ChannelRegistry:
    """Registry for notification channel types.

    Provides a plugin system for registering and discovering
    channel implementations.

    Usage:
        # Register a channel
        @ChannelRegistry.register("custom")
        class CustomChannel(BaseNotificationChannel):
            ...

        # Get a channel class
        channel_class = ChannelRegistry.get("custom")

        # Create an instance
        channel = ChannelRegistry.create(
            "custom",
            channel_id="123",
            name="My Channel",
            config={...},
        )
    """

    _channels: ClassVar[dict[str, type[BaseNotificationChannel]]] = {}

    @classmethod
    def register(
        cls, channel_type: str
    ) -> type[type[BaseNotificationChannel]]:
        """Decorator to register a channel implementation.

        Args:
            channel_type: Unique identifier for this channel type.

        Returns:
            Decorator function.

        Example:
            @ChannelRegistry.register("slack")
            class SlackChannel(BaseNotificationChannel):
                ...
        """

        def decorator(
            channel_class: type[BaseNotificationChannel],
        ) -> type[BaseNotificationChannel]:
            channel_class.channel_type = channel_type
            cls._channels[channel_type] = channel_class
            return channel_class

        return decorator  # type: ignore

    @classmethod
    def get(cls, channel_type: str) -> type[BaseNotificationChannel] | None:
        """Get a registered channel class by type.

        Args:
            channel_type: Channel type identifier.

        Returns:
            Channel class or None if not found.
        """
        return cls._channels.get(channel_type)

    @classmethod
    def create(
        cls,
        channel_type: str,
        channel_id: str,
        name: str,
        config: dict[str, Any],
        is_active: bool = True,
    ) -> BaseNotificationChannel | None:
        """Create a channel instance by type.

        Args:
            channel_type: Channel type identifier.
            channel_id: Database ID.
            name: Channel name.
            config: Channel configuration.
            is_active: Whether channel is active.

        Returns:
            Channel instance or None if type not found.
        """
        channel_class = cls.get(channel_type)
        if channel_class is None:
            return None

        return channel_class(
            channel_id=channel_id,
            name=name,
            config=config,
            is_active=is_active,
        )

    @classmethod
    def list_types(cls) -> list[str]:
        """Get list of registered channel types.

        Returns:
            List of channel type identifiers.
        """
        return list(cls._channels.keys())

    @classmethod
    def get_all_schemas(cls) -> dict[str, dict[str, Any]]:
        """Get configuration schemas for all registered channels.

        Returns:
            Dictionary mapping channel type to config schema.
        """
        return {
            channel_type: channel_class.get_config_schema()
            for channel_type, channel_class in cls._channels.items()
        }
