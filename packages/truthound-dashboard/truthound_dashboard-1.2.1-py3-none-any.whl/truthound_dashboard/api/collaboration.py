"""Collaboration API endpoints.

This module provides REST API endpoints for managing comments
and activity feeds.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from truthound_dashboard.core.phase5 import CollaborationService
from truthound_dashboard.schemas import (
    ActivityListResponse,
    ActivityResponse,
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
    MessageResponse,
)

from .deps import SessionDep

router = APIRouter()


# =============================================================================
# Dependencies
# =============================================================================


async def get_collaboration_service(session: SessionDep) -> CollaborationService:
    """Get collaboration service dependency."""
    return CollaborationService(session)


CollaborationServiceDep = Annotated[CollaborationService, Depends(get_collaboration_service)]


# =============================================================================
# Comment Endpoints
# =============================================================================


@router.get("/comments", response_model=CommentListResponse)
async def get_comments(
    service: CollaborationServiceDep,
    resource_type: Annotated[str, Query(description="Resource type (term, asset, column)")],
    resource_id: Annotated[str, Query(description="Resource ID")],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CommentListResponse:
    """Get comments for a resource.

    - **resource_type**: Type of resource (term, asset, column)
    - **resource_id**: ID of the resource
    """
    comments, total = await service.get_comments(
        resource_type,
        resource_id,
        limit=limit,
    )
    return CommentListResponse(
        data=[CommentResponse.from_model(c) for c in comments],
        total=total,
    )


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    service: CollaborationServiceDep,
    data: CommentCreate,
) -> CommentResponse:
    """Create a new comment."""
    try:
        comment = await service.create_comment(
            resource_type=data.resource_type.value,
            resource_id=data.resource_id,
            content=data.content,
            author_id=data.author_id,
            parent_id=data.parent_id,
        )
        return CommentResponse.from_model(comment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    service: CollaborationServiceDep,
    comment_id: str,
    data: CommentUpdate,
) -> CommentResponse:
    """Update a comment."""
    comment = await service.update_comment(
        comment_id,
        content=data.content,
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment '{comment_id}' not found",
        )
    return CommentResponse.from_model(comment)


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    service: CollaborationServiceDep,
    comment_id: str,
) -> MessageResponse:
    """Delete a comment."""
    deleted = await service.delete_comment(comment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment '{comment_id}' not found",
        )
    return MessageResponse(message="Comment deleted successfully")


# =============================================================================
# Activity Endpoints
# =============================================================================


@router.get("/activities", response_model=ActivityListResponse)
async def get_activities(
    service: CollaborationServiceDep,
    resource_type: Annotated[str | None, Query(description="Filter by resource type")] = None,
    resource_id: Annotated[str | None, Query(description="Filter by resource ID")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ActivityListResponse:
    """Get activity feed.

    - **resource_type**: Optional filter by type (term, asset, column)
    - **resource_id**: Optional filter by resource ID (requires resource_type)
    """
    activities = await service.get_activities(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
    )
    return ActivityListResponse(
        data=[ActivityResponse.from_model(a) for a in activities],
        total=len(activities),
    )
