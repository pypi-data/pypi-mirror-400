"""Profile-related Pydantic schemas.

This module defines schemas for data profiling API operations.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import BaseSchema


class ColumnProfile(BaseSchema):
    """Profile information for a single column."""

    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type")
    null_pct: str = Field(default="0%", description="Percentage of null values")
    unique_pct: str = Field(default="0%", description="Percentage of unique values")
    min: Any | None = Field(default=None, description="Minimum value")
    max: Any | None = Field(default=None, description="Maximum value")
    mean: float | None = Field(default=None, description="Mean value (numeric columns)")
    std: float | None = Field(default=None, description="Standard deviation (numeric)")

    # Additional statistics (optional)
    distinct_count: int | None = Field(
        default=None,
        description="Count of distinct values",
    )
    most_common: list[dict[str, Any]] | None = Field(
        default=None,
        description="Most common values with counts",
    )


class ProfileResponse(BaseSchema):
    """Data profiling response."""

    source: str = Field(..., description="Source path/identifier")
    row_count: int = Field(..., ge=0, description="Total number of rows")
    column_count: int = Field(..., ge=0, description="Total number of columns")
    size_bytes: int = Field(..., ge=0, description="Data size in bytes")
    columns: list[ColumnProfile] = Field(
        default_factory=list,
        description="Profile for each column",
    )

    # Computed properties
    @property
    def size_human(self) -> str:
        """Get human-readable size."""
        size = self.size_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    @classmethod
    def from_result(cls, result: Any) -> ProfileResponse:
        """Create response from adapter result.

        Args:
            result: ProfileResult from adapter.

        Returns:
            ProfileResponse instance.
        """
        columns = [
            ColumnProfile(
                name=col["name"],
                dtype=col["dtype"],
                null_pct=col.get("null_pct", "0%"),
                unique_pct=col.get("unique_pct", "0%"),
                min=col.get("min"),
                max=col.get("max"),
                mean=col.get("mean"),
                std=col.get("std"),
            )
            for col in result.columns
        ]

        return cls(
            source=result.source,
            row_count=result.row_count,
            column_count=result.column_count,
            size_bytes=result.size_bytes,
            columns=columns,
        )
