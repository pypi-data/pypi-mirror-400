"""Base classes for core services.

This module provides abstract base classes and protocols for
implementing core business logic services with consistent patterns.

The service pattern separates business logic from API handlers,
enabling better testability and reusability.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db.repository import BaseRepository

# Type variables
ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT")
UpdateSchemaT = TypeVar("UpdateSchemaT")
ResponseSchemaT = TypeVar("ResponseSchemaT")


class BaseService(ABC, Generic[ModelT]):
    """Abstract base class for services.

    Services encapsulate business logic and orchestrate
    operations between repositories and external systems.

    Type Parameters:
        ModelT: The model type this service manages.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session.

        Args:
            session: Async database session.
        """
        self.session = session

    @abstractmethod
    async def get_by_id(self, id: str) -> ModelT | None:
        """Get entity by ID."""
        ...

    @abstractmethod
    async def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelT]:
        """List entities with pagination."""
        ...


class CRUDService(BaseService[ModelT], Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """Base service with full CRUD operations.

    Extends BaseService with create, update, and delete operations.

    Type Parameters:
        ModelT: The model type.
        CreateSchemaT: Pydantic schema for creation.
        UpdateSchemaT: Pydantic schema for updates.
    """

    repository_class: type[BaseRepository[ModelT]]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.repository = self.repository_class(session)

    async def get_by_id(self, id: str) -> ModelT | None:
        """Get entity by ID.

        Args:
            id: Entity's unique identifier.

        Returns:
            Model instance or None if not found.
        """
        return await self.repository.get_by_id(id)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> list[ModelT]:
        """List entities with pagination and filtering.

        Args:
            offset: Number of records to skip.
            limit: Maximum records to return.
            **filters: Additional filter criteria.

        Returns:
            List of model instances.
        """
        filter_conditions = self._build_filters(**filters)
        result = await self.repository.list(
            offset=offset,
            limit=limit,
            filters=filter_conditions,
        )
        return list(result)

    async def create(self, data: CreateSchemaT) -> ModelT:
        """Create new entity.

        Args:
            data: Pydantic schema with creation data.

        Returns:
            Created model instance.
        """
        create_data = self._prepare_create_data(data)
        return await self.repository.create(**create_data)

    async def update(self, id: str, data: UpdateSchemaT) -> ModelT | None:
        """Update existing entity.

        Args:
            id: Entity's unique identifier.
            data: Pydantic schema with update data.

        Returns:
            Updated model instance or None if not found.
        """
        update_data = self._prepare_update_data(data)
        return await self.repository.update(id, **update_data)

    async def delete(self, id: str) -> bool:
        """Delete entity by ID.

        Args:
            id: Entity's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        return await self.repository.delete(id)

    def _prepare_create_data(self, data: CreateSchemaT) -> dict[str, Any]:
        """Prepare data for creation.

        Override to customize creation data processing.

        Args:
            data: Pydantic schema with creation data.

        Returns:
            Dictionary of field values.
        """
        if hasattr(data, "model_dump"):
            return data.model_dump(exclude_unset=True)  # type: ignore
        return dict(data)  # type: ignore

    def _prepare_update_data(self, data: UpdateSchemaT) -> dict[str, Any]:
        """Prepare data for update.

        Override to customize update data processing.

        Args:
            data: Pydantic schema with update data.

        Returns:
            Dictionary of field values (excluding None).
        """
        if hasattr(data, "model_dump"):
            return data.model_dump(exclude_unset=True, exclude_none=True)  # type: ignore
        return {k: v for k, v in dict(data).items() if v is not None}  # type: ignore

    def _build_filters(self, **_filters: Any) -> list[Any]:
        """Build SQLAlchemy filter conditions.

        Override to customize filter building.

        Args:
            **filters: Filter criteria.

        Returns:
            List of SQLAlchemy filter conditions.
        """
        return []
