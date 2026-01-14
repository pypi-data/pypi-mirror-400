"""Source-related Pydantic schemas.

This module defines schemas for data source API operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from .base import BaseSchema, IDMixin, ListResponseWrapper, TimestampMixin

# Supported source types
SourceType = Literal["file", "postgresql", "mysql", "snowflake", "bigquery"]


class SourceBase(BaseSchema):
    """Base source schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable source name",
        examples=["Sales Data", "User Events"],
    )
    type: SourceType = Field(
        ...,
        description="Data source type",
        examples=["file", "postgresql"],
    )
    config: dict[str, Any] = Field(
        ...,
        description="Source-specific configuration",
        examples=[{"path": "/data/sales.csv"}],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional source description",
    )


class SourceCreate(SourceBase):
    """Schema for creating a new source."""

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate configuration has required fields."""
        if not v:
            raise ValueError("Config cannot be empty")
        return v


class SourceUpdate(BaseSchema):
    """Schema for updating an existing source."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New source name",
    )
    config: dict[str, Any] | None = Field(
        default=None,
        description="New source configuration",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="New description",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether source is active",
    )


class SourceResponse(SourceBase, IDMixin, TimestampMixin):
    """Schema for source responses."""

    is_active: bool = Field(default=True, description="Whether source is active")
    last_validated_at: datetime | None = Field(
        default=None,
        description="Last validation timestamp",
    )

    # Computed properties from relationships
    has_schema: bool = Field(default=False, description="Whether schema exists")
    latest_validation_status: str | None = Field(
        default=None,
        description="Status of latest validation",
    )

    @classmethod
    def from_model(cls, source: Any) -> SourceResponse:
        """Create response from model with computed fields.

        Args:
            source: Source model instance.

        Returns:
            SourceResponse with computed fields.
        """
        return cls(
            id=source.id,
            name=source.name,
            type=source.type,
            config=source.config,
            description=source.description,
            is_active=source.is_active,
            created_at=source.created_at,
            updated_at=source.updated_at,
            last_validated_at=source.last_validated_at,
            has_schema=source.latest_schema is not None,
            latest_validation_status=(
                source.latest_validation.status if source.latest_validation else None
            ),
        )


class SourceListResponse(ListResponseWrapper[SourceResponse]):
    """Paginated source list response."""

    pass


class SourceSummary(BaseSchema):
    """Minimal source summary for lists."""

    id: str
    name: str
    type: SourceType
    is_active: bool
    last_validated_at: datetime | None = None
