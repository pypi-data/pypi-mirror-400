"""SQLAlchemy database models.

This module defines all database models for the dashboard.
Models use mixins from base.py for consistent behavior.

Models:
    - Source: Data source configuration
    - Schema: Learned schemas from th.learn
    - Rule: Custom validation rules for sources
    - Validation: Validation run results
    - AppSettings: Application-level settings
    - NotificationChannel: Notification channel configuration
    - NotificationRule: Notification trigger rules
    - NotificationLog: Notification delivery log

Phase 5 Models:
    - GlossaryCategory: Business term categories
    - GlossaryTerm: Business glossary terms
    - TermRelationship: Relationships between terms
    - TermHistory: Term change history
    - CatalogAsset: Data catalog assets
    - AssetColumn: Asset column metadata
    - AssetTag: Asset tags
    - Comment: Comments on resources
    - Activity: Activity log
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


# =============================================================================
# Phase 5: Enums
# =============================================================================


class TermStatus(str, Enum):
    """Status of a glossary term."""

    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class RelationshipType(str, Enum):
    """Type of relationship between terms."""

    SYNONYM = "synonym"
    RELATED = "related"
    PARENT = "parent"
    CHILD = "child"


class AssetType(str, Enum):
    """Type of catalog asset."""

    TABLE = "table"
    FILE = "file"
    API = "api"


class SensitivityLevel(str, Enum):
    """Sensitivity level for data columns."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ResourceType(str, Enum):
    """Type of resource for comments and activities."""

    TERM = "term"
    CATEGORY = "category"
    ASSET = "asset"
    COLUMN = "column"


class ActivityAction(str, Enum):
    """Type of activity action."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMMENTED = "commented"
    STATUS_CHANGED = "status_changed"
    MAPPED = "mapped"
    UNMAPPED = "unmapped"


class Source(Base, UUIDMixin, TimestampMixin):
    """Data source model.

    Represents a data source that can be validated.
    Supports various types: file, postgresql, mysql, snowflake, bigquery.

    Attributes:
        id: Unique identifier (UUID).
        name: Human-readable name for the source.
        type: Source type (file, postgresql, etc.).
        config: JSON configuration specific to source type.
        is_active: Whether the source is active.
        last_validated_at: Timestamp of last validation.
    """

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        if "is_active" not in kwargs:
            kwargs["is_active"] = True
        super().__init__(**kwargs)

    # Relationships
    schemas: Mapped[list[Schema]] = relationship(
        "Schema",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    rules: Mapped[list[Rule]] = relationship(
        "Rule",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Rule.created_at)",
    )
    validations: Mapped[list[Validation]] = relationship(
        "Validation",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Validation.created_at)",
    )
    profiles: Mapped[list[Profile]] = relationship(
        "Profile",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Profile.created_at)",
    )
    schedules: Mapped[list[Schedule]] = relationship(
        "Schedule",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Phase 5: Catalog assets linked to this source
    assets: Mapped[list[CatalogAsset]] = relationship(
        "CatalogAsset",
        back_populates="source",
        lazy="selectin",
    )

    @property
    def source_path(self) -> str | None:
        """Get the data path from config."""
        return self.config.get("path") or self.config.get("connection_string")

    @property
    def latest_schema(self) -> Schema | None:
        """Get the most recent schema."""
        if self.schemas:
            return max(self.schemas, key=lambda s: s.created_at)
        return None

    @property
    def latest_validation(self) -> Validation | None:
        """Get the most recent validation."""
        if self.validations:
            return self.validations[0]
        return None

    @property
    def active_rules(self) -> list[Rule]:
        """Get all active rules for this source."""
        return [r for r in self.rules if r.is_active]

    @property
    def active_rule(self) -> Rule | None:
        """Get the active rule for this source (most recent)."""
        active = self.active_rules
        return active[0] if active else None


class Rule(Base, UUIDMixin, TimestampMixin):
    """Custom validation rules model.

    Stores custom validation rules for data sources in YAML format.
    Rules are used by truthound validators during validation runs.

    Attributes:
        id: Unique identifier (UUID).
        source_id: Reference to parent Source.
        name: Human-readable rule name.
        description: Optional description of the rule.
        rules_yaml: YAML content defining validation rules.
        rules_json: Parsed rules as JSON for programmatic access.
        is_active: Whether this rule set is currently active.
        version: Optional version string for tracking changes.

    Example rules_yaml format:
        columns:
          user_id:
            not_null: true
            unique: true
          email:
            pattern: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
          age:
            min: 0
            max: 150
    """

    __tablename__ = "rules"

    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Default Rules",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    rules_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="rules")

    @property
    def column_rules(self) -> dict[str, Any]:
        """Get column-level rules from JSON."""
        if self.rules_json and "columns" in self.rules_json:
            return self.rules_json["columns"]
        return {}

    @property
    def table_rules(self) -> dict[str, Any]:
        """Get table-level rules from JSON."""
        if self.rules_json and "table" in self.rules_json:
            return self.rules_json["table"]
        return {}

    @property
    def column_count(self) -> int:
        """Get number of columns with rules defined."""
        return len(self.column_rules)

    def deactivate(self) -> None:
        """Mark this rule as inactive."""
        self.is_active = False

    def activate(self) -> None:
        """Mark this rule as active."""
        self.is_active = True


class Schema(Base, UUIDMixin, TimestampMixin):
    """Learned schema model.

    Stores truthound Schema objects (from th.learn) which contain:
    - Column definitions with dtype, nullable, unique, constraints
    - Row count and statistics
    - Version information

    Attributes:
        id: Unique identifier (UUID).
        source_id: Reference to parent Source.
        schema_yaml: YAML representation for display/editing.
        schema_json: Full schema as JSON for programmatic access.
        row_count: Number of rows when schema was learned.
        version: Schema version string.
        is_active: Whether this is the active schema for the source.
    """

    __tablename__ = "schemas"

    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schema_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    schema_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="schemas")

    @property
    def columns(self) -> list[str]:
        """Get list of column names from schema."""
        if self.schema_json and "columns" in self.schema_json:
            return list(self.schema_json["columns"].keys())
        return []


class Validation(Base, UUIDMixin):
    """Validation result model.

    Stores results from th.check validation runs.

    Attributes:
        id: Unique identifier (UUID).
        source_id: Reference to parent Source.
        status: Current status (pending, running, success, failed, error).
        passed: Whether validation passed (no issues).
        has_critical: Whether critical issues were found.
        has_high: Whether high severity issues were found.
        total_issues: Total number of issues found.
        result_json: Full validation result as JSON.
        duration_ms: Validation duration in milliseconds.
    """

    __tablename__ = "validations"

    # Composite index for efficient history queries (source + time ordering)
    __table_args__ = (
        Index("idx_validations_source_created", "source_id", "created_at"),
    )

    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    # Validation results summary
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_critical: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_high: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    total_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)
    critical_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)
    high_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)
    medium_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)
    low_issues: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Data statistics
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Full result and timing
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="validations")

    @property
    def issues(self) -> list[dict[str, Any]]:
        """Get list of issues from result JSON."""
        if self.result_json and "issues" in self.result_json:
            return self.result_json["issues"]
        return []

    @property
    def is_complete(self) -> bool:
        """Check if validation has completed (success, failed, or error)."""
        return self.status in ("success", "failed", "error")

    def mark_started(self) -> None:
        """Mark validation as started."""
        self.status = "running"
        self.started_at = datetime.utcnow()

    def mark_completed(
        self,
        passed: bool,
        result: dict[str, Any],
    ) -> None:
        """Mark validation as completed with results."""
        self.status = "success" if passed else "failed"
        self.passed = passed
        self.result_json = result
        self.completed_at = datetime.utcnow()

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    def mark_error(self, message: str) -> None:
        """Mark validation as errored."""
        self.status = "error"
        self.error_message = message
        self.completed_at = datetime.utcnow()

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)


class Profile(Base, UUIDMixin, TimestampMixin):
    """Data profile model.

    Stores profiling results from th.profile() for historical tracking.

    Attributes:
        id: Unique identifier (UUID).
        source_id: Reference to parent Source.
        profile_json: Full profile result as JSON.
        row_count: Number of rows profiled.
        column_count: Number of columns.
        size_bytes: Data size in bytes.
    """

    __tablename__ = "profiles"

    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    profile_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="profiles")

    @property
    def columns(self) -> list[dict[str, Any]]:
        """Get column profiles from JSON."""
        if self.profile_json and "columns" in self.profile_json:
            return self.profile_json["columns"]
        return []


class Schedule(Base, UUIDMixin, TimestampMixin):
    """Validation schedule model.

    Manages scheduled validation runs using cron expressions.

    Attributes:
        id: Unique identifier (UUID).
        name: Human-readable schedule name.
        source_id: Reference to Source to validate.
        cron_expression: Cron expression for scheduling.
        is_active: Whether schedule is active.
        notify_on_failure: Send notification on validation failure.
        last_run_at: Timestamp of last execution.
        next_run_at: Timestamp of next scheduled run.
        config: Additional configuration (validators, schema_path, etc.).
    """

    __tablename__ = "schedules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_failure: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="schedules")

    def pause(self) -> None:
        """Pause this schedule."""
        self.is_active = False

    def resume(self) -> None:
        """Resume this schedule."""
        self.is_active = True

    def mark_run(self, next_run: datetime | None = None) -> None:
        """Mark schedule as run and update next run time."""
        self.last_run_at = datetime.utcnow()
        self.next_run_at = next_run


class DriftComparison(Base, UUIDMixin, TimestampMixin):
    """Drift comparison result model.

    Stores results from th.compare() drift detection.

    Attributes:
        id: Unique identifier (UUID).
        baseline_source_id: Reference to baseline Source.
        current_source_id: Reference to current Source.
        has_drift: Whether drift was detected.
        has_high_drift: Whether high-severity drift was detected.
        total_columns: Total columns compared.
        drifted_columns: Number of columns with drift.
        result_json: Full comparison result as JSON.
        config: Comparison configuration (method, threshold, etc.).
    """

    __tablename__ = "drift_comparisons"

    baseline_source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    has_drift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_high_drift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_columns: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drifted_columns: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    baseline_source: Mapped[Source] = relationship(
        "Source",
        foreign_keys=[baseline_source_id],
        backref="baseline_comparisons",
    )
    current_source: Mapped[Source] = relationship(
        "Source",
        foreign_keys=[current_source_id],
        backref="current_comparisons",
    )

    @property
    def drift_percentage(self) -> float:
        """Calculate percentage of columns with drift."""
        if self.total_columns and self.total_columns > 0:
            return (self.drifted_columns or 0) / self.total_columns * 100
        return 0.0

    @property
    def column_results(self) -> list[dict[str, Any]]:
        """Get per-column drift results."""
        if self.result_json and "columns" in self.result_json:
            return self.result_json["columns"]
        return []


class AppSettings(Base):
    """Application settings model.

    Stores key-value configuration that can be modified at runtime.

    Attributes:
        key: Setting key (primary key).
        value: JSON value for the setting.
        description: Human-readable description.
    """

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# =============================================================================
# Phase 3: Notification Models
# =============================================================================


class NotificationChannel(Base, UUIDMixin, TimestampMixin):
    """Notification channel configuration model.

    Represents a configured notification channel (Slack, Email, Webhook, etc.).
    Uses a polymorphic pattern where channel-specific configuration is stored
    in the 'config' JSON field.

    Attributes:
        id: Unique identifier (UUID).
        type: Channel type (slack, email, webhook, etc.).
        name: Human-readable channel name.
        config: JSON configuration specific to channel type.
        is_active: Whether channel is active.

    Example configs:
        Slack: {"webhook_url": "https://hooks.slack.com/..."}
        Email: {"smtp_host": "...", "smtp_port": 587, "recipients": [...]}
        Webhook: {"url": "...", "headers": {...}, "method": "POST"}
    """

    __tablename__ = "notification_channels"

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    logs: Mapped[list[NotificationLog]] = relationship(
        "NotificationLog",
        back_populates="channel",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def activate(self) -> None:
        """Activate this channel."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate this channel."""
        self.is_active = False

    def get_config_summary(self) -> str:
        """Get a safe summary of channel configuration (hides sensitive data)."""
        if self.type == "slack":
            url = self.config.get("webhook_url", "")
            return f"Webhook: ...{url[-20:]}" if len(url) > 20 else f"Webhook: {url}"
        elif self.type == "email":
            recipients = self.config.get("recipients", [])
            preview = ", ".join(recipients[:2])
            suffix = "..." if len(recipients) > 2 else ""
            return f"Recipients: {preview}{suffix}"
        elif self.type == "webhook":
            url = self.config.get("url", "")
            return f"URL: {url[:50]}..." if len(url) > 50 else f"URL: {url}"
        return "Configured"


class NotificationRule(Base, UUIDMixin, TimestampMixin):
    """Notification trigger rules model.

    Defines when and how notifications should be triggered based on
    validation events and conditions.

    Attributes:
        id: Unique identifier (UUID).
        name: Human-readable rule name.
        condition: Trigger condition type.
        condition_config: Additional condition configuration.
        channel_ids: List of channel IDs to notify.
        source_ids: Optional list of source IDs to filter (null = all sources).
        is_active: Whether rule is active.

    Condition types:
        - validation_failed: Any validation failure
        - critical_issues: Validation has critical issues
        - high_issues: Validation has high severity issues
        - schedule_failed: Scheduled validation failed
        - drift_detected: Drift detected in comparison
    """

    __tablename__ = "notification_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    condition: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condition_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
    channel_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        """Activate this rule."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate this rule."""
        self.is_active = False

    def matches_source(self, source_id: str) -> bool:
        """Check if this rule applies to a given source.

        Args:
            source_id: Source ID to check.

        Returns:
            True if rule applies to this source.
        """
        if self.source_ids is None:
            return True  # Applies to all sources
        return source_id in self.source_ids


class NotificationLog(Base, UUIDMixin):
    """Notification delivery log model.

    Records all notification delivery attempts for auditing and debugging.

    Attributes:
        id: Unique identifier (UUID).
        channel_id: Reference to NotificationChannel.
        rule_id: Optional reference to NotificationRule that triggered this.
        event_type: Type of event that triggered notification.
        event_data: JSON data about the triggering event.
        status: Delivery status (pending, sent, failed).
        error_message: Error message if delivery failed.
        sent_at: Timestamp when notification was sent.
    """

    __tablename__ = "notification_logs"

    # Composite index for efficient queries
    __table_args__ = (
        Index("idx_notification_logs_channel_created", "channel_id", "created_at"),
        Index("idx_notification_logs_status", "status"),
    )

    channel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("notification_channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("notification_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    channel: Mapped[NotificationChannel] = relationship(
        "NotificationChannel", back_populates="logs"
    )
    rule: Mapped[NotificationRule | None] = relationship(
        "NotificationRule", backref="logs"
    )

    def mark_sent(self) -> None:
        """Mark notification as successfully sent."""
        self.status = "sent"
        self.sent_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark notification as failed with error message."""
        self.status = "failed"
        self.error_message = error
        self.sent_at = datetime.utcnow()


# =============================================================================
# Phase 5: Business Glossary Models
# =============================================================================


class GlossaryCategory(Base, UUIDMixin, TimestampMixin):
    """Business glossary category model.

    Provides hierarchical categorization for business terms.
    Categories can be nested (parent-child relationships).

    Attributes:
        id: Unique identifier (UUID).
        name: Category name (unique).
        description: Optional category description.
        parent_id: Optional parent category ID for hierarchy.
    """

    __tablename__ = "glossary_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("glossary_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    parent: Mapped[GlossaryCategory | None] = relationship(
        "GlossaryCategory",
        remote_side="GlossaryCategory.id",
        back_populates="children",
    )
    children: Mapped[list[GlossaryCategory]] = relationship(
        "GlossaryCategory",
        back_populates="parent",
        lazy="selectin",
    )
    terms: Mapped[list[GlossaryTerm]] = relationship(
        "GlossaryTerm",
        back_populates="category",
        lazy="selectin",
    )

    @property
    def term_count(self) -> int:
        """Get number of terms in this category."""
        return len(self.terms)

    @property
    def full_path(self) -> str:
        """Get full category path (e.g., 'Parent > Child')."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class GlossaryTerm(Base, UUIDMixin, TimestampMixin):
    """Business glossary term model.

    Represents a business term with its definition, status, and relationships.

    Attributes:
        id: Unique identifier (UUID).
        name: Term name (unique).
        definition: Term definition (required).
        category_id: Optional category ID.
        status: Term status (draft, approved, deprecated).
        owner_id: Optional owner identifier.
    """

    __tablename__ = "glossary_terms"

    # Composite index for efficient search queries
    __table_args__ = (
        Index("idx_glossary_terms_name_status", "name", "status"),
        Index("idx_glossary_terms_category", "category_id"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("glossary_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TermStatus.DRAFT.value,
        index=True,
    )
    owner_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    category: Mapped[GlossaryCategory | None] = relationship(
        "GlossaryCategory",
        back_populates="terms",
    )
    history: Mapped[list[TermHistory]] = relationship(
        "TermHistory",
        back_populates="term",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(TermHistory.changed_at)",
    )
    # Relationships where this term is the source
    outgoing_relationships: Mapped[list[TermRelationship]] = relationship(
        "TermRelationship",
        foreign_keys="TermRelationship.source_term_id",
        back_populates="source_term",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Relationships where this term is the target
    incoming_relationships: Mapped[list[TermRelationship]] = relationship(
        "TermRelationship",
        foreign_keys="TermRelationship.target_term_id",
        back_populates="target_term",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Columns mapped to this term
    mapped_columns: Mapped[list[AssetColumn]] = relationship(
        "AssetColumn",
        back_populates="term",
        lazy="selectin",
    )

    @property
    def synonyms(self) -> list[GlossaryTerm]:
        """Get all synonym terms."""
        result = []
        for rel in self.outgoing_relationships:
            if rel.relationship_type == RelationshipType.SYNONYM.value:
                result.append(rel.target_term)
        for rel in self.incoming_relationships:
            if rel.relationship_type == RelationshipType.SYNONYM.value:
                result.append(rel.source_term)
        return result

    @property
    def related_terms(self) -> list[GlossaryTerm]:
        """Get all related terms (non-synonym relationships)."""
        result = []
        for rel in self.outgoing_relationships:
            if rel.relationship_type == RelationshipType.RELATED.value:
                result.append(rel.target_term)
        for rel in self.incoming_relationships:
            if rel.relationship_type == RelationshipType.RELATED.value:
                result.append(rel.source_term)
        return result

    @property
    def is_approved(self) -> bool:
        """Check if term is approved."""
        return self.status == TermStatus.APPROVED.value

    @property
    def is_deprecated(self) -> bool:
        """Check if term is deprecated."""
        return self.status == TermStatus.DEPRECATED.value

    def approve(self) -> None:
        """Approve this term."""
        self.status = TermStatus.APPROVED.value

    def deprecate(self) -> None:
        """Mark this term as deprecated."""
        self.status = TermStatus.DEPRECATED.value


class TermRelationship(Base, UUIDMixin):
    """Relationship between glossary terms.

    Represents directional relationships between terms such as
    synonyms, related terms, or parent-child relationships.

    Attributes:
        id: Unique identifier (UUID).
        source_term_id: Source term ID.
        target_term_id: Target term ID.
        relationship_type: Type of relationship.
        created_at: When the relationship was created.
    """

    __tablename__ = "term_relationships"

    # Unique constraint to prevent duplicate relationships
    __table_args__ = (
        Index(
            "idx_term_relationships_unique",
            "source_term_id",
            "target_term_id",
            "relationship_type",
            unique=True,
        ),
    )

    source_term_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("glossary_terms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_term_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("glossary_terms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    source_term: Mapped[GlossaryTerm] = relationship(
        "GlossaryTerm",
        foreign_keys=[source_term_id],
        back_populates="outgoing_relationships",
    )
    target_term: Mapped[GlossaryTerm] = relationship(
        "GlossaryTerm",
        foreign_keys=[target_term_id],
        back_populates="incoming_relationships",
    )


class TermHistory(Base, UUIDMixin):
    """History of changes to glossary terms.

    Tracks all modifications to term fields for auditing.

    Attributes:
        id: Unique identifier (UUID).
        term_id: Reference to the term.
        field_name: Name of the changed field.
        old_value: Previous value (as string).
        new_value: New value (as string).
        changed_by: User who made the change.
        changed_at: When the change occurred.
    """

    __tablename__ = "term_history"

    # Index for efficient history queries
    __table_args__ = (
        Index("idx_term_history_term_changed", "term_id", "changed_at"),
    )

    term_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("glossary_terms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    term: Mapped[GlossaryTerm] = relationship(
        "GlossaryTerm",
        back_populates="history",
    )


# =============================================================================
# Phase 5: Data Catalog Models
# =============================================================================


class CatalogAsset(Base, UUIDMixin, TimestampMixin):
    """Data catalog asset model.

    Represents a data asset (table, file, API) in the catalog.

    Attributes:
        id: Unique identifier (UUID).
        name: Asset name.
        asset_type: Type of asset (table, file, api).
        source_id: Optional reference to data source.
        description: Optional asset description.
        owner_id: Optional owner identifier.
        quality_score: Computed quality score (0-100).
    """

    __tablename__ = "catalog_assets"

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_catalog_assets_type", "asset_type"),
        Index("idx_catalog_assets_source", "source_id"),
        Index("idx_catalog_assets_name_type", "name", "asset_type"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AssetType.TABLE.value,
    )
    source_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    source: Mapped[Source | None] = relationship(
        "Source",
        back_populates="assets",
    )
    columns: Mapped[list[AssetColumn]] = relationship(
        "AssetColumn",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AssetColumn.name",
    )
    tags: Mapped[list[AssetTag]] = relationship(
        "AssetTag",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def column_count(self) -> int:
        """Get number of columns."""
        return len(self.columns)

    @property
    def tag_names(self) -> list[str]:
        """Get list of tag names."""
        return [tag.tag_name for tag in self.tags]

    @property
    def quality_level(self) -> str:
        """Get quality level based on score."""
        if self.quality_score is None:
            return "unknown"
        if self.quality_score >= 90:
            return "excellent"
        if self.quality_score >= 70:
            return "good"
        if self.quality_score >= 50:
            return "fair"
        return "poor"

    def update_quality_score(self, score: float) -> None:
        """Update the quality score."""
        self.quality_score = min(100.0, max(0.0, score))


class AssetColumn(Base, UUIDMixin, TimestampMixin):
    """Asset column metadata model.

    Represents a column within a data asset with optional term mapping.

    Attributes:
        id: Unique identifier (UUID).
        asset_id: Reference to parent asset.
        name: Column name.
        data_type: Column data type.
        description: Optional column description.
        is_nullable: Whether column allows null values.
        is_primary_key: Whether column is a primary key.
        term_id: Optional mapped glossary term ID.
        sensitivity_level: Data sensitivity classification.
    """

    __tablename__ = "asset_columns"

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_asset_columns_asset", "asset_id"),
        Index("idx_asset_columns_term", "term_id"),
        Index("idx_asset_columns_sensitivity", "sensitivity_level"),
    )

    asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("catalog_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_nullable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    term_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("glossary_terms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sensitivity_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=SensitivityLevel.PUBLIC.value,
    )

    # Relationships
    asset: Mapped[CatalogAsset] = relationship(
        "CatalogAsset",
        back_populates="columns",
    )
    term: Mapped[GlossaryTerm | None] = relationship(
        "GlossaryTerm",
        back_populates="mapped_columns",
    )

    @property
    def is_sensitive(self) -> bool:
        """Check if column contains sensitive data."""
        if self.sensitivity_level is None:
            return False
        return self.sensitivity_level in (
            SensitivityLevel.CONFIDENTIAL.value,
            SensitivityLevel.RESTRICTED.value,
        )

    @property
    def has_term_mapping(self) -> bool:
        """Check if column is mapped to a term."""
        return self.term_id is not None

    def map_to_term(self, term_id: str) -> None:
        """Map this column to a glossary term."""
        self.term_id = term_id

    def unmap_term(self) -> None:
        """Remove term mapping from this column."""
        self.term_id = None


class AssetTag(Base, UUIDMixin):
    """Tag for catalog assets.

    Provides flexible tagging for assets with optional values.

    Attributes:
        id: Unique identifier (UUID).
        asset_id: Reference to parent asset.
        tag_name: Tag name/key.
        tag_value: Optional tag value.
        created_at: When the tag was created.
    """

    __tablename__ = "asset_tags"

    # Unique constraint to prevent duplicate tags
    __table_args__ = (
        Index("idx_asset_tags_asset", "asset_id"),
        Index("idx_asset_tags_name", "tag_name"),
        Index(
            "idx_asset_tags_unique",
            "asset_id",
            "tag_name",
            unique=True,
        ),
    )

    asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("catalog_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    asset: Mapped[CatalogAsset] = relationship(
        "CatalogAsset",
        back_populates="tags",
    )


# =============================================================================
# Phase 5: Collaboration Models
# =============================================================================


class Comment(Base, UUIDMixin, TimestampMixin):
    """Comment on resources (terms, assets, columns).

    Supports threaded comments with replies.

    Attributes:
        id: Unique identifier (UUID).
        resource_type: Type of resource being commented on.
        resource_id: ID of the resource.
        content: Comment content.
        author_id: Optional author identifier.
        parent_id: Optional parent comment ID for replies.
    """

    __tablename__ = "comments"

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_comments_resource", "resource_type", "resource_id"),
        Index("idx_comments_parent", "parent_id"),
    )

    resource_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    parent: Mapped[Comment | None] = relationship(
        "Comment",
        remote_side="Comment.id",
        back_populates="replies",
    )
    replies: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Comment.created_at",
    )

    @property
    def is_reply(self) -> bool:
        """Check if this is a reply to another comment."""
        return self.parent_id is not None

    @property
    def reply_count(self) -> int:
        """Get number of direct replies."""
        return len(self.replies)


class Activity(Base, UUIDMixin):
    """Activity log for tracking changes.

    Records all significant actions on resources for audit trail.

    Attributes:
        id: Unique identifier (UUID).
        resource_type: Type of resource.
        resource_id: ID of the resource.
        action: Type of action performed.
        actor_id: User who performed the action.
        description: Human-readable description.
        metadata: Additional action metadata as JSON.
        created_at: When the activity occurred.
    """

    __tablename__ = "activities"

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_activities_resource", "resource_type", "resource_id"),
        Index("idx_activities_action", "action"),
        Index("idx_activities_created", "created_at"),
    )

    resource_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    @property
    def resource_key(self) -> str:
        """Get unique resource key."""
        return f"{self.resource_type}:{self.resource_id}"
