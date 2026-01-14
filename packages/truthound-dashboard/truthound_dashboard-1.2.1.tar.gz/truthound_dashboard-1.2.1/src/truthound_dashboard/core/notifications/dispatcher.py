"""Notification dispatcher for orchestrating notification delivery.

The dispatcher coordinates between events, rules, and channels to
deliver notifications based on configured triggers.

Architecture:
    Event -> Dispatcher -> Rules -> Channels -> Delivery

Example:
    dispatcher = get_dispatcher()

    # Notify about validation failure
    await dispatcher.notify_validation_failed(
        source_id="source-123",
        source_name="My Source",
        validation_id="val-456",
        has_critical=True,
        has_high=False,
        total_issues=5,
    )
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    NotificationChannel,
    NotificationLog,
    NotificationRule,
    get_session,
)

from .base import (
    BaseNotificationChannel,
    ChannelRegistry,
    NotificationEvent,
    NotificationResult,
)
from .events import (
    DriftDetectedEvent,
    ScheduleFailedEvent,
    TestNotificationEvent,
    ValidationFailedEvent,
)

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Orchestrates notification delivery based on events and rules.

    The dispatcher:
    1. Receives notification events
    2. Matches events against active rules
    3. Resolves target channels from matching rules
    4. Delivers notifications through channels
    5. Logs delivery results

    Usage:
        dispatcher = NotificationDispatcher(session)

        # Send test notification
        results = await dispatcher.test_channel(channel_id)

        # Notify about events
        await dispatcher.notify_validation_failed(...)
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the dispatcher.

        Args:
            session: Database session for accessing rules and channels.
        """
        self.session = session

    async def dispatch(
        self,
        event: NotificationEvent,
        *,
        channel_ids: list[str] | None = None,
        rule_id: str | None = None,
    ) -> list[NotificationResult]:
        """Dispatch a notification event to matching channels.

        If channel_ids is provided, sends directly to those channels.
        Otherwise, matches event against rules to find target channels.

        Args:
            event: The notification event to dispatch.
            channel_ids: Optional explicit channel IDs to send to.
            rule_id: Optional rule ID that triggered this dispatch.

        Returns:
            List of delivery results for each channel.
        """
        # Get target channels
        if channel_ids:
            channels = await self._get_channels_by_ids(channel_ids)
        else:
            channels = await self._get_channels_for_event(event)

        if not channels:
            logger.debug(f"No channels found for event: {event.event_type}")
            return []

        # Dispatch to each channel
        results = []
        for channel_model in channels:
            result = await self._send_to_channel(channel_model, event, rule_id)
            results.append(result)

        return results

    async def _get_channels_by_ids(
        self, channel_ids: list[str]
    ) -> Sequence[NotificationChannel]:
        """Get channels by their IDs."""
        result = await self.session.execute(
            select(NotificationChannel)
            .where(NotificationChannel.id.in_(channel_ids))
            .where(NotificationChannel.is_active == True)
        )
        return result.scalars().all()

    async def _get_channels_for_event(
        self, event: NotificationEvent
    ) -> Sequence[NotificationChannel]:
        """Get channels that should receive this event based on rules."""
        # Get matching rules
        rules = await self._get_matching_rules(event)

        if not rules:
            return []

        # Collect unique channel IDs
        channel_ids: set[str] = set()
        for rule in rules:
            channel_ids.update(rule.channel_ids)

        if not channel_ids:
            return []

        # Get active channels
        return await self._get_channels_by_ids(list(channel_ids))

    async def _get_matching_rules(
        self, event: NotificationEvent
    ) -> Sequence[NotificationRule]:
        """Get rules that match the given event."""
        # Map event types to rule conditions
        condition_map = {
            "validation_failed": ["validation_failed", "critical_issues", "high_issues"],
            "schedule_failed": ["schedule_failed", "validation_failed"],
            "drift_detected": ["drift_detected"],
            "test": [],
        }

        conditions = condition_map.get(event.event_type, [event.event_type])

        if not conditions:
            return []

        # Query matching rules
        result = await self.session.execute(
            select(NotificationRule)
            .where(NotificationRule.is_active == True)
            .where(NotificationRule.condition.in_(conditions))
        )
        all_rules = result.scalars().all()

        # Filter by event-specific conditions
        matching_rules = []
        for rule in all_rules:
            if self._rule_matches_event(rule, event):
                matching_rules.append(rule)

        return matching_rules

    def _rule_matches_event(
        self, rule: NotificationRule, event: NotificationEvent
    ) -> bool:
        """Check if a rule matches the specific event."""
        # Check source filter
        if event.source_id and not rule.matches_source(event.source_id):
            return False

        # Check condition-specific matching
        if isinstance(event, ValidationFailedEvent):
            if rule.condition == "critical_issues" and not event.has_critical:
                return False
            if rule.condition == "high_issues" and not (event.has_critical or event.has_high):
                return False

        elif isinstance(event, DriftDetectedEvent):
            # Could add threshold checks here from rule.condition_config
            pass

        return True

    async def _send_to_channel(
        self,
        channel_model: NotificationChannel,
        event: NotificationEvent,
        rule_id: str | None = None,
    ) -> NotificationResult:
        """Send notification to a specific channel."""
        # Create channel instance
        channel = ChannelRegistry.create(
            channel_type=channel_model.type,
            channel_id=channel_model.id,
            name=channel_model.name,
            config=channel_model.config,
            is_active=channel_model.is_active,
        )

        if channel is None:
            error = f"Unknown channel type: {channel_model.type}"
            await self._log_delivery(channel_model.id, event, False, "", error, rule_id)
            return NotificationResult(
                success=False,
                channel_id=channel_model.id,
                channel_type=channel_model.type,
                message="",
                error=error,
            )

        # Format message for this channel
        message = channel.format_message(event)

        # Send notification
        result = await channel.send_with_result(message, event)

        # Log delivery
        await self._log_delivery(
            channel_model.id,
            event,
            result.success,
            message,
            result.error,
            rule_id,
        )

        return result

    async def _log_delivery(
        self,
        channel_id: str,
        event: NotificationEvent,
        success: bool,
        message: str,
        error: str | None,
        rule_id: str | None,
    ) -> None:
        """Log notification delivery attempt."""
        log = NotificationLog(
            channel_id=channel_id,
            rule_id=rule_id,
            event_type=event.event_type,
            event_data=event.to_dict(),
            message=message[:1000] if message else "",
            status="sent" if success else "failed",
            error_message=error,
        )

        if success:
            log.mark_sent()
        else:
            log.mark_failed(error or "Unknown error")

        self.session.add(log)
        await self.session.flush()

    # =========================================================================
    # Convenience methods for common events
    # =========================================================================

    async def notify_validation_failed(
        self,
        source_id: str,
        source_name: str,
        validation_id: str,
        has_critical: bool = False,
        has_high: bool = False,
        total_issues: int = 0,
        issues: list[dict[str, Any]] | None = None,
    ) -> list[NotificationResult]:
        """Send notifications for a validation failure.

        Args:
            source_id: ID of the source that was validated.
            source_name: Name of the source.
            validation_id: ID of the validation run.
            has_critical: Whether critical issues were found.
            has_high: Whether high severity issues were found.
            total_issues: Total number of issues.
            issues: Optional list of issue details.

        Returns:
            List of delivery results.
        """
        event = ValidationFailedEvent(
            source_id=source_id,
            source_name=source_name,
            validation_id=validation_id,
            has_critical=has_critical,
            has_high=has_high,
            total_issues=total_issues,
            issues=issues or [],
        )

        return await self.dispatch(event)

    async def notify_schedule_failed(
        self,
        source_id: str,
        source_name: str,
        schedule_id: str,
        schedule_name: str,
        validation_id: str | None = None,
        error_message: str | None = None,
    ) -> list[NotificationResult]:
        """Send notifications for a scheduled validation failure.

        Args:
            source_id: ID of the source.
            source_name: Name of the source.
            schedule_id: ID of the schedule.
            schedule_name: Name of the schedule.
            validation_id: Optional ID of the failed validation.
            error_message: Optional error message.

        Returns:
            List of delivery results.
        """
        event = ScheduleFailedEvent(
            source_id=source_id,
            source_name=source_name,
            schedule_id=schedule_id,
            schedule_name=schedule_name,
            validation_id=validation_id,
            error_message=error_message,
        )

        return await self.dispatch(event)

    async def notify_drift_detected(
        self,
        comparison_id: str,
        baseline_source_id: str,
        baseline_source_name: str,
        current_source_id: str,
        current_source_name: str,
        has_high_drift: bool = False,
        drifted_columns: int = 0,
        total_columns: int = 0,
    ) -> list[NotificationResult]:
        """Send notifications for drift detection.

        Args:
            comparison_id: ID of the drift comparison.
            baseline_source_id: ID of the baseline source.
            baseline_source_name: Name of the baseline source.
            current_source_id: ID of the current source.
            current_source_name: Name of the current source.
            has_high_drift: Whether high severity drift was detected.
            drifted_columns: Number of columns with drift.
            total_columns: Total columns compared.

        Returns:
            List of delivery results.
        """
        event = DriftDetectedEvent(
            source_id=baseline_source_id,
            source_name=baseline_source_name,
            comparison_id=comparison_id,
            baseline_source_id=baseline_source_id,
            baseline_source_name=baseline_source_name,
            current_source_id=current_source_id,
            current_source_name=current_source_name,
            has_high_drift=has_high_drift,
            drifted_columns=drifted_columns,
            total_columns=total_columns,
        )

        return await self.dispatch(event)

    async def test_channel(self, channel_id: str) -> NotificationResult:
        """Send a test notification to a specific channel.

        Args:
            channel_id: ID of the channel to test.

        Returns:
            Delivery result.
        """
        # Get channel
        result = await self.session.execute(
            select(NotificationChannel).where(NotificationChannel.id == channel_id)
        )
        channel_model = result.scalar_one_or_none()

        if channel_model is None:
            return NotificationResult(
                success=False,
                channel_id=channel_id,
                channel_type="unknown",
                message="",
                error="Channel not found",
            )

        event = TestNotificationEvent(channel_name=channel_model.name)

        return await self._send_to_channel(channel_model, event)


# =============================================================================
# Singleton management
# =============================================================================

_dispatcher: NotificationDispatcher | None = None


async def get_dispatcher() -> NotificationDispatcher:
    """Get the notification dispatcher instance.

    Creates a new dispatcher with a fresh database session.

    Returns:
        NotificationDispatcher instance.
    """
    async with get_session() as session:
        return NotificationDispatcher(session)


def create_dispatcher(session: AsyncSession) -> NotificationDispatcher:
    """Create a dispatcher with a specific session.

    Use this when you need to share a session with other operations.

    Args:
        session: Database session to use.

    Returns:
        NotificationDispatcher instance.
    """
    return NotificationDispatcher(session)
