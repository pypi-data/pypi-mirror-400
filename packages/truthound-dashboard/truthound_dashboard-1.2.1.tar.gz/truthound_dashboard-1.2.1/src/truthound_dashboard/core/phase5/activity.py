"""Activity logging service for Phase 5.

Provides centralized activity logging for all Phase 5 operations.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import Activity, ActivityAction, BaseRepository, ResourceType


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity model operations."""

    model = Activity

    async def get_for_resource(
        self,
        resource_type: str,
        resource_id: str,
        *,
        limit: int = 50,
    ) -> list[Activity]:
        """Get activities for a specific resource."""
        result = await self.session.execute(
            select(Activity)
            .where(Activity.resource_type == resource_type)
            .where(Activity.resource_id == resource_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(
        self,
        *,
        resource_type: str | None = None,
        limit: int = 50,
    ) -> list[Activity]:
        """Get recent activities."""
        query = select(Activity).order_by(Activity.created_at.desc()).limit(limit)

        if resource_type:
            query = query.where(Activity.resource_type == resource_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())


class ActivityLogger:
    """Service for logging activities.

    Usage:
        logger = ActivityLogger(session)
        await logger.log(ResourceType.TERM, term_id, ActivityAction.CREATED,
                         description="Created term: Customer ID")
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ActivityRepository(session)

    async def log(
        self,
        resource_type: ResourceType | str,
        resource_id: str,
        action: ActivityAction | str,
        *,
        actor_id: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Activity:
        """Log an activity.

        Args:
            resource_type: Type of resource (term, asset, column, category).
            resource_id: Resource ID.
            action: Action performed (created, updated, deleted, etc).
            actor_id: User who performed the action.
            description: Human-readable description.
            metadata: Additional metadata as JSON.

        Returns:
            Created activity record.
        """
        resource_type_value = (
            resource_type.value
            if isinstance(resource_type, ResourceType)
            else resource_type
        )
        action_value = (
            action.value if isinstance(action, ActivityAction) else action
        )

        return await self.repository.create(
            resource_type=resource_type_value,
            resource_id=resource_id,
            action=action_value,
            actor_id=actor_id,
            description=description,
            metadata=metadata,
        )

    async def get_for_resource(
        self,
        resource_type: ResourceType | str,
        resource_id: str,
        *,
        limit: int = 50,
    ) -> list[Activity]:
        """Get activities for a specific resource."""
        resource_type_value = (
            resource_type.value
            if isinstance(resource_type, ResourceType)
            else resource_type
        )
        return await self.repository.get_for_resource(
            resource_type_value,
            resource_id,
            limit=limit,
        )

    async def get_recent(
        self,
        *,
        resource_type: ResourceType | str | None = None,
        limit: int = 50,
    ) -> list[Activity]:
        """Get recent activities."""
        resource_type_value = None
        if resource_type:
            resource_type_value = (
                resource_type.value
                if isinstance(resource_type, ResourceType)
                else resource_type
            )
        return await self.repository.get_recent(
            resource_type=resource_type_value,
            limit=limit,
        )
