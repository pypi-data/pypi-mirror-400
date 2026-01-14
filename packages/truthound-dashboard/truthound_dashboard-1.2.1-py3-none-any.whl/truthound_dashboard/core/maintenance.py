"""Database maintenance and cleanup tasks.

This module provides automated database maintenance operations including:
- Cleanup of old validation records
- Removal of stale profile data
- Notification log cleanup
- Database optimization (VACUUM)

The maintenance system uses a configurable strategy pattern allowing
custom cleanup policies.

Example:
    manager = get_maintenance_manager()
    await manager.run_cleanup()
    await manager.vacuum()
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import delete, func, select, text

from truthound_dashboard.config import get_settings
from truthound_dashboard.db import get_session
from truthound_dashboard.db.models import (
    NotificationLog,
    Profile,
    Source,
    Validation,
)

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of a cleanup operation.

    Attributes:
        task_name: Name of the cleanup task.
        records_deleted: Number of records deleted.
        duration_ms: Duration in milliseconds.
        success: Whether the operation succeeded.
        error: Error message if failed.
    """

    task_name: str
    records_deleted: int = 0
    duration_ms: int = 0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_name": self.task_name,
            "records_deleted": self.records_deleted,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class MaintenanceConfig:
    """Configuration for maintenance tasks.

    Attributes:
        validation_retention_days: Days to keep validation records.
        profile_keep_per_source: Number of profiles to keep per source.
        notification_log_retention_days: Days to keep notification logs.
        run_vacuum: Whether to run VACUUM after cleanup.
    """

    validation_retention_days: int = 90
    profile_keep_per_source: int = 5
    notification_log_retention_days: int = 30
    run_vacuum: bool = True
    enabled: bool = True


class CleanupStrategy(ABC):
    """Abstract base class for cleanup strategies.

    Subclass this to implement custom cleanup logic.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get strategy name."""
        ...

    @abstractmethod
    async def execute(self, config: MaintenanceConfig) -> CleanupResult:
        """Execute cleanup strategy.

        Args:
            config: Maintenance configuration.

        Returns:
            CleanupResult with operation details.
        """
        ...


class ValidationCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for old validation records."""

    @property
    def name(self) -> str:
        return "validation_cleanup"

    async def execute(self, config: MaintenanceConfig) -> CleanupResult:
        """Remove validation records older than retention period."""
        start_time = datetime.utcnow()

        try:
            cutoff = datetime.utcnow() - timedelta(
                days=config.validation_retention_days
            )

            async with get_session() as session:
                # Count records to delete
                count_result = await session.execute(
                    select(func.count(Validation.id)).where(
                        Validation.created_at < cutoff
                    )
                )
                count = count_result.scalar() or 0

                # Delete old records
                if count > 0:
                    await session.execute(
                        delete(Validation).where(Validation.created_at < cutoff)
                    )

                duration = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                logger.info(
                    f"Validation cleanup: deleted {count} records "
                    f"older than {config.validation_retention_days} days"
                )

                return CleanupResult(
                    task_name=self.name,
                    records_deleted=count,
                    duration_ms=duration,
                    success=True,
                )

        except Exception as e:
            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Validation cleanup failed: {e}")
            return CleanupResult(
                task_name=self.name,
                duration_ms=duration,
                success=False,
                error=str(e),
            )


class ProfileCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for keeping only recent profiles per source."""

    @property
    def name(self) -> str:
        return "profile_cleanup"

    async def execute(self, config: MaintenanceConfig) -> CleanupResult:
        """Keep only the most recent N profiles per source."""
        start_time = datetime.utcnow()
        total_deleted = 0

        try:
            async with get_session() as session:
                # Get all source IDs
                sources_result = await session.execute(select(Source.id))
                source_ids = [row[0] for row in sources_result]

                for source_id in source_ids:
                    # Get IDs of profiles to keep
                    keep_result = await session.execute(
                        select(Profile.id)
                        .where(Profile.source_id == source_id)
                        .order_by(Profile.created_at.desc())
                        .limit(config.profile_keep_per_source)
                    )
                    keep_ids = [row[0] for row in keep_result]

                    if not keep_ids:
                        continue

                    # Count and delete excess profiles
                    count_result = await session.execute(
                        select(func.count(Profile.id))
                        .where(Profile.source_id == source_id)
                        .where(Profile.id.not_in(keep_ids))
                    )
                    count = count_result.scalar() or 0

                    if count > 0:
                        await session.execute(
                            delete(Profile)
                            .where(Profile.source_id == source_id)
                            .where(Profile.id.not_in(keep_ids))
                        )
                        total_deleted += count

            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            logger.info(
                f"Profile cleanup: deleted {total_deleted} records, "
                f"keeping {config.profile_keep_per_source} per source"
            )

            return CleanupResult(
                task_name=self.name,
                records_deleted=total_deleted,
                duration_ms=duration,
                success=True,
            )

        except Exception as e:
            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Profile cleanup failed: {e}")
            return CleanupResult(
                task_name=self.name,
                duration_ms=duration,
                success=False,
                error=str(e),
            )


class NotificationLogCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for old notification logs."""

    @property
    def name(self) -> str:
        return "notification_log_cleanup"

    async def execute(self, config: MaintenanceConfig) -> CleanupResult:
        """Remove notification logs older than retention period."""
        start_time = datetime.utcnow()

        try:
            cutoff = datetime.utcnow() - timedelta(
                days=config.notification_log_retention_days
            )

            async with get_session() as session:
                # Count records to delete
                count_result = await session.execute(
                    select(func.count(NotificationLog.id)).where(
                        NotificationLog.created_at < cutoff
                    )
                )
                count = count_result.scalar() or 0

                # Delete old records
                if count > 0:
                    await session.execute(
                        delete(NotificationLog).where(
                            NotificationLog.created_at < cutoff
                        )
                    )

                duration = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                logger.info(
                    f"Notification log cleanup: deleted {count} records "
                    f"older than {config.notification_log_retention_days} days"
                )

                return CleanupResult(
                    task_name=self.name,
                    records_deleted=count,
                    duration_ms=duration,
                    success=True,
                )

        except Exception as e:
            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Notification log cleanup failed: {e}")
            return CleanupResult(
                task_name=self.name,
                duration_ms=duration,
                success=False,
                error=str(e),
            )


@dataclass
class MaintenanceReport:
    """Report of a complete maintenance run.

    Attributes:
        started_at: When maintenance started.
        completed_at: When maintenance completed.
        results: List of cleanup results.
        vacuum_performed: Whether VACUUM was run.
    """

    started_at: datetime
    completed_at: datetime | None = None
    results: list[CleanupResult] = field(default_factory=list)
    vacuum_performed: bool = False
    vacuum_error: str | None = None

    @property
    def total_deleted(self) -> int:
        """Get total records deleted across all tasks."""
        return sum(r.records_deleted for r in self.results)

    @property
    def total_duration_ms(self) -> int:
        """Get total duration in milliseconds."""
        if self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return 0

    @property
    def success(self) -> bool:
        """Check if all tasks succeeded."""
        return all(r.success for r in self.results) and self.vacuum_error is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "results": [r.to_dict() for r in self.results],
            "total_deleted": self.total_deleted,
            "total_duration_ms": self.total_duration_ms,
            "vacuum_performed": self.vacuum_performed,
            "vacuum_error": self.vacuum_error,
            "success": self.success,
        }


class MaintenanceManager:
    """Manager for database maintenance operations.

    Coordinates cleanup strategies and provides a unified interface
    for maintenance tasks.

    Usage:
        manager = MaintenanceManager()
        manager.register_strategy(ValidationCleanupStrategy())
        report = await manager.run_cleanup()
    """

    def __init__(self, config: MaintenanceConfig | None = None) -> None:
        """Initialize maintenance manager.

        Args:
            config: Maintenance configuration. Uses defaults if not provided.
        """
        self._config = config or MaintenanceConfig()
        self._strategies: list[CleanupStrategy] = []

    @property
    def config(self) -> MaintenanceConfig:
        """Get maintenance configuration."""
        return self._config

    def register_strategy(self, strategy: CleanupStrategy) -> None:
        """Register a cleanup strategy.

        Args:
            strategy: Cleanup strategy to register.
        """
        self._strategies.append(strategy)

    def register_default_strategies(self) -> None:
        """Register all default cleanup strategies."""
        self._strategies = [
            ValidationCleanupStrategy(),
            ProfileCleanupStrategy(),
            NotificationLogCleanupStrategy(),
        ]

    async def run_cleanup(self) -> MaintenanceReport:
        """Run all registered cleanup strategies.

        Returns:
            MaintenanceReport with all results.
        """
        if not self._config.enabled:
            logger.info("Maintenance is disabled")
            return MaintenanceReport(
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

        report = MaintenanceReport(started_at=datetime.utcnow())

        for strategy in self._strategies:
            try:
                result = await strategy.execute(self._config)
                report.results.append(result)
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}")
                report.results.append(
                    CleanupResult(
                        task_name=strategy.name,
                        success=False,
                        error=str(e),
                    )
                )

        # Run VACUUM if configured
        if self._config.run_vacuum:
            try:
                await self.vacuum()
                report.vacuum_performed = True
            except Exception as e:
                report.vacuum_error = str(e)
                logger.error(f"VACUUM failed: {e}")

        report.completed_at = datetime.utcnow()

        logger.info(
            f"Maintenance completed: {report.total_deleted} records deleted "
            f"in {report.total_duration_ms}ms"
        )

        return report

    async def vacuum(self) -> None:
        """Run SQLite VACUUM to reclaim space."""
        from truthound_dashboard.db.database import get_engine

        logger.info("Running database VACUUM")

        engine = get_engine()
        async with engine.begin() as conn:
            # VACUUM cannot run in a transaction, so we need raw connection
            await conn.execute(text("VACUUM"))

        logger.info("Database VACUUM completed")

    async def run_task(self, task_name: str) -> CleanupResult | None:
        """Run a specific cleanup task by name.

        Args:
            task_name: Name of the task to run.

        Returns:
            CleanupResult or None if task not found.
        """
        for strategy in self._strategies:
            if strategy.name == task_name:
                return await strategy.execute(self._config)
        return None


# Singleton instance
_manager: MaintenanceManager | None = None


def get_maintenance_manager() -> MaintenanceManager:
    """Get maintenance manager singleton.

    Returns:
        MaintenanceManager with default strategies registered.
    """
    global _manager
    if _manager is None:
        _manager = MaintenanceManager()
        _manager.register_default_strategies()
    return _manager


def reset_maintenance_manager() -> None:
    """Reset maintenance manager singleton (for testing)."""
    global _manager
    _manager = None


# Convenience functions for scheduled tasks
async def cleanup_old_validations(days: int | None = None) -> CleanupResult:
    """Cleanup old validation records.

    Args:
        days: Override retention days. Uses config default if not specified.

    Returns:
        CleanupResult with operation details.
    """
    manager = get_maintenance_manager()
    if days is not None:
        manager.config.validation_retention_days = days
    return await ValidationCleanupStrategy().execute(manager.config)


async def cleanup_old_profiles(keep_per_source: int | None = None) -> CleanupResult:
    """Cleanup old profile records.

    Args:
        keep_per_source: Override profiles to keep. Uses config default if not specified.

    Returns:
        CleanupResult with operation details.
    """
    manager = get_maintenance_manager()
    if keep_per_source is not None:
        manager.config.profile_keep_per_source = keep_per_source
    return await ProfileCleanupStrategy().execute(manager.config)


async def cleanup_notification_logs(days: int | None = None) -> CleanupResult:
    """Cleanup old notification logs.

    Args:
        days: Override retention days. Uses config default if not specified.

    Returns:
        CleanupResult with operation details.
    """
    manager = get_maintenance_manager()
    if days is not None:
        manager.config.notification_log_retention_days = days
    return await NotificationLogCleanupStrategy().execute(manager.config)


async def vacuum_database() -> None:
    """Run database VACUUM."""
    manager = get_maintenance_manager()
    await manager.vacuum()
