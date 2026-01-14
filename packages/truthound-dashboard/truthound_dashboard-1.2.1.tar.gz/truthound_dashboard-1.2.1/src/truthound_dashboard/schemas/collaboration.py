"""Pydantic schemas for Collaboration API.

This module defines request/response schemas for comments
and activity logs.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from .base import BaseSchema, IDMixin, ListResponseWrapper, TimestampMixin


# =============================================================================
# Enums
# =============================================================================


class ResourceType(str, Enum):
    """Type of resource for comments and activities."""

    TERM = "term"
    CATEGORY = "category"
    ASSET = "asset"
    COLUMN = "column"


class ActivityAction(str, Enum):
    """Type of activity action."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMMENTED = "commented"
    STATUS_CHANGED = "status_changed"
    MAPPED = "mapped"
    UNMAPPED = "unmapped"


# =============================================================================
# Comment Schemas
# =============================================================================


class CommentBase(BaseSchema):
    """Base schema for comments."""

    content: str = Field(..., min_length=1, max_length=10000, description="Comment content")


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    resource_type: ResourceType = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="ID of the resource")
    parent_id: str | None = Field(None, description="Parent comment ID for replies")
    author_id: str | None = Field(None, description="Author identifier")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content."""
        return v.strip()


class CommentUpdate(BaseSchema):
    """Schema for updating a comment."""

    content: str = Field(..., min_length=1, max_length=10000)


class CommentResponse(BaseSchema, IDMixin, TimestampMixin):
    """Response schema for a comment."""

    resource_type: ResourceType
    resource_id: str
    content: str
    author_id: str | None
    parent_id: str | None
    is_reply: bool = False
    reply_count: int = 0
    replies: list[CommentResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, comment: any, include_replies: bool = True) -> CommentResponse:
        """Create response from model."""
        replies = []
        if include_replies and comment.replies:
            replies = [
                CommentResponse.from_model(r, include_replies=False)
                for r in comment.replies
            ]

        return cls(
            id=comment.id,
            resource_type=ResourceType(comment.resource_type),
            resource_id=comment.resource_id,
            content=comment.content,
            author_id=comment.author_id,
            parent_id=comment.parent_id,
            is_reply=comment.is_reply,
            reply_count=comment.reply_count,
            replies=replies,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )


class CommentListResponse(ListResponseWrapper[CommentResponse]):
    """List of comments."""

    pass


# =============================================================================
# Activity Schemas
# =============================================================================


class ActivityResponse(BaseSchema, IDMixin):
    """Response schema for an activity log entry."""

    resource_type: ResourceType
    resource_id: str
    action: ActivityAction
    actor_id: str | None
    description: str | None
    metadata: dict[str, Any] | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, activity: any) -> ActivityResponse:
        """Create response from model."""
        return cls(
            id=activity.id,
            resource_type=ResourceType(activity.resource_type),
            resource_id=activity.resource_id,
            action=ActivityAction(activity.action),
            actor_id=activity.actor_id,
            description=activity.description,
            metadata=activity.metadata,
            created_at=activity.created_at,
        )


class ActivityListResponse(ListResponseWrapper[ActivityResponse]):
    """List of activities."""

    pass


# =============================================================================
# Activity Create (Internal use)
# =============================================================================


class ActivityCreate(BaseSchema):
    """Schema for creating an activity (internal use)."""

    resource_type: ResourceType
    resource_id: str
    action: ActivityAction
    actor_id: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None
