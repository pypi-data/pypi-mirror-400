"""Collaboration service for Phase 5.

Provides business logic for managing comments and activity feeds.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    Activity,
    ActivityAction,
    BaseRepository,
    Comment,
    ResourceType,
)

from .activity import ActivityLogger, ActivityRepository


# =============================================================================
# Repositories
# =============================================================================


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model operations."""

    model = Comment

    async def get_for_resource(
        self,
        resource_type: str,
        resource_id: str,
        *,
        limit: int = 100,
    ) -> list[Comment]:
        """Get comments for a resource.

        Args:
            resource_type: Type of resource.
            resource_id: Resource ID.
            limit: Maximum to return.

        Returns:
            List of root comments (with replies loaded).
        """
        result = await self.session.execute(
            select(Comment)
            .where(Comment.resource_type == resource_type)
            .where(Comment.resource_id == resource_id)
            .where(Comment.parent_id.is_(None))  # Only root comments
            .order_by(Comment.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_for_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> int:
        """Count comments for a resource.

        Args:
            resource_type: Type of resource.
            resource_id: Resource ID.

        Returns:
            Total count including replies.
        """
        return await self.count([
            Comment.resource_type == resource_type,
            Comment.resource_id == resource_id,
        ])


# =============================================================================
# Service
# =============================================================================


class CollaborationService:
    """Service for managing collaboration features.

    Handles comments and activity feeds.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.comment_repo = CommentRepository(session)
        self.activity_repo = ActivityRepository(session)
        self.activity_logger = ActivityLogger(session)

    # =========================================================================
    # Comment Operations
    # =========================================================================

    async def get_comments(
        self,
        resource_type: str,
        resource_id: str,
        *,
        limit: int = 100,
    ) -> tuple[list[Comment], int]:
        """Get comments for a resource.

        Args:
            resource_type: Type of resource.
            resource_id: Resource ID.
            limit: Maximum to return.

        Returns:
            Tuple of (comments, total_count).
        """
        comments = await self.comment_repo.get_for_resource(
            resource_type,
            resource_id,
            limit=limit,
        )
        total = await self.comment_repo.count_for_resource(
            resource_type,
            resource_id,
        )
        return comments, total

    async def get_comment(self, comment_id: str) -> Comment | None:
        """Get comment by ID.

        Args:
            comment_id: Comment ID.

        Returns:
            Comment or None.
        """
        return await self.comment_repo.get_by_id(comment_id)

    async def create_comment(
        self,
        *,
        resource_type: str,
        resource_id: str,
        content: str,
        author_id: str | None = None,
        parent_id: str | None = None,
    ) -> Comment:
        """Create a new comment.

        Args:
            resource_type: Type of resource.
            resource_id: Resource ID.
            content: Comment content.
            author_id: Author identifier.
            parent_id: Parent comment ID for replies.

        Returns:
            Created comment.

        Raises:
            ValueError: If parent comment not found or mismatched resource.
        """
        # Validate parent if provided
        if parent_id:
            parent = await self.comment_repo.get_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent comment '{parent_id}' not found")
            # Ensure reply is on same resource
            if parent.resource_type != resource_type or parent.resource_id != resource_id:
                raise ValueError("Reply must be on the same resource as parent")

        comment = await self.comment_repo.create(
            resource_type=resource_type,
            resource_id=resource_id,
            content=content,
            author_id=author_id,
            parent_id=parent_id,
        )

        await self.activity_logger.log(
            resource_type,
            resource_id,
            ActivityAction.COMMENTED,
            actor_id=author_id,
            description="Added a comment",
            metadata={"comment_id": comment.id},
        )

        return comment

    async def update_comment(
        self,
        comment_id: str,
        *,
        content: str,
        actor_id: str | None = None,
    ) -> Comment | None:
        """Update a comment.

        Args:
            comment_id: Comment ID.
            content: New content.
            actor_id: User updating the comment.

        Returns:
            Updated comment or None.
        """
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            return None

        comment.content = content
        await self.session.flush()
        await self.session.refresh(comment)

        return comment

    async def delete_comment(
        self,
        comment_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete a comment.

        Args:
            comment_id: Comment ID.
            actor_id: User deleting the comment.

        Returns:
            True if deleted.
        """
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False

        resource_type = comment.resource_type
        resource_id = comment.resource_id

        deleted = await self.comment_repo.delete(comment_id)

        if deleted:
            await self.activity_logger.log(
                resource_type,
                resource_id,
                ActivityAction.DELETED,
                actor_id=actor_id,
                description="Deleted a comment",
            )

        return deleted

    # =========================================================================
    # Activity Operations
    # =========================================================================

    async def get_activities(
        self,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        limit: int = 50,
    ) -> list[Activity]:
        """Get activities with optional filters.

        Args:
            resource_type: Filter by resource type.
            resource_id: Filter by resource ID.
            limit: Maximum to return.

        Returns:
            List of activities.
        """
        if resource_type and resource_id:
            return await self.activity_logger.get_for_resource(
                resource_type,
                resource_id,
                limit=limit,
            )
        return await self.activity_logger.get_recent(
            resource_type=resource_type,
            limit=limit,
        )

    async def get_recent_activities(
        self,
        *,
        limit: int = 50,
    ) -> list[Activity]:
        """Get recent activities across all resources.

        Args:
            limit: Maximum to return.

        Returns:
            List of recent activities.
        """
        return await self.activity_logger.get_recent(limit=limit)
