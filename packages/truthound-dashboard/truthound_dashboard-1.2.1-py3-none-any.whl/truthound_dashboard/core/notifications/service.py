"""Notification service layer for business logic.

This module provides the service layer for managing notification
channels, rules, and logs using the repository pattern.

Services:
    - NotificationChannelService: Manage notification channels
    - NotificationRuleService: Manage notification rules
    - NotificationLogService: Query notification logs
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    BaseRepository,
    NotificationChannel,
    NotificationLog,
    NotificationRule,
)

from .base import ChannelRegistry


# =============================================================================
# Repositories
# =============================================================================


class NotificationChannelRepository(BaseRepository[NotificationChannel]):
    """Repository for NotificationChannel operations."""

    model = NotificationChannel

    async def get_active(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[NotificationChannel]:
        """Get active channels only.

        Args:
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of active channels.
        """
        return await self.list(
            offset=offset,
            limit=limit,
            filters=[NotificationChannel.is_active == True],
        )

    async def get_by_type(
        self,
        channel_type: str,
        *,
        active_only: bool = True,
    ) -> Sequence[NotificationChannel]:
        """Get channels by type.

        Args:
            channel_type: Type of channels to get.
            active_only: Only return active channels.

        Returns:
            Sequence of channels.
        """
        filters = [NotificationChannel.type == channel_type]
        if active_only:
            filters.append(NotificationChannel.is_active == True)

        return await self.list(filters=filters)


class NotificationRuleRepository(BaseRepository[NotificationRule]):
    """Repository for NotificationRule operations."""

    model = NotificationRule

    async def get_active(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[NotificationRule]:
        """Get active rules only.

        Args:
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of active rules.
        """
        return await self.list(
            offset=offset,
            limit=limit,
            filters=[NotificationRule.is_active == True],
        )

    async def get_by_condition(
        self,
        condition: str,
        *,
        active_only: bool = True,
    ) -> Sequence[NotificationRule]:
        """Get rules by condition type.

        Args:
            condition: Condition type to filter by.
            active_only: Only return active rules.

        Returns:
            Sequence of rules.
        """
        filters = [NotificationRule.condition == condition]
        if active_only:
            filters.append(NotificationRule.is_active == True)

        return await self.list(filters=filters)

    async def get_for_source(
        self,
        source_id: str,
        *,
        active_only: bool = True,
    ) -> Sequence[NotificationRule]:
        """Get rules that apply to a specific source.

        Args:
            source_id: Source ID to check.
            active_only: Only return active rules.

        Returns:
            Sequence of rules.
        """
        # Get all active rules first, then filter by source
        filters = []
        if active_only:
            filters.append(NotificationRule.is_active == True)

        all_rules = await self.list(filters=filters if filters else None)

        # Filter to rules that match this source
        return [r for r in all_rules if r.matches_source(source_id)]


class NotificationLogRepository(BaseRepository[NotificationLog]):
    """Repository for NotificationLog operations."""

    model = NotificationLog

    async def get_for_channel(
        self,
        channel_id: str,
        *,
        limit: int = 50,
    ) -> Sequence[NotificationLog]:
        """Get logs for a specific channel.

        Args:
            channel_id: Channel ID.
            limit: Maximum to return.

        Returns:
            Sequence of logs.
        """
        return await self.list(
            limit=limit,
            filters=[NotificationLog.channel_id == channel_id],
            order_by=NotificationLog.created_at.desc(),
        )

    async def get_recent(
        self,
        *,
        hours: int = 24,
        limit: int = 100,
        status: str | None = None,
    ) -> Sequence[NotificationLog]:
        """Get recent notification logs.

        Args:
            hours: Number of hours to look back.
            limit: Maximum to return.
            status: Optional status filter.

        Returns:
            Sequence of logs.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        filters = [NotificationLog.created_at >= cutoff]

        if status:
            filters.append(NotificationLog.status == status)

        return await self.list(
            limit=limit,
            filters=filters,
            order_by=NotificationLog.created_at.desc(),
        )

    async def get_stats(
        self,
        *,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Get notification statistics.

        Args:
            hours: Number of hours to analyze.

        Returns:
            Statistics dictionary.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Count by status
        result = await self.session.execute(
            select(
                NotificationLog.status,
                func.count(NotificationLog.id).label("count"),
            )
            .where(NotificationLog.created_at >= cutoff)
            .group_by(NotificationLog.status)
        )
        status_counts = {row.status: row.count for row in result}

        # Count by channel
        result = await self.session.execute(
            select(
                NotificationLog.channel_id,
                func.count(NotificationLog.id).label("count"),
            )
            .where(NotificationLog.created_at >= cutoff)
            .group_by(NotificationLog.channel_id)
        )
        channel_counts = {row.channel_id: row.count for row in result}

        return {
            "period_hours": hours,
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "by_channel": channel_counts,
            "success_rate": self._calculate_success_rate(status_counts),
        }

    def _calculate_success_rate(self, status_counts: dict[str, int]) -> float:
        """Calculate success rate from status counts."""
        total = sum(status_counts.values())
        if total == 0:
            return 100.0
        sent = status_counts.get("sent", 0)
        return round(sent / total * 100, 2)


# =============================================================================
# Services
# =============================================================================


class NotificationChannelService:
    """Service for managing notification channels.

    Provides business logic for channel CRUD operations
    and validation.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.repository = NotificationChannelRepository(session)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        active_only: bool = False,
        channel_type: str | None = None,
    ) -> Sequence[NotificationChannel]:
        """List notification channels.

        Args:
            offset: Number to skip.
            limit: Maximum to return.
            active_only: Only return active channels.
            channel_type: Optional type filter.

        Returns:
            Sequence of channels.
        """
        if channel_type:
            channels = await self.repository.get_by_type(
                channel_type, active_only=active_only
            )
            return channels[offset : offset + limit]

        if active_only:
            return await self.repository.get_active(offset=offset, limit=limit)

        return await self.repository.list(offset=offset, limit=limit)

    async def get_by_id(self, channel_id: str) -> NotificationChannel | None:
        """Get channel by ID.

        Args:
            channel_id: Channel ID.

        Returns:
            Channel or None.
        """
        return await self.repository.get_by_id(channel_id)

    async def create(
        self,
        *,
        name: str,
        channel_type: str,
        config: dict[str, Any],
        is_active: bool = True,
    ) -> NotificationChannel:
        """Create a new notification channel.

        Args:
            name: Channel name.
            channel_type: Channel type (slack, email, webhook).
            config: Channel configuration.
            is_active: Whether channel is active.

        Returns:
            Created channel.

        Raises:
            ValueError: If channel type is unknown or config is invalid.
        """
        # Validate channel type
        channel_class = ChannelRegistry.get(channel_type)
        if channel_class is None:
            available = ChannelRegistry.list_types()
            raise ValueError(
                f"Unknown channel type: {channel_type}. "
                f"Available types: {', '.join(available)}"
            )

        # Validate config
        errors = channel_class.validate_config(config)
        if errors:
            raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

        return await self.repository.create(
            name=name,
            type=channel_type,
            config=config,
            is_active=is_active,
        )

    async def update(
        self,
        channel_id: str,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> NotificationChannel | None:
        """Update a notification channel.

        Args:
            channel_id: Channel ID.
            name: New name.
            config: New configuration.
            is_active: New active status.

        Returns:
            Updated channel or None if not found.

        Raises:
            ValueError: If config is invalid.
        """
        channel = await self.repository.get_by_id(channel_id)
        if channel is None:
            return None

        # Validate config if provided
        if config is not None:
            channel_class = ChannelRegistry.get(channel.type)
            if channel_class:
                errors = channel_class.validate_config(config)
                if errors:
                    raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

        # Update fields
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if config is not None:
            update_data["config"] = config
        if is_active is not None:
            update_data["is_active"] = is_active

        if not update_data:
            return channel

        return await self.repository.update(channel_id, **update_data)

    async def delete(self, channel_id: str) -> bool:
        """Delete a notification channel.

        Args:
            channel_id: Channel ID.

        Returns:
            True if deleted.
        """
        return await self.repository.delete(channel_id)

    async def toggle_active(
        self, channel_id: str, is_active: bool
    ) -> NotificationChannel | None:
        """Toggle channel active status.

        Args:
            channel_id: Channel ID.
            is_active: New active status.

        Returns:
            Updated channel or None if not found.
        """
        return await self.update(channel_id, is_active=is_active)

    def get_available_types(self) -> dict[str, dict[str, Any]]:
        """Get available channel types with their schemas.

        Returns:
            Dictionary mapping type to schema.
        """
        return ChannelRegistry.get_all_schemas()


class NotificationRuleService:
    """Service for managing notification rules.

    Provides business logic for rule CRUD operations
    and condition matching.
    """

    # Valid condition types
    VALID_CONDITIONS = [
        "validation_failed",
        "critical_issues",
        "high_issues",
        "schedule_failed",
        "drift_detected",
    ]

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.repository = NotificationRuleRepository(session)
        self.channel_repo = NotificationChannelRepository(session)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        active_only: bool = False,
        condition: str | None = None,
    ) -> Sequence[NotificationRule]:
        """List notification rules.

        Args:
            offset: Number to skip.
            limit: Maximum to return.
            active_only: Only return active rules.
            condition: Optional condition filter.

        Returns:
            Sequence of rules.
        """
        if condition:
            rules = await self.repository.get_by_condition(
                condition, active_only=active_only
            )
            return rules[offset : offset + limit]

        if active_only:
            return await self.repository.get_active(offset=offset, limit=limit)

        return await self.repository.list(offset=offset, limit=limit)

    async def get_by_id(self, rule_id: str) -> NotificationRule | None:
        """Get rule by ID.

        Args:
            rule_id: Rule ID.

        Returns:
            Rule or None.
        """
        return await self.repository.get_by_id(rule_id)

    async def create(
        self,
        *,
        name: str,
        condition: str,
        channel_ids: list[str],
        condition_config: dict[str, Any] | None = None,
        source_ids: list[str] | None = None,
        is_active: bool = True,
    ) -> NotificationRule:
        """Create a new notification rule.

        Args:
            name: Rule name.
            condition: Trigger condition type.
            channel_ids: List of channel IDs to notify.
            condition_config: Optional condition configuration.
            source_ids: Optional source IDs to filter (None = all sources).
            is_active: Whether rule is active.

        Returns:
            Created rule.

        Raises:
            ValueError: If condition is invalid or channels don't exist.
        """
        # Validate condition
        if condition not in self.VALID_CONDITIONS:
            raise ValueError(
                f"Invalid condition: {condition}. "
                f"Valid conditions: {', '.join(self.VALID_CONDITIONS)}"
            )

        # Validate channel IDs exist
        if channel_ids:
            for channel_id in channel_ids:
                channel = await self.channel_repo.get_by_id(channel_id)
                if channel is None:
                    raise ValueError(f"Channel not found: {channel_id}")

        return await self.repository.create(
            name=name,
            condition=condition,
            channel_ids=channel_ids,
            condition_config=condition_config or {},
            source_ids=source_ids,
            is_active=is_active,
        )

    async def update(
        self,
        rule_id: str,
        *,
        name: str | None = None,
        condition: str | None = None,
        channel_ids: list[str] | None = None,
        condition_config: dict[str, Any] | None = None,
        source_ids: list[str] | None = None,
        is_active: bool | None = None,
    ) -> NotificationRule | None:
        """Update a notification rule.

        Args:
            rule_id: Rule ID.
            name: New name.
            condition: New condition.
            channel_ids: New channel IDs.
            condition_config: New condition config.
            source_ids: New source IDs.
            is_active: New active status.

        Returns:
            Updated rule or None if not found.

        Raises:
            ValueError: If condition or channel IDs are invalid.
        """
        rule = await self.repository.get_by_id(rule_id)
        if rule is None:
            return None

        # Validate condition if provided
        if condition is not None and condition not in self.VALID_CONDITIONS:
            raise ValueError(
                f"Invalid condition: {condition}. "
                f"Valid conditions: {', '.join(self.VALID_CONDITIONS)}"
            )

        # Validate channel IDs if provided
        if channel_ids is not None:
            for channel_id in channel_ids:
                channel = await self.channel_repo.get_by_id(channel_id)
                if channel is None:
                    raise ValueError(f"Channel not found: {channel_id}")

        # Build update data
        update_data: dict[str, Any] = {}
        if name is not None:
            update_data["name"] = name
        if condition is not None:
            update_data["condition"] = condition
        if channel_ids is not None:
            update_data["channel_ids"] = channel_ids
        if condition_config is not None:
            update_data["condition_config"] = condition_config
        if source_ids is not None:
            update_data["source_ids"] = source_ids
        if is_active is not None:
            update_data["is_active"] = is_active

        if not update_data:
            return rule

        return await self.repository.update(rule_id, **update_data)

    async def delete(self, rule_id: str) -> bool:
        """Delete a notification rule.

        Args:
            rule_id: Rule ID.

        Returns:
            True if deleted.
        """
        return await self.repository.delete(rule_id)

    async def toggle_active(
        self, rule_id: str, is_active: bool
    ) -> NotificationRule | None:
        """Toggle rule active status.

        Args:
            rule_id: Rule ID.
            is_active: New active status.

        Returns:
            Updated rule or None if not found.
        """
        return await self.update(rule_id, is_active=is_active)

    def get_valid_conditions(self) -> list[str]:
        """Get list of valid condition types.

        Returns:
            List of condition type strings.
        """
        return list(self.VALID_CONDITIONS)


class NotificationLogService:
    """Service for querying notification logs.

    Provides read-only access to notification delivery history.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.repository = NotificationLogRepository(session)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        channel_id: str | None = None,
        status: str | None = None,
        hours: int | None = None,
    ) -> Sequence[NotificationLog]:
        """List notification logs.

        Args:
            offset: Number to skip.
            limit: Maximum to return.
            channel_id: Optional channel filter.
            status: Optional status filter.
            hours: Optional time range in hours.

        Returns:
            Sequence of logs.
        """
        if channel_id:
            return await self.repository.get_for_channel(channel_id, limit=limit)

        if hours:
            return await self.repository.get_recent(
                hours=hours, limit=limit, status=status
            )

        filters = []
        if status:
            filters.append(NotificationLog.status == status)

        return await self.repository.list(
            offset=offset,
            limit=limit,
            filters=filters if filters else None,
            order_by=NotificationLog.created_at.desc(),
        )

    async def get_by_id(self, log_id: str) -> NotificationLog | None:
        """Get log by ID.

        Args:
            log_id: Log ID.

        Returns:
            Log or None.
        """
        return await self.repository.get_by_id(log_id)

    async def get_stats(self, *, hours: int = 24) -> dict[str, Any]:
        """Get notification statistics.

        Args:
            hours: Time range in hours.

        Returns:
            Statistics dictionary.
        """
        return await self.repository.get_stats(hours=hours)
