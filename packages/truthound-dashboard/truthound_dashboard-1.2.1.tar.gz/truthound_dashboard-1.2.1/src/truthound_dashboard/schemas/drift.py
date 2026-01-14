"""Drift detection schemas.

Schemas for drift comparison request/response.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .base import IDMixin, TimestampMixin


class DriftCompareRequest(BaseModel):
    """Request body for drift comparison."""

    baseline_source_id: str = Field(..., description="Baseline source ID")
    current_source_id: str = Field(..., description="Current source ID to compare")
    columns: list[str] | None = Field(
        None, description="Columns to compare (None = all)"
    )
    method: Literal["auto", "ks", "psi", "chi2", "js"] = Field(
        "auto", description="Drift detection method"
    )
    threshold: float | None = Field(None, ge=0, le=1, description="Custom threshold")
    sample_size: int | None = Field(
        None, ge=100, description="Sample size for large datasets"
    )


class ColumnDriftResult(BaseModel):
    """Drift result for a single column."""

    column: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type")
    drifted: bool = Field(..., description="Whether drift was detected")
    level: str = Field(..., description="Drift level (high, medium, low, none)")
    method: str = Field(..., description="Detection method used")
    statistic: float | None = Field(None, description="Test statistic value")
    p_value: float | None = Field(None, description="P-value")
    baseline_stats: dict[str, Any] = Field(
        default_factory=dict, description="Baseline statistics"
    )
    current_stats: dict[str, Any] = Field(
        default_factory=dict, description="Current statistics"
    )


class DriftResult(BaseModel):
    """Full drift comparison result."""

    baseline_source: str = Field(..., description="Baseline source path")
    current_source: str = Field(..., description="Current source path")
    baseline_rows: int = Field(..., description="Number of baseline rows")
    current_rows: int = Field(..., description="Number of current rows")
    has_drift: bool = Field(..., description="Whether any drift was detected")
    has_high_drift: bool = Field(
        ..., description="Whether high-severity drift was detected"
    )
    total_columns: int = Field(..., description="Total columns compared")
    drifted_columns: list[str] = Field(
        default_factory=list, description="Columns with drift"
    )
    columns: list[ColumnDriftResult] = Field(
        default_factory=list, description="Per-column results"
    )


class DriftSourceSummary(BaseModel):
    """Summary of a source in drift comparison."""

    id: str = Field(..., description="Source ID")
    name: str = Field(..., description="Source name")


class DriftComparisonResponse(BaseModel, IDMixin, TimestampMixin):
    """Response for drift comparison."""

    baseline_source_id: str = Field(..., description="Baseline source ID")
    current_source_id: str = Field(..., description="Current source ID")
    has_drift: bool = Field(..., description="Whether drift was detected")
    has_high_drift: bool = Field(
        ..., description="Whether high-severity drift was detected"
    )
    total_columns: int | None = Field(None, description="Total columns compared")
    drifted_columns: int | None = Field(
        None, description="Number of columns with drift"
    )
    drift_percentage: float = Field(0, description="Percentage of columns with drift")
    result: DriftResult | None = Field(None, description="Full drift result")
    config: dict[str, Any] | None = Field(None, description="Comparison configuration")

    # Optional source details
    baseline: DriftSourceSummary | None = Field(
        None, description="Baseline source info"
    )
    current: DriftSourceSummary | None = Field(None, description="Current source info")


class DriftComparisonListItem(BaseModel, IDMixin, TimestampMixin):
    """List item for drift comparisons."""

    baseline_source_id: str
    current_source_id: str
    has_drift: bool
    has_high_drift: bool
    total_columns: int | None = None
    drifted_columns: int | None = None
    drift_percentage: float = 0


class DriftComparisonListResponse(BaseModel):
    """List response for drift comparisons."""

    success: bool = True
    data: list[DriftComparisonListItem] = Field(default_factory=list)
    total: int = 0
