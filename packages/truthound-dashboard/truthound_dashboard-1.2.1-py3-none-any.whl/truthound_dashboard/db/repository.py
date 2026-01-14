"""Generic repository pattern for database operations.

This module provides a generic repository base class that implements
common CRUD operations, reducing boilerplate in API endpoints.

Example:
    class SourceRepository(BaseRepository[Source]):
        pass

    async with get_session() as session:
        repo = SourceRepository(session)
        source = await repo.get_by_id("uuid-here")
        sources = await repo.list(limit=10)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from .base import Base

# Type variable for model classes
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository providing common CRUD operations.

    This class implements the repository pattern for database access,
    providing a clean abstraction over SQLAlchemy operations.

    Type Parameters:
        ModelT: The SQLAlchemy model class this repository manages.

    Attributes:
        session: The async database session.
        model: The model class for this repository.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async database session for operations.
        """
        self.session = session

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Set model class from generic type argument."""
        super().__init_subclass__(**kwargs)
        # Get the model type from Generic parameters
        for base in cls.__orig_bases__:  # type: ignore
            if hasattr(base, "__args__"):
                cls.model = base.__args__[0]
                break

    async def get_by_id(self, id: str) -> ModelT | None:
        """Get a single record by ID.

        Args:
            id: The record's primary key.

        Returns:
            The model instance or None if not found.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, id: str) -> ModelT:
        """Get a single record by ID, raising if not found.

        Args:
            id: The record's primary key.

        Returns:
            The model instance.

        Raises:
            ValueError: If record not found.
        """
        record = await self.get_by_id(id)
        if record is None:
            raise ValueError(f"{self.model.__name__} with id '{id}' not found")
        return record

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Any = None,
        filters: list[Any] | None = None,
    ) -> Sequence[ModelT]:
        """List records with pagination and filtering.

        Args:
            offset: Number of records to skip.
            limit: Maximum records to return.
            order_by: Column(s) to order by.
            filters: List of SQLAlchemy filter conditions.

        Returns:
            Sequence of model instances.
        """
        query = self._build_query(filters)

        if order_by is not None:
            query = query.order_by(order_by)
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self, filters: list[Any] | None = None) -> int:
        """Count records matching filters.

        Args:
            filters: List of SQLAlchemy filter conditions.

        Returns:
            Total count of matching records.
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelT:
        """Create a new record.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            The created model instance.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: str, **kwargs: Any) -> ModelT | None:
        """Update a record by ID.

        Args:
            id: The record's primary key.
            **kwargs: Field values to update.

        Returns:
            The updated model instance or None if not found.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: str) -> bool:
        """Delete a record by ID.

        Args:
            id: The record's primary key.

        Returns:
            True if deleted, False if not found.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def bulk_create(self, items: list[dict[str, Any]]) -> list[ModelT]:
        """Create multiple records at once.

        Args:
            items: List of dictionaries with field values.

        Returns:
            List of created model instances.
        """
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def exists(self, id: str) -> bool:
        """Check if a record exists.

        Args:
            id: The record's primary key.

        Returns:
            True if exists, False otherwise.
        """
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    def _build_query(self, filters: list[Any] | None = None) -> Select:
        """Build base query with filters.

        Args:
            filters: List of SQLAlchemy filter conditions.

        Returns:
            Select query with filters applied.
        """
        query = select(self.model)
        if filters:
            for f in filters:
                query = query.where(f)
        return query
