"""Base Pydantic schemas and mixins.

This module provides reusable base classes and mixins for Pydantic schemas,
enabling consistent patterns across all API schemas.

The schema classes follow a consistent naming convention:
- *Base: Common fields shared by create/update/response
- *Create: Fields for creation (POST)
- *Update: Fields for updates (PUT/PATCH)
- *Response: Fields returned in responses
- *ListResponse: Paginated list response wrapper
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Type variable for generic response wrappers
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration.

    All schemas should inherit from this base class to ensure
    consistent behavior and serialization.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={"example": {}},
    )


class TimestampMixin:
    """Mixin for timestamp fields in responses."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class IDMixin:
    """Mixin for ID field in responses."""

    id: str = Field(..., description="Unique identifier")


class ResponseWrapper(BaseSchema, Generic[T]):
    """Generic wrapper for single item responses.

    Provides consistent structure for API responses.
    """

    success: bool = Field(default=True, description="Whether request succeeded")
    data: T = Field(..., description="Response data")
    message: str | None = Field(default=None, description="Optional message")


class ListResponseWrapper(BaseSchema, Generic[T]):
    """Generic wrapper for list responses with pagination.

    Provides consistent structure for paginated API responses.
    """

    success: bool = Field(default=True, description="Whether request succeeded")
    data: list[T] = Field(default_factory=list, description="List of items")
    total: int = Field(default=0, description="Total count of items")
    offset: int = Field(default=0, description="Offset for pagination")
    limit: int = Field(default=100, description="Limit for pagination")

    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        return self.offset + len(self.data) < self.total


class ErrorResponse(BaseSchema):
    """Standard error response schema."""

    success: bool = Field(default=False)
    detail: str = Field(..., description="Error description")
    code: str | None = Field(default=None, description="Error code")
    errors: list[dict[str, Any]] | None = Field(
        default=None, description="Validation errors"
    )


class MessageResponse(BaseSchema):
    """Simple message response schema."""

    success: bool = Field(default=True)
    message: str = Field(..., description="Response message")
