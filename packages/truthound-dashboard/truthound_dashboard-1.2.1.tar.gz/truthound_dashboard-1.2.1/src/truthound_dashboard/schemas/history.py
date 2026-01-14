"""History and analytics schemas.

Schemas for validation history and trend analysis.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TrendDataPoint(BaseModel):
    """Single data point in trend analysis."""

    date: str = Field(..., description="Date string (format depends on granularity)")
    success_rate: float = Field(
        ..., ge=0, le=100, description="Success rate percentage"
    )
    run_count: int = Field(..., ge=0, description="Number of validation runs")
    passed_count: int = Field(..., ge=0, description="Number of passed validations")
    failed_count: int = Field(..., ge=0, description="Number of failed validations")


class FailureFrequencyItem(BaseModel):
    """Failure frequency for an issue type."""

    issue: str = Field(..., description="Issue identifier (column.issue_type)")
    count: int = Field(..., ge=0, description="Total occurrence count")


class RecentValidation(BaseModel):
    """Summary of a recent validation run."""

    id: str = Field(..., description="Validation ID")
    status: str = Field(..., description="Validation status")
    passed: bool | None = Field(None, description="Whether validation passed")
    has_critical: bool | None = Field(None, description="Has critical issues")
    has_high: bool | None = Field(None, description="Has high severity issues")
    total_issues: int | None = Field(None, description="Total issue count")
    created_at: str = Field(..., description="ISO timestamp")


class HistorySummary(BaseModel):
    """Summary statistics for the history period."""

    total_runs: int = Field(..., ge=0, description="Total validation runs")
    passed_runs: int = Field(..., ge=0, description="Number of passed runs")
    failed_runs: int = Field(..., ge=0, description="Number of failed runs")
    success_rate: float = Field(
        ..., ge=0, le=100, description="Success rate percentage"
    )


class HistoryResponse(BaseModel):
    """Validation history response with trends and analytics."""

    summary: HistorySummary = Field(..., description="Summary statistics")
    trend: list[TrendDataPoint] = Field(default_factory=list, description="Trend data")
    failure_frequency: list[FailureFrequencyItem] = Field(
        default_factory=list, description="Top failure types"
    )
    recent_validations: list[RecentValidation] = Field(
        default_factory=list, description="Recent validation runs"
    )


class HistoryQueryParams(BaseModel):
    """Query parameters for history endpoint."""

    period: Literal["7d", "30d", "90d"] = Field("30d", description="Time period")
    granularity: Literal["hourly", "daily", "weekly"] = Field(
        "daily", description="Aggregation granularity"
    )
