"""Pydantic schemas for Data Catalog API.

This module defines request/response schemas for catalog assets,
columns, and tags.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from .base import BaseSchema, IDMixin, ListResponseWrapper, TimestampMixin
from .glossary import TermSummary


# =============================================================================
# Enums
# =============================================================================


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


class QualityLevel(str, Enum):
    """Quality level based on score."""

    UNKNOWN = "unknown"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


# =============================================================================
# Tag Schemas
# =============================================================================


class TagBase(BaseSchema):
    """Base schema for asset tags."""

    tag_name: str = Field(..., min_length=1, max_length=100, description="Tag name")
    tag_value: str | None = Field(None, max_length=255, description="Tag value")


class TagCreate(TagBase):
    """Schema for creating an asset tag."""

    @field_validator("tag_name")
    @classmethod
    def validate_tag_name(cls, v: str) -> str:
        """Validate and normalize tag name."""
        return v.strip().lower()


class TagResponse(BaseSchema, IDMixin):
    """Response schema for an asset tag."""

    tag_name: str
    tag_value: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, tag: any) -> TagResponse:
        """Create response from model."""
        return cls(
            id=tag.id,
            tag_name=tag.tag_name,
            tag_value=tag.tag_value,
            created_at=tag.created_at,
        )


# =============================================================================
# Column Schemas
# =============================================================================


class ColumnBase(BaseSchema):
    """Base schema for asset columns."""

    name: str = Field(..., min_length=1, max_length=255, description="Column name")
    data_type: str | None = Field(None, max_length=100, description="Data type")
    description: str | None = Field(None, description="Column description")
    is_nullable: bool = Field(default=True, description="Whether column allows nulls")
    is_primary_key: bool = Field(default=False, description="Whether column is PK")
    sensitivity_level: SensitivityLevel | None = Field(
        default=SensitivityLevel.PUBLIC,
        description="Data sensitivity level",
    )


class ColumnCreate(ColumnBase):
    """Schema for creating an asset column."""

    pass


class ColumnUpdate(BaseSchema):
    """Schema for updating an asset column."""

    name: str | None = Field(None, min_length=1, max_length=255)
    data_type: str | None = None
    description: str | None = None
    is_nullable: bool | None = None
    is_primary_key: bool | None = None
    sensitivity_level: SensitivityLevel | None = None


class ColumnTermMapping(BaseSchema):
    """Schema for mapping a column to a glossary term."""

    term_id: str = Field(..., description="Glossary term ID to map")


class ColumnResponse(BaseSchema, IDMixin, TimestampMixin):
    """Response schema for an asset column."""

    asset_id: str
    name: str
    data_type: str | None
    description: str | None
    is_nullable: bool
    is_primary_key: bool
    term_id: str | None
    term: TermSummary | None = None
    sensitivity_level: SensitivityLevel | None
    is_sensitive: bool = False
    has_term_mapping: bool = False

    @classmethod
    def from_model(cls, column: any) -> ColumnResponse:
        """Create response from model."""
        from .glossary import TermStatus

        term_summary = None
        if column.term:
            term_summary = TermSummary(
                id=column.term.id,
                name=column.term.name,
                status=TermStatus(column.term.status),
            )

        sensitivity = None
        if column.sensitivity_level:
            sensitivity = SensitivityLevel(column.sensitivity_level)

        return cls(
            id=column.id,
            asset_id=column.asset_id,
            name=column.name,
            data_type=column.data_type,
            description=column.description,
            is_nullable=column.is_nullable,
            is_primary_key=column.is_primary_key,
            term_id=column.term_id,
            term=term_summary,
            sensitivity_level=sensitivity,
            is_sensitive=column.is_sensitive,
            has_term_mapping=column.has_term_mapping,
            created_at=column.created_at,
            updated_at=column.updated_at,
        )


class ColumnListResponse(ListResponseWrapper[ColumnResponse]):
    """List of columns."""

    pass


# =============================================================================
# Asset Schemas
# =============================================================================


class SourceSummary(BaseSchema, IDMixin):
    """Summary schema for data source references."""

    name: str
    type: str


class AssetBase(BaseSchema):
    """Base schema for catalog assets."""

    name: str = Field(..., min_length=1, max_length=255, description="Asset name")
    asset_type: AssetType = Field(
        default=AssetType.TABLE,
        description="Asset type",
    )
    source_id: str | None = Field(None, description="Linked data source ID")
    description: str | None = Field(None, description="Asset description")
    owner_id: str | None = Field(None, description="Owner identifier")


class AssetCreate(AssetBase):
    """Schema for creating a catalog asset."""

    columns: list[ColumnCreate] = Field(
        default_factory=list,
        description="Initial columns to create",
    )
    tags: list[TagCreate] = Field(
        default_factory=list,
        description="Initial tags to add",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate asset name."""
        return v.strip()


class AssetUpdate(BaseSchema):
    """Schema for updating a catalog asset."""

    name: str | None = Field(None, min_length=1, max_length=255)
    asset_type: AssetType | None = None
    source_id: str | None = None
    description: str | None = None
    owner_id: str | None = None
    quality_score: float | None = Field(None, ge=0, le=100)


class AssetResponse(BaseSchema, IDMixin, TimestampMixin):
    """Response schema for a catalog asset."""

    name: str
    asset_type: AssetType
    source_id: str | None
    source: SourceSummary | None = None
    description: str | None
    owner_id: str | None
    quality_score: float | None
    quality_level: QualityLevel = QualityLevel.UNKNOWN
    column_count: int = 0
    columns: list[ColumnResponse] = Field(default_factory=list)
    tags: list[TagResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, asset: any, include_columns: bool = True) -> AssetResponse:
        """Create response from model."""
        source_summary = None
        if asset.source:
            source_summary = SourceSummary(
                id=asset.source.id,
                name=asset.source.name,
                type=asset.source.type,
            )

        columns = []
        if include_columns:
            columns = [ColumnResponse.from_model(c) for c in asset.columns]

        tags = [TagResponse.from_model(t) for t in asset.tags]

        quality_level = QualityLevel.UNKNOWN
        if asset.quality_score is not None:
            if asset.quality_score >= 90:
                quality_level = QualityLevel.EXCELLENT
            elif asset.quality_score >= 70:
                quality_level = QualityLevel.GOOD
            elif asset.quality_score >= 50:
                quality_level = QualityLevel.FAIR
            else:
                quality_level = QualityLevel.POOR

        return cls(
            id=asset.id,
            name=asset.name,
            asset_type=AssetType(asset.asset_type),
            source_id=asset.source_id,
            source=source_summary,
            description=asset.description,
            owner_id=asset.owner_id,
            quality_score=asset.quality_score,
            quality_level=quality_level,
            column_count=asset.column_count,
            columns=columns,
            tags=tags,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )


class AssetListItem(BaseSchema, IDMixin, TimestampMixin):
    """List item schema for assets (lighter than full response)."""

    name: str
    asset_type: AssetType
    source_id: str | None
    source_name: str | None = None
    description: str | None
    owner_id: str | None
    quality_score: float | None
    quality_level: QualityLevel = QualityLevel.UNKNOWN
    column_count: int = 0
    tag_names: list[str] = Field(default_factory=list)

    @classmethod
    def from_model(cls, asset: any) -> AssetListItem:
        """Create list item from model."""
        quality_level = QualityLevel.UNKNOWN
        if asset.quality_score is not None:
            if asset.quality_score >= 90:
                quality_level = QualityLevel.EXCELLENT
            elif asset.quality_score >= 70:
                quality_level = QualityLevel.GOOD
            elif asset.quality_score >= 50:
                quality_level = QualityLevel.FAIR
            else:
                quality_level = QualityLevel.POOR

        return cls(
            id=asset.id,
            name=asset.name,
            asset_type=AssetType(asset.asset_type),
            source_id=asset.source_id,
            source_name=asset.source.name if asset.source else None,
            description=asset.description,
            owner_id=asset.owner_id,
            quality_score=asset.quality_score,
            quality_level=quality_level,
            column_count=asset.column_count,
            tag_names=asset.tag_names,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )


class AssetListResponse(ListResponseWrapper[AssetListItem]):
    """Paginated list of assets."""

    pass
