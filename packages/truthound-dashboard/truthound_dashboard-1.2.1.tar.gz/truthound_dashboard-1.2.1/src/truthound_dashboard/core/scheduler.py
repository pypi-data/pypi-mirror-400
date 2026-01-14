"""Validation scheduler with notification integration.

This module provides scheduled validation execution with automatic
notification dispatch on failures.

The scheduler:
1. Runs scheduled validations based on cron expressions
2. Triggers notifications on validation failures
3. Updates schedule run timestamps
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from truthound_dashboard.db import Schedule, Source, get_session

from .notifications.dispatcher import create_dispatcher
from .services import ValidationService
from .truthound_adapter import get_adapter

logger = logging.getLogger(__name__)


class ValidationScheduler:
    """Scheduler for automated validation runs with notifications.

    Manages scheduled validation jobs using APScheduler and integrates
    with the notification system to alert on failures.

    Usage:
        scheduler = ValidationScheduler()
        await scheduler.start()
        # ... on shutdown ...
        await scheduler.stop()
    """

    def __init__(self) -> None:
        """Initialize the scheduler."""
        self._scheduler = AsyncIOScheduler()
        self._jobs: dict[str, str] = {}  # schedule_id -> job_id mapping

    async def start(self) -> None:
        """Start the scheduler and load existing schedules."""
        logger.info("Starting validation scheduler")
        self._scheduler.start()
        await self._load_schedules()

    async def stop(self) -> None:
        """Stop the scheduler."""
        logger.info("Stopping validation scheduler")
        self._scheduler.shutdown(wait=False)

    async def _load_schedules(self) -> None:
        """Load active schedules from database."""
        async with get_session() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(Schedule).where(Schedule.is_active == True)
            )
            schedules = result.scalars().all()

            for schedule in schedules:
                self.add_schedule(schedule)

    def add_schedule(self, schedule: Schedule) -> None:
        """Add a schedule to the scheduler.

        Args:
            schedule: Schedule model to add.
        """
        if schedule.id in self._jobs:
            self.remove_schedule(schedule.id)

        try:
            trigger = CronTrigger.from_crontab(schedule.cron_expression)
            job = self._scheduler.add_job(
                self._run_validation,
                trigger=trigger,
                args=[schedule.id],
                id=f"schedule_{schedule.id}",
                name=f"Validation: {schedule.name}",
                replace_existing=True,
            )
            self._jobs[schedule.id] = job.id
            logger.info(f"Added schedule: {schedule.name} ({schedule.cron_expression})")
        except Exception as e:
            logger.error(f"Failed to add schedule {schedule.id}: {e}")

    def remove_schedule(self, schedule_id: str) -> None:
        """Remove a schedule from the scheduler.

        Args:
            schedule_id: Schedule ID to remove.
        """
        job_id = self._jobs.pop(schedule_id, None)
        if job_id:
            try:
                self._scheduler.remove_job(job_id)
                logger.info(f"Removed schedule: {schedule_id}")
            except Exception as e:
                logger.error(f"Failed to remove schedule {schedule_id}: {e}")

    def update_schedule(self, schedule: Schedule) -> None:
        """Update a schedule in the scheduler.

        Args:
            schedule: Updated schedule model.
        """
        if schedule.is_active:
            self.add_schedule(schedule)
        else:
            self.remove_schedule(schedule.id)

    async def _run_validation(self, schedule_id: str) -> None:
        """Execute a scheduled validation.

        Args:
            schedule_id: ID of the schedule to run.
        """
        logger.info(f"Running scheduled validation: {schedule_id}")

        async with get_session() as session:
            from sqlalchemy import select

            # Get schedule
            result = await session.execute(
                select(Schedule).where(Schedule.id == schedule_id)
            )
            schedule = result.scalar_one_or_none()

            if schedule is None:
                logger.error(f"Schedule not found: {schedule_id}")
                return

            if not schedule.is_active:
                logger.info(f"Schedule is inactive: {schedule_id}")
                return

            # Get source
            result = await session.execute(
                select(Source).where(Source.id == schedule.source_id)
            )
            source = result.scalar_one_or_none()

            if source is None:
                logger.error(f"Source not found for schedule: {schedule_id}")
                return

            # Run validation
            validation_service = ValidationService(session)
            config = schedule.config or {}

            try:
                validation = await validation_service.run_validation(
                    schedule.source_id,
                    validators=config.get("validators"),
                    schema_path=config.get("schema_path"),
                    auto_schema=config.get("auto_schema", False),
                )

                # Update schedule run time
                schedule.mark_run(self._get_next_run(schedule.cron_expression))
                await session.commit()

                logger.info(
                    f"Validation completed for schedule {schedule_id}: "
                    f"passed={validation.passed}"
                )

                # Send notifications if failed and notifications are enabled
                if schedule.notify_on_failure and not validation.passed:
                    await self._send_failure_notification(
                        session=session,
                        source=source,
                        schedule=schedule,
                        validation=validation,
                    )

            except Exception as e:
                logger.error(f"Validation failed for schedule {schedule_id}: {e}")

                # Send error notification
                if schedule.notify_on_failure:
                    await self._send_error_notification(
                        session=session,
                        source=source,
                        schedule=schedule,
                        error_message=str(e),
                    )

    async def _send_failure_notification(
        self,
        session: Any,
        source: Source,
        schedule: Schedule,
        validation: Any,
    ) -> None:
        """Send notification for validation failure.

        Args:
            session: Database session.
            source: Source that was validated.
            schedule: Schedule that triggered the validation.
            validation: Validation result.
        """
        dispatcher = create_dispatcher(session)

        try:
            results = await dispatcher.notify_schedule_failed(
                source_id=source.id,
                source_name=source.name,
                schedule_id=schedule.id,
                schedule_name=schedule.name,
                validation_id=validation.id,
                error_message=f"Validation failed with {validation.total_issues or 0} issues",
            )
            await session.commit()

            success_count = sum(1 for r in results if r.success)
            logger.info(
                f"Sent {success_count}/{len(results)} failure notifications "
                f"for schedule {schedule.id}"
            )
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")

    async def _send_error_notification(
        self,
        session: Any,
        source: Source,
        schedule: Schedule,
        error_message: str,
    ) -> None:
        """Send notification for validation error.

        Args:
            session: Database session.
            source: Source that was validated.
            schedule: Schedule that triggered the validation.
            error_message: Error message.
        """
        dispatcher = create_dispatcher(session)

        try:
            results = await dispatcher.notify_schedule_failed(
                source_id=source.id,
                source_name=source.name,
                schedule_id=schedule.id,
                schedule_name=schedule.name,
                error_message=error_message,
            )
            await session.commit()

            success_count = sum(1 for r in results if r.success)
            logger.info(
                f"Sent {success_count}/{len(results)} error notifications "
                f"for schedule {schedule.id}"
            )
        except Exception as e:
            logger.error(f"Failed to send error notifications: {e}")

    def _get_next_run(self, cron_expression: str) -> datetime | None:
        """Calculate next run time from cron expression.

        Args:
            cron_expression: Cron expression.

        Returns:
            Next run datetime or None if invalid.
        """
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            return trigger.get_next_fire_time(None, datetime.utcnow())
        except Exception:
            return None


# Singleton instance
_scheduler: ValidationScheduler | None = None


def get_scheduler() -> ValidationScheduler:
    """Get the singleton scheduler instance.

    Returns:
        ValidationScheduler instance.
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ValidationScheduler()
    return _scheduler


async def start_scheduler() -> None:
    """Start the validation scheduler."""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler() -> None:
    """Stop the validation scheduler."""
    scheduler = get_scheduler()
    await scheduler.stop()
