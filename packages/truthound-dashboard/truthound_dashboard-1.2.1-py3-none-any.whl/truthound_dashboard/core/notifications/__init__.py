"""Notification system for truthound dashboard.

This package provides an extensible notification system with support for
multiple channels (Slack, Email, Webhook) and configurable rules.

Architecture:
    - BaseNotificationChannel: Abstract base for channel implementations
    - ChannelRegistry: Registry for channel type discovery
    - NotificationDispatcher: Orchestrates notification delivery
    - NotificationService: Business logic for notifications

Example:
    # Register a custom channel
    @ChannelRegistry.register("custom")
    class CustomChannel(BaseNotificationChannel):
        async def send(self, message: str, **kwargs) -> bool:
            ...

    # Send notifications
    dispatcher = get_dispatcher()
    await dispatcher.notify_validation_failed(validation)
"""

from .base import (
    BaseNotificationChannel,
    ChannelRegistry,
    NotificationEvent,
    NotificationResult,
)
from .channels import EmailChannel, SlackChannel, WebhookChannel
from .dispatcher import NotificationDispatcher, create_dispatcher, get_dispatcher
from .events import (
    DriftDetectedEvent,
    ScheduleFailedEvent,
    ValidationFailedEvent,
)

__all__ = [
    # Base classes
    "BaseNotificationChannel",
    "ChannelRegistry",
    "NotificationEvent",
    "NotificationResult",
    # Channel implementations
    "SlackChannel",
    "EmailChannel",
    "WebhookChannel",
    # Dispatcher
    "NotificationDispatcher",
    "create_dispatcher",
    "get_dispatcher",
    # Events
    "ValidationFailedEvent",
    "ScheduleFailedEvent",
    "DriftDetectedEvent",
]
