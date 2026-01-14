"""Validation-related Pydantic schemas.

This module defines schemas for validation API operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from .base import BaseSchema, IDMixin, ListResponseWrapper

# Validation status types
ValidationStatus = Literal["pending", "running", "success", "failed", "error"]

# Issue severity types
IssueSeverity = Literal["critical", "high", "medium", "low"]


class ValidationIssue(BaseSchema):
    """Single validation issue.

    Represents one issue found during validation, mapping to
    truthound's ValidationIssue dataclass.
    """

    column: str = Field(..., description="Column where issue was found")
    issue_type: str = Field(
        ..., description="Type of issue", examples=["null_values", "type_mismatch"]
    )
    count: int = Field(..., ge=0, description="Number of occurrences")
    severity: IssueSeverity = Field(..., description="Issue severity level")
    details: str | None = Field(default=None, description="Detailed description")
    expected: Any | None = Field(default=None, description="Expected value/type")
    actual: Any | None = Field(default=None, description="Actual value/type found")
    sample_values: list[Any] | None = Field(
        default=None,
        description="Sample problematic values",
    )


class ValidationRunRequest(BaseSchema):
    """Request to run validation on a source."""

    validators: list[str] | None = Field(
        default=None,
        description="Specific validators to run. If None, all validators are used.",
        examples=[["null", "duplicate", "schema"]],
    )
    schema_path: str | None = Field(
        default=None,
        description="Path to schema YAML file for schema validation",
    )
    auto_schema: bool = Field(
        default=False,
        description="Auto-learn and cache schema for validation",
    )


class ValidationSummary(BaseSchema):
    """Summary statistics for a validation run."""

    passed: bool = Field(..., description="Whether validation passed")
    has_critical: bool = Field(default=False, description="Has critical issues")
    has_high: bool = Field(default=False, description="Has high severity issues")
    total_issues: int = Field(default=0, ge=0, description="Total issue count")
    critical_issues: int = Field(default=0, ge=0, description="Critical issue count")
    high_issues: int = Field(default=0, ge=0, description="High severity issue count")
    medium_issues: int = Field(
        default=0, ge=0, description="Medium severity issue count"
    )
    low_issues: int = Field(default=0, ge=0, description="Low severity issue count")


class ValidationResponse(IDMixin, ValidationSummary):
    """Full validation response with all details."""

    source_id: str = Field(..., description="Source that was validated")
    status: ValidationStatus = Field(..., description="Current validation status")

    # Data statistics
    row_count: int | None = Field(default=None, description="Number of rows validated")
    column_count: int | None = Field(default=None, description="Number of columns")

    # Issues list (full details)
    issues: list[ValidationIssue] = Field(
        default_factory=list,
        description="List of validation issues",
    )

    # Error info (if status is 'error')
    error_message: str | None = Field(
        default=None,
        description="Error message if validation failed",
    )

    # Timing
    duration_ms: int | None = Field(
        default=None,
        ge=0,
        description="Validation duration in milliseconds",
    )
    started_at: datetime | None = Field(default=None, description="Start timestamp")
    completed_at: datetime | None = Field(
        default=None, description="Completion timestamp"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")

    @classmethod
    def from_model(cls, validation: Any) -> ValidationResponse:
        """Create response from model.

        Args:
            validation: Validation model instance.

        Returns:
            ValidationResponse instance.
        """
        issues = []
        if validation.result_json and "issues" in validation.result_json:
            issues = [
                ValidationIssue(**issue) for issue in validation.result_json["issues"]
            ]

        return cls(
            id=validation.id,
            source_id=validation.source_id,
            status=validation.status,
            passed=validation.passed or False,
            has_critical=validation.has_critical or False,
            has_high=validation.has_high or False,
            total_issues=validation.total_issues or 0,
            critical_issues=validation.critical_issues or 0,
            high_issues=validation.high_issues or 0,
            medium_issues=validation.medium_issues or 0,
            low_issues=validation.low_issues or 0,
            row_count=validation.row_count,
            column_count=validation.column_count,
            issues=issues,
            error_message=validation.error_message,
            duration_ms=validation.duration_ms,
            started_at=validation.started_at,
            completed_at=validation.completed_at,
            created_at=validation.created_at,
        )


class ValidationListItem(IDMixin, ValidationSummary):
    """Validation list item (without full issues)."""

    source_id: str
    status: ValidationStatus
    row_count: int | None = None
    column_count: int | None = None
    duration_ms: int | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, validation: Any) -> ValidationListItem:
        """Create list item from model.

        Args:
            validation: Validation model instance.

        Returns:
            ValidationListItem instance.
        """
        return cls(
            id=validation.id,
            source_id=validation.source_id,
            status=validation.status,
            passed=validation.passed or False,
            has_critical=validation.has_critical or False,
            has_high=validation.has_high or False,
            total_issues=validation.total_issues or 0,
            critical_issues=validation.critical_issues or 0,
            high_issues=validation.high_issues or 0,
            medium_issues=validation.medium_issues or 0,
            low_issues=validation.low_issues or 0,
            row_count=validation.row_count,
            column_count=validation.column_count,
            duration_ms=validation.duration_ms,
            created_at=validation.created_at,
        )


class ValidationListResponse(ListResponseWrapper[ValidationListItem]):
    """Paginated validation list response."""

    pass
