"""Schema-related Pydantic schemas.

This module defines schemas for learned schema API operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from .base import BaseSchema, IDMixin, TimestampMixin


class ColumnSchema(BaseSchema):
    """Schema for a single column."""

    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type")
    nullable: bool = Field(default=True, description="Whether nulls are allowed")
    unique: bool = Field(default=False, description="Whether values must be unique")
    min_value: Any | None = Field(default=None, description="Minimum value constraint")
    max_value: Any | None = Field(default=None, description="Maximum value constraint")
    allowed_values: list[Any] | None = Field(
        default=None,
        description="List of allowed values",
    )
    pattern: str | None = Field(default=None, description="Regex pattern constraint")
    min_length: int | None = Field(default=None, description="Minimum string length")
    max_length: int | None = Field(default=None, description="Maximum string length")

    # Statistics
    null_ratio: float | None = Field(default=None, description="Ratio of null values")
    unique_ratio: float | None = Field(
        default=None, description="Ratio of unique values"
    )
    mean: float | None = Field(default=None, description="Mean value (numeric)")
    std: float | None = Field(default=None, description="Standard deviation (numeric)")


class SchemaLearnRequest(BaseSchema):
    """Request to learn schema from source."""

    infer_constraints: bool = Field(
        default=True,
        description="Infer constraints from data statistics",
    )


class SchemaUpdateRequest(BaseSchema):
    """Request to update schema YAML."""

    schema_yaml: str = Field(
        ...,
        min_length=1,
        description="Updated schema in YAML format",
    )


class SchemaResponse(BaseSchema, IDMixin, TimestampMixin):
    """Full schema response."""

    source_id: str = Field(..., description="Parent source ID")
    schema_yaml: str = Field(..., description="Schema in YAML format")
    schema_json: dict[str, Any] | None = Field(
        default=None,
        description="Schema as JSON object",
    )
    row_count: int | None = Field(
        default=None,
        description="Row count when schema was learned",
    )
    column_count: int | None = Field(
        default=None,
        description="Number of columns in schema",
    )
    columns: list[str] = Field(
        default_factory=list,
        description="List of column names",
    )
    version: str | None = Field(default=None, description="Schema version")
    is_active: bool = Field(default=True, description="Whether this schema is active")

    @classmethod
    def from_model(cls, schema: Any) -> SchemaResponse:
        """Create response from model.

        Args:
            schema: Schema model instance.

        Returns:
            SchemaResponse instance.
        """
        columns = []
        if schema.schema_json and "columns" in schema.schema_json:
            columns = list(schema.schema_json["columns"].keys())

        return cls(
            id=schema.id,
            source_id=schema.source_id,
            schema_yaml=schema.schema_yaml,
            schema_json=schema.schema_json,
            row_count=schema.row_count,
            column_count=schema.column_count,
            columns=columns,
            version=schema.version,
            is_active=schema.is_active,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
        )


class SchemaSummary(IDMixin):
    """Minimal schema summary."""

    source_id: str
    column_count: int | None = None
    row_count: int | None = None
    is_active: bool = True
    created_at: datetime
