"""Notification channel implementations.

This module provides concrete implementations of notification channels
for Slack, Email, and Webhook notifications.

Each channel is registered with the ChannelRegistry and can be
instantiated dynamically based on channel type.
"""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import httpx

from .base import (
    BaseNotificationChannel,
    ChannelRegistry,
    NotificationEvent,
)
from .events import (
    DriftDetectedEvent,
    ScheduleFailedEvent,
    TestNotificationEvent,
    ValidationFailedEvent,
)


@ChannelRegistry.register("slack")
class SlackChannel(BaseNotificationChannel):
    """Slack notification channel using incoming webhooks.

    Configuration:
        webhook_url: Slack incoming webhook URL
        channel: Optional channel override
        username: Optional username override
        icon_emoji: Optional emoji icon (e.g., ":robot:")

    Example config:
        {
            "webhook_url": "https://hooks.slack.com/services/...",
            "username": "Truthound Bot",
            "icon_emoji": ":bar_chart:"
        }
    """

    channel_type = "slack"

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get Slack channel configuration schema."""
        return {
            "webhook_url": {
                "type": "string",
                "required": True,
                "description": "Slack incoming webhook URL",
            },
            "channel": {
                "type": "string",
                "required": False,
                "description": "Channel override (e.g., #alerts)",
            },
            "username": {
                "type": "string",
                "required": False,
                "description": "Bot username override",
            },
            "icon_emoji": {
                "type": "string",
                "required": False,
                "description": "Emoji icon (e.g., :robot:)",
            },
        }

    async def send(
        self,
        message: str,
        event: NotificationEvent | None = None,
        **kwargs: Any,
    ) -> bool:
        """Send notification to Slack.

        Args:
            message: Message text (supports Slack markdown).
            event: Optional triggering event.
            **kwargs: Additional Slack message options.

        Returns:
            True if message was sent successfully.
        """
        webhook_url = self.config["webhook_url"]

        # Build payload
        payload: dict[str, Any] = {
            "text": message,
        }

        # Add blocks for rich formatting
        blocks = self._build_blocks(message, event)
        if blocks:
            payload["blocks"] = blocks

        # Add optional overrides
        if self.config.get("channel"):
            payload["channel"] = self.config["channel"]
        if self.config.get("username"):
            payload["username"] = self.config["username"]
        if self.config.get("icon_emoji"):
            payload["icon_emoji"] = self.config["icon_emoji"]

        # Merge any additional kwargs
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=payload)
            return response.status_code == 200

    def _build_blocks(
        self,
        message: str,
        event: NotificationEvent | None,
    ) -> list[dict[str, Any]]:
        """Build Slack blocks for rich message formatting."""
        blocks = []

        # Main message section
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message},
            }
        )

        # Add context for specific event types
        if isinstance(event, ValidationFailedEvent):
            context_elements = [
                {"type": "mrkdwn", "text": f"*Severity:* {event.severity}"},
                {"type": "mrkdwn", "text": f"*Issues:* {event.total_issues}"},
            ]
            if event.validation_id:
                context_elements.append(
                    {"type": "mrkdwn", "text": f"*ID:* `{event.validation_id[:8]}...`"}
                )
            blocks.append({"type": "context", "elements": context_elements})

        elif isinstance(event, DriftDetectedEvent):
            context_elements = [
                {
                    "type": "mrkdwn",
                    "text": f"*Drift:* {event.drifted_columns}/{event.total_columns} columns",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Percentage:* {event.drift_percentage:.1f}%",
                },
            ]
            blocks.append({"type": "context", "elements": context_elements})

        return blocks

    def format_message(self, event: NotificationEvent) -> str:
        """Format message for Slack with mrkdwn syntax."""
        if isinstance(event, ValidationFailedEvent):
            emoji = ":rotating_light:" if event.has_critical else ":warning:"
            return (
                f"{emoji} *Validation Failed*\n\n"
                f"*Source:* {event.source_name or 'Unknown'}\n"
                f"*Severity:* {event.severity}\n"
                f"*Total Issues:* {event.total_issues}"
            )

        elif isinstance(event, ScheduleFailedEvent):
            return (
                f":clock1: *Scheduled Validation Failed*\n\n"
                f"*Schedule:* {event.schedule_name}\n"
                f"*Source:* {event.source_name or 'Unknown'}\n"
                f"*Error:* {event.error_message or 'Validation failed'}"
            )

        elif isinstance(event, DriftDetectedEvent):
            emoji = ":chart_with_upwards_trend:" if event.has_high_drift else ":chart_with_downwards_trend:"
            return (
                f"{emoji} *Drift Detected*\n\n"
                f"*Baseline:* {event.baseline_source_name}\n"
                f"*Current:* {event.current_source_name}\n"
                f"*Drifted Columns:* {event.drifted_columns}/{event.total_columns} "
                f"({event.drift_percentage:.1f}%)"
            )

        elif isinstance(event, TestNotificationEvent):
            return (
                f":white_check_mark: *Test Notification*\n\n"
                f"This is a test from truthound-dashboard.\n"
                f"Channel: {event.channel_name}"
            )

        return self._default_format(event)


@ChannelRegistry.register("email")
class EmailChannel(BaseNotificationChannel):
    """Email notification channel using SMTP.

    Configuration:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port (default: 587)
        smtp_username: SMTP authentication username
        smtp_password: SMTP authentication password
        from_email: Sender email address
        recipients: List of recipient email addresses
        use_tls: Whether to use TLS (default: True)

    Example config:
        {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "user@gmail.com",
            "smtp_password": "app-password",
            "from_email": "alerts@example.com",
            "recipients": ["admin@example.com"],
            "use_tls": true
        }
    """

    channel_type = "email"

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get Email channel configuration schema."""
        return {
            "smtp_host": {
                "type": "string",
                "required": True,
                "description": "SMTP server hostname",
            },
            "smtp_port": {
                "type": "integer",
                "required": False,
                "default": 587,
                "description": "SMTP server port",
            },
            "smtp_username": {
                "type": "string",
                "required": False,
                "description": "SMTP authentication username",
            },
            "smtp_password": {
                "type": "string",
                "required": False,
                "secret": True,
                "description": "SMTP authentication password",
            },
            "from_email": {
                "type": "string",
                "required": True,
                "description": "Sender email address",
            },
            "recipients": {
                "type": "array",
                "required": True,
                "items": {"type": "string"},
                "description": "List of recipient email addresses",
            },
            "use_tls": {
                "type": "boolean",
                "required": False,
                "default": True,
                "description": "Use TLS encryption",
            },
        }

    async def send(
        self,
        message: str,
        event: NotificationEvent | None = None,
        subject: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """Send notification via email.

        Args:
            message: Email body text.
            event: Optional triggering event (used for subject).
            subject: Optional subject override.
            **kwargs: Additional options.

        Returns:
            True if email was sent successfully.
        """
        try:
            import aiosmtplib
        except ImportError:
            raise ImportError(
                "aiosmtplib is required for email notifications. "
                "Install with: pip install aiosmtplib"
            )

        # Build subject
        if subject is None:
            subject = self._build_subject(event)

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.config["from_email"]
        msg["To"] = ", ".join(self.config["recipients"])

        # Plain text version
        text_part = MIMEText(message, "plain")
        msg.attach(text_part)

        # HTML version
        html_content = self._build_html(message, event)
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Send
        await aiosmtplib.send(
            msg,
            hostname=self.config["smtp_host"],
            port=self.config.get("smtp_port", 587),
            username=self.config.get("smtp_username"),
            password=self.config.get("smtp_password"),
            use_tls=self.config.get("use_tls", True),
        )

        return True

    def _build_subject(self, event: NotificationEvent | None) -> str:
        """Build email subject from event."""
        if event is None:
            return "[Truthound] Notification"

        if isinstance(event, ValidationFailedEvent):
            severity = event.severity
            return f"[Truthound] {severity} - Validation Failed: {event.source_name}"

        elif isinstance(event, ScheduleFailedEvent):
            return f"[Truthound] Schedule Failed: {event.schedule_name}"

        elif isinstance(event, DriftDetectedEvent):
            return f"[Truthound] Drift Detected: {event.baseline_source_name} → {event.current_source_name}"

        elif isinstance(event, TestNotificationEvent):
            return "[Truthound] Test Notification"

        return f"[Truthound] {event.event_type}"

    def _build_html(self, message: str, event: NotificationEvent | None) -> str:
        """Build HTML email body."""
        # Convert newlines to <br> for simple HTML
        html_message = message.replace("\n", "<br>")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #fd9e4b; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; }}
                .footer {{ font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Truthound Dashboard</h2>
                </div>
                <div class="content">
                    <p>{html_message}</p>
                </div>
                <div class="footer">
                    <p>This notification was sent by Truthound Dashboard.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def format_message(self, event: NotificationEvent) -> str:
        """Format message for email (plain text)."""
        if isinstance(event, ValidationFailedEvent):
            return (
                f"Validation Failed\n\n"
                f"Source: {event.source_name or 'Unknown'}\n"
                f"Severity: {event.severity}\n"
                f"Total Issues: {event.total_issues}\n"
                f"Validation ID: {event.validation_id}\n\n"
                f"Please check the dashboard for details."
            )

        elif isinstance(event, ScheduleFailedEvent):
            return (
                f"Scheduled Validation Failed\n\n"
                f"Schedule: {event.schedule_name}\n"
                f"Source: {event.source_name or 'Unknown'}\n"
                f"Error: {event.error_message or 'Validation failed'}\n\n"
                f"Please check the dashboard for details."
            )

        elif isinstance(event, DriftDetectedEvent):
            return (
                f"Drift Detected\n\n"
                f"Baseline: {event.baseline_source_name}\n"
                f"Current: {event.current_source_name}\n"
                f"Drifted Columns: {event.drifted_columns}/{event.total_columns} "
                f"({event.drift_percentage:.1f}%)\n\n"
                f"Please check the dashboard for details."
            )

        elif isinstance(event, TestNotificationEvent):
            return (
                f"Test Notification\n\n"
                f"This is a test notification from truthound-dashboard.\n"
                f"Channel: {event.channel_name}\n\n"
                f"If you received this, your email channel is configured correctly."
            )

        return self._default_format(event)


@ChannelRegistry.register("webhook")
class WebhookChannel(BaseNotificationChannel):
    """Generic webhook notification channel.

    Sends JSON payloads to any HTTP endpoint.

    Configuration:
        url: Webhook endpoint URL
        method: HTTP method (default: POST)
        headers: Optional custom headers
        include_event_data: Whether to include full event data (default: True)

    Example config:
        {
            "url": "https://example.com/webhook",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer token",
                "X-Custom-Header": "value"
            }
        }
    """

    channel_type = "webhook"

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get Webhook channel configuration schema."""
        return {
            "url": {
                "type": "string",
                "required": True,
                "description": "Webhook endpoint URL",
            },
            "method": {
                "type": "string",
                "required": False,
                "default": "POST",
                "description": "HTTP method (GET, POST, PUT)",
            },
            "headers": {
                "type": "object",
                "required": False,
                "description": "Custom HTTP headers",
            },
            "include_event_data": {
                "type": "boolean",
                "required": False,
                "default": True,
                "description": "Include full event data in payload",
            },
        }

    async def send(
        self,
        message: str,
        event: NotificationEvent | None = None,
        payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> bool:
        """Send notification via webhook.

        Args:
            message: Message text.
            event: Optional triggering event.
            payload: Optional custom payload (overrides default).
            **kwargs: Additional options.

        Returns:
            True if webhook call was successful.
        """
        url = self.config["url"]
        method = self.config.get("method", "POST").upper()
        headers = self.config.get("headers", {})

        # Build payload
        if payload is None:
            payload = self._build_payload(message, event)

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=payload)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=payload)
            else:  # Default to POST
                response = await client.post(url, headers=headers, json=payload)

            # Consider 2xx responses as success
            return 200 <= response.status_code < 300

    def _build_payload(
        self,
        message: str,
        event: NotificationEvent | None,
    ) -> dict[str, Any]:
        """Build webhook payload."""
        payload: dict[str, Any] = {
            "message": message,
            "channel_id": self.channel_id,
            "channel_name": self.name,
        }

        if event and self.config.get("include_event_data", True):
            payload["event"] = event.to_dict()
            payload["event_type"] = event.event_type

        return payload

    def format_message(self, event: NotificationEvent) -> str:
        """Format message for webhook (plain text)."""
        if isinstance(event, ValidationFailedEvent):
            return (
                f"Validation failed for {event.source_name or 'Unknown'}: "
                f"{event.total_issues} issues ({event.severity})"
            )

        elif isinstance(event, ScheduleFailedEvent):
            return (
                f"Schedule '{event.schedule_name}' failed for "
                f"{event.source_name or 'Unknown'}"
            )

        elif isinstance(event, DriftDetectedEvent):
            return (
                f"Drift detected: {event.drifted_columns}/{event.total_columns} columns "
                f"({event.drift_percentage:.1f}%)"
            )

        elif isinstance(event, TestNotificationEvent):
            return f"Test notification from truthound-dashboard"

        return self._default_format(event)
