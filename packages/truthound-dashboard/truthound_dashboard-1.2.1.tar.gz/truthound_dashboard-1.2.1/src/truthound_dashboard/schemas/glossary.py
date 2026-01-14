"""Pydantic schemas for Business Glossary API.

This module defines request/response schemas for glossary terms,
categories, and relationships.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from .base import BaseSchema, IDMixin, ListResponseWrapper, TimestampMixin


# =============================================================================
# Enums
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


# =============================================================================
# Category Schemas
# =============================================================================


class CategoryBase(BaseSchema):
    """Base schema for glossary categories."""

    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    description: str | None = Field(None, description="Category description")
    parent_id: str | None = Field(None, description="Parent category ID")


class CategoryCreate(CategoryBase):
    """Schema for creating a glossary category."""

    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating a glossary category."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    parent_id: str | None = None


class CategorySummary(BaseSchema, IDMixin):
    """Summary schema for category references."""

    name: str
    full_path: str | None = None


class CategoryResponse(BaseSchema, IDMixin, TimestampMixin):
    """Response schema for a glossary category."""

    name: str
    description: str | None
    parent_id: str | None
    parent: CategorySummary | None = None
    term_count: int = 0
    full_path: str

    @classmethod
    def from_model(cls, category: any) -> CategoryResponse:
        """Create response from model."""
        parent_summary = None
        if category.parent:
            parent_summary = CategorySummary(
                id=category.parent.id,
                name=category.parent.name,
                full_path=category.parent.full_path,
            )
        return cls(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            parent=parent_summary,
            term_count=category.term_count,
            full_path=category.full_path,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )


class CategoryListResponse(ListResponseWrapper[CategoryResponse]):
    """Paginated list of categories."""

    pass


# =============================================================================
# Term Schemas
# =============================================================================


class TermBase(BaseSchema):
    """Base schema for glossary terms."""

    name: str = Field(..., min_length=1, max_length=255, description="Term name")
    definition: str = Field(..., min_length=1, description="Term definition")
    category_id: str | None = Field(None, description="Category ID")
    status: TermStatus = Field(default=TermStatus.DRAFT, description="Term status")
    owner_id: str | None = Field(None, description="Owner identifier")


class TermCreate(TermBase):
    """Schema for creating a glossary term."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate term name."""
        return v.strip()

    @field_validator("definition")
    @classmethod
    def validate_definition(cls, v: str) -> str:
        """Validate term definition."""
        return v.strip()


class TermUpdate(BaseSchema):
    """Schema for updating a glossary term."""

    name: str | None = Field(None, min_length=1, max_length=255)
    definition: str | None = Field(None, min_length=1)
    category_id: str | None = None
    status: TermStatus | None = None
    owner_id: str | None = None


class TermSummary(BaseSchema, IDMixin):
    """Summary schema for term references."""

    name: str
    status: TermStatus


class RelatedTermSummary(BaseSchema, IDMixin):
    """Summary for related terms with relationship type."""

    name: str
    status: TermStatus
    relationship_type: RelationshipType


class TermResponse(BaseSchema, IDMixin, TimestampMixin):
    """Response schema for a glossary term."""

    name: str
    definition: str
    category_id: str | None
    category: CategorySummary | None = None
    status: TermStatus
    owner_id: str | None
    synonyms: list[TermSummary] = Field(default_factory=list)
    related_terms: list[TermSummary] = Field(default_factory=list)
    mapped_column_count: int = 0

    @classmethod
    def from_model(cls, term: any) -> TermResponse:
        """Create response from model."""
        category_summary = None
        if term.category:
            category_summary = CategorySummary(
                id=term.category.id,
                name=term.category.name,
                full_path=term.category.full_path,
            )

        synonyms = [
            TermSummary(id=t.id, name=t.name, status=TermStatus(t.status))
            for t in term.synonyms
        ]

        related = [
            TermSummary(id=t.id, name=t.name, status=TermStatus(t.status))
            for t in term.related_terms
        ]

        return cls(
            id=term.id,
            name=term.name,
            definition=term.definition,
            category_id=term.category_id,
            category=category_summary,
            status=TermStatus(term.status),
            owner_id=term.owner_id,
            synonyms=synonyms,
            related_terms=related,
            mapped_column_count=len(term.mapped_columns),
            created_at=term.created_at,
            updated_at=term.updated_at,
        )


class TermListItem(BaseSchema, IDMixin, TimestampMixin):
    """List item schema for terms (lighter than full response)."""

    name: str
    definition: str
    category_id: str | None
    category_name: str | None = None
    status: TermStatus
    owner_id: str | None
    synonym_count: int = 0
    related_count: int = 0

    @classmethod
    def from_model(cls, term: any) -> TermListItem:
        """Create list item from model."""
        return cls(
            id=term.id,
            name=term.name,
            definition=term.definition,
            category_id=term.category_id,
            category_name=term.category.name if term.category else None,
            status=TermStatus(term.status),
            owner_id=term.owner_id,
            synonym_count=len(term.synonyms),
            related_count=len(term.related_terms),
            created_at=term.created_at,
            updated_at=term.updated_at,
        )


class TermListResponse(ListResponseWrapper[TermListItem]):
    """Paginated list of terms."""

    pass


# =============================================================================
# Relationship Schemas
# =============================================================================


class RelationshipBase(BaseSchema):
    """Base schema for term relationships."""

    source_term_id: str = Field(..., description="Source term ID")
    target_term_id: str = Field(..., description="Target term ID")
    relationship_type: RelationshipType = Field(..., description="Relationship type")


class RelationshipCreate(RelationshipBase):
    """Schema for creating a term relationship."""

    @field_validator("target_term_id")
    @classmethod
    def validate_different_terms(cls, v: str, info) -> str:
        """Validate that source and target are different."""
        if info.data.get("source_term_id") == v:
            raise ValueError("Source and target terms must be different")
        return v


class RelationshipResponse(BaseSchema, IDMixin):
    """Response schema for a term relationship."""

    source_term_id: str
    target_term_id: str
    source_term: TermSummary
    target_term: TermSummary
    relationship_type: RelationshipType
    created_at: datetime

    @classmethod
    def from_model(cls, rel: any) -> RelationshipResponse:
        """Create response from model."""
        return cls(
            id=rel.id,
            source_term_id=rel.source_term_id,
            target_term_id=rel.target_term_id,
            source_term=TermSummary(
                id=rel.source_term.id,
                name=rel.source_term.name,
                status=TermStatus(rel.source_term.status),
            ),
            target_term=TermSummary(
                id=rel.target_term.id,
                name=rel.target_term.name,
                status=TermStatus(rel.target_term.status),
            ),
            relationship_type=RelationshipType(rel.relationship_type),
            created_at=rel.created_at,
        )


class RelationshipListResponse(ListResponseWrapper[RelationshipResponse]):
    """List of relationships."""

    pass


# =============================================================================
# History Schemas
# =============================================================================


class TermHistoryResponse(BaseSchema, IDMixin):
    """Response schema for term change history."""

    term_id: str
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_by: str | None
    changed_at: datetime

    @classmethod
    def from_model(cls, history: any) -> TermHistoryResponse:
        """Create response from model."""
        return cls(
            id=history.id,
            term_id=history.term_id,
            field_name=history.field_name,
            old_value=history.old_value,
            new_value=history.new_value,
            changed_by=history.changed_by,
            changed_at=history.changed_at,
        )


class TermHistoryListResponse(ListResponseWrapper[TermHistoryResponse]):
    """List of term history entries."""

    pass
