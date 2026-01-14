"""Notification event types.

This module defines specific event types that can trigger notifications.
Each event type contains relevant data for message formatting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .base import NotificationEvent


@dataclass
class ValidationFailedEvent(NotificationEvent):
    """Event triggered when a validation fails.

    Attributes:
        validation_id: ID of the validation run.
        has_critical: Whether critical issues were found.
        has_high: Whether high severity issues were found.
        total_issues: Total number of issues.
        issues: List of issue details.
    """

    event_type: str = field(default="validation_failed", init=False)
    validation_id: str = ""
    has_critical: bool = False
    has_high: bool = False
    total_issues: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)

    @property
    def severity(self) -> str:
        """Get the highest severity level."""
        if self.has_critical:
            return "Critical"
        if self.has_high:
            return "High"
        return "Medium"

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {
                "validation_id": self.validation_id,
                "has_critical": self.has_critical,
                "has_high": self.has_high,
                "total_issues": self.total_issues,
                "severity": self.severity,
            }
        )
        return base


@dataclass
class ScheduleFailedEvent(NotificationEvent):
    """Event triggered when a scheduled validation fails.

    Attributes:
        schedule_id: ID of the schedule.
        schedule_name: Name of the schedule.
        validation_id: ID of the failed validation.
        error_message: Error message if execution failed.
    """

    event_type: str = field(default="schedule_failed", init=False)
    schedule_id: str = ""
    schedule_name: str = ""
    validation_id: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {
                "schedule_id": self.schedule_id,
                "schedule_name": self.schedule_name,
                "validation_id": self.validation_id,
                "error_message": self.error_message,
            }
        )
        return base


@dataclass
class DriftDetectedEvent(NotificationEvent):
    """Event triggered when drift is detected between datasets.

    Attributes:
        comparison_id: ID of the drift comparison.
        baseline_source_id: ID of the baseline source.
        baseline_source_name: Name of the baseline source.
        current_source_id: ID of the current source.
        current_source_name: Name of the current source.
        has_high_drift: Whether high severity drift was detected.
        drifted_columns: Number of columns with drift.
        total_columns: Total columns compared.
    """

    event_type: str = field(default="drift_detected", init=False)
    comparison_id: str = ""
    baseline_source_id: str = ""
    baseline_source_name: str = ""
    current_source_id: str = ""
    current_source_name: str = ""
    has_high_drift: bool = False
    drifted_columns: int = 0
    total_columns: int = 0

    @property
    def drift_percentage(self) -> float:
        """Calculate drift percentage."""
        if self.total_columns > 0:
            return (self.drifted_columns / self.total_columns) * 100
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {
                "comparison_id": self.comparison_id,
                "baseline_source_id": self.baseline_source_id,
                "baseline_source_name": self.baseline_source_name,
                "current_source_id": self.current_source_id,
                "current_source_name": self.current_source_name,
                "has_high_drift": self.has_high_drift,
                "drifted_columns": self.drifted_columns,
                "total_columns": self.total_columns,
                "drift_percentage": round(self.drift_percentage, 2),
            }
        )
        return base


@dataclass
class TestNotificationEvent(NotificationEvent):
    """Event for testing notification channels.

    Used when sending test notifications to verify channel configuration.
    """

    event_type: str = field(default="test", init=False)
    channel_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update({"channel_name": self.channel_name})
        return base
