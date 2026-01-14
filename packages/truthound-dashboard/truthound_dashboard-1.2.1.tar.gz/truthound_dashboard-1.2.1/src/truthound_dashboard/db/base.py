"""Database base classes and mixins for extensibility.

This module provides reusable base classes and mixins for SQLAlchemy models,
enabling consistent patterns across all database entities.

Example:
    class MyModel(Base, TimestampMixin, UUIDMixin):
        __tablename__ = "my_models"
        name: Mapped[str] = mapped_column(String(255))
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides common functionality like automatic table naming
    and serialization methods.
    """

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        import re

        name = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower() + "s"

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class UUIDMixin:
    """Mixin that adds a UUID primary key.

    Automatically generates a UUID4 string as the primary key.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps.

    Automatically sets created_at on insert and updates
    updated_at on every modification.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality.

    Instead of actually deleting records, sets deleted_at timestamp.
    Use with query filters to exclude deleted records.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft-deleted record."""
        self.deleted_at = None
