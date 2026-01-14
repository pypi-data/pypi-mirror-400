"""Rule-related Pydantic schemas.

This module defines schemas for custom validation rules API operations.
"""

from __future__ import annotations

from typing import Any

import yaml
from pydantic import Field, field_validator

from .base import BaseSchema, IDMixin, ListResponseWrapper, TimestampMixin


class RuleBase(BaseSchema):
    """Base rule schema with common fields."""

    name: str = Field(
        default="Default Rules",
        min_length=1,
        max_length=255,
        description="Human-readable rule name",
        examples=["Email Validation Rules", "User Data Constraints"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional description of the rules",
    )
    rules_yaml: str = Field(
        ...,
        min_length=1,
        description="YAML content defining validation rules",
        examples=[
            """columns:
  user_id:
    not_null: true
    unique: true
  email:
    pattern: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
"""
        ],
    )


class RuleCreate(RuleBase):
    """Schema for creating a new rule."""

    @field_validator("rules_yaml")
    @classmethod
    def validate_yaml(cls, v: str) -> str:
        """Validate YAML syntax."""
        try:
            yaml.safe_load(v)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        return v


class RuleUpdate(BaseSchema):
    """Schema for updating an existing rule."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New rule name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="New description",
    )
    rules_yaml: str | None = Field(
        default=None,
        min_length=1,
        description="New YAML rules content",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether rule is active",
    )
    version: str | None = Field(
        default=None,
        max_length=50,
        description="Version string for tracking changes",
    )

    @field_validator("rules_yaml")
    @classmethod
    def validate_yaml(cls, v: str | None) -> str | None:
        """Validate YAML syntax if provided."""
        if v is not None:
            try:
                yaml.safe_load(v)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML syntax: {e}")
        return v


class ColumnRuleInfo(BaseSchema):
    """Information about a single column's rules."""

    name: str = Field(..., description="Column name")
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints applied to this column",
    )


class RuleResponse(RuleBase, IDMixin, TimestampMixin):
    """Schema for rule responses."""

    source_id: str = Field(..., description="Source this rule belongs to")
    is_active: bool = Field(default=True, description="Whether rule is active")
    version: str | None = Field(default=None, description="Rule version")

    # Computed from rules_json
    rules_json: dict[str, Any] | None = Field(
        default=None,
        description="Parsed rules as JSON",
    )
    column_count: int = Field(
        default=0,
        description="Number of columns with rules",
    )

    @classmethod
    def from_model(cls, rule: Any) -> RuleResponse:
        """Create response from model with computed fields.

        Args:
            rule: Rule model instance.

        Returns:
            RuleResponse with computed fields.
        """
        return cls(
            id=rule.id,
            source_id=rule.source_id,
            name=rule.name,
            description=rule.description,
            rules_yaml=rule.rules_yaml,
            rules_json=rule.rules_json,
            is_active=rule.is_active,
            version=rule.version,
            column_count=rule.column_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )


class RuleListItem(BaseSchema, IDMixin, TimestampMixin):
    """Rule list item (without full YAML content)."""

    source_id: str
    name: str
    description: str | None = None
    is_active: bool = True
    version: str | None = None
    column_count: int = 0

    @classmethod
    def from_model(cls, rule: Any) -> RuleListItem:
        """Create list item from model.

        Args:
            rule: Rule model instance.

        Returns:
            RuleListItem instance.
        """
        return cls(
            id=rule.id,
            source_id=rule.source_id,
            name=rule.name,
            description=rule.description,
            is_active=rule.is_active,
            version=rule.version,
            column_count=rule.column_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )


class RuleListResponse(ListResponseWrapper[RuleListItem]):
    """Paginated rule list response."""

    pass


class RuleSummary(BaseSchema):
    """Minimal rule summary for embedded responses."""

    id: str
    name: str
    is_active: bool = True
    column_count: int = 0
