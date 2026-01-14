"""Glossary service for Phase 5.

Provides business logic for managing glossary terms, categories,
and relationships with automatic history tracking.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    ActivityAction,
    BaseRepository,
    GlossaryCategory,
    GlossaryTerm,
    ResourceType,
    TermHistory,
    TermRelationship,
    TermStatus,
)

from .activity import ActivityLogger


# =============================================================================
# Repositories
# =============================================================================


class CategoryRepository(BaseRepository[GlossaryCategory]):
    """Repository for GlossaryCategory model operations."""

    model = GlossaryCategory

    async def get_by_name(self, name: str) -> GlossaryCategory | None:
        """Get category by name.

        Args:
            name: Category name.

        Returns:
            Category or None.
        """
        result = await self.session.execute(
            select(GlossaryCategory).where(GlossaryCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def get_root_categories(self, *, limit: int = 100) -> Sequence[GlossaryCategory]:
        """Get root categories (no parent).

        Args:
            limit: Maximum to return.

        Returns:
            Sequence of root categories.
        """
        return await self.list(
            limit=limit,
            filters=[GlossaryCategory.parent_id.is_(None)],
        )


class TermRepository(BaseRepository[GlossaryTerm]):
    """Repository for GlossaryTerm model operations."""

    model = GlossaryTerm

    async def get_by_name(self, name: str) -> GlossaryTerm | None:
        """Get term by name.

        Args:
            name: Term name.

        Returns:
            Term or None.
        """
        result = await self.session.execute(
            select(GlossaryTerm).where(GlossaryTerm.name == name)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        query: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[GlossaryTerm]:
        """Search terms with filters.

        Args:
            query: Search query (name or definition).
            category_id: Filter by category.
            status: Filter by status.
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of matching terms.
        """
        filters = []

        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    GlossaryTerm.name.ilike(search_pattern),
                    GlossaryTerm.definition.ilike(search_pattern),
                )
            )

        if category_id:
            filters.append(GlossaryTerm.category_id == category_id)

        if status:
            filters.append(GlossaryTerm.status == status)

        return await self.list(
            offset=offset,
            limit=limit,
            filters=filters if filters else None,
        )

    async def count_filtered(
        self,
        *,
        query: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
    ) -> int:
        """Count terms matching filters.

        Args:
            query: Search query.
            category_id: Filter by category.
            status: Filter by status.

        Returns:
            Total count.
        """
        filters = []

        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    GlossaryTerm.name.ilike(search_pattern),
                    GlossaryTerm.definition.ilike(search_pattern),
                )
            )

        if category_id:
            filters.append(GlossaryTerm.category_id == category_id)

        if status:
            filters.append(GlossaryTerm.status == status)

        return await self.count(filters if filters else None)


class RelationshipRepository(BaseRepository[TermRelationship]):
    """Repository for TermRelationship model operations."""

    model = TermRelationship

    async def get_for_term(self, term_id: str) -> list[TermRelationship]:
        """Get all relationships for a term.

        Args:
            term_id: Term ID.

        Returns:
            List of relationships.
        """
        result = await self.session.execute(
            select(TermRelationship).where(
                or_(
                    TermRelationship.source_term_id == term_id,
                    TermRelationship.target_term_id == term_id,
                )
            )
        )
        return list(result.scalars().all())

    async def get_existing(
        self,
        source_term_id: str,
        target_term_id: str,
        relationship_type: str,
    ) -> TermRelationship | None:
        """Check if relationship already exists.

        Args:
            source_term_id: Source term ID.
            target_term_id: Target term ID.
            relationship_type: Type of relationship.

        Returns:
            Existing relationship or None.
        """
        result = await self.session.execute(
            select(TermRelationship).where(
                TermRelationship.source_term_id == source_term_id,
                TermRelationship.target_term_id == target_term_id,
                TermRelationship.relationship_type == relationship_type,
            )
        )
        return result.scalar_one_or_none()


class HistoryRepository(BaseRepository[TermHistory]):
    """Repository for TermHistory model operations."""

    model = TermHistory

    async def get_for_term(
        self,
        term_id: str,
        *,
        limit: int = 50,
    ) -> Sequence[TermHistory]:
        """Get history for a term.

        Args:
            term_id: Term ID.
            limit: Maximum to return.

        Returns:
            Sequence of history entries.
        """
        return await self.list(
            limit=limit,
            filters=[TermHistory.term_id == term_id],
            order_by=TermHistory.changed_at.desc(),
        )


# =============================================================================
# Service
# =============================================================================


class GlossaryService:
    """Service for managing business glossary.

    Handles term and category CRUD operations with automatic
    history tracking and activity logging.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.term_repo = TermRepository(session)
        self.relationship_repo = RelationshipRepository(session)
        self.history_repo = HistoryRepository(session)
        self.activity_logger = ActivityLogger(session)

    # =========================================================================
    # Category Operations
    # =========================================================================

    async def list_categories(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[GlossaryCategory], int]:
        """List all categories.

        Args:
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Tuple of (categories, total_count).
        """
        categories = await self.category_repo.list(offset=offset, limit=limit)
        total = await self.category_repo.count()
        return categories, total

    async def get_category(self, category_id: str) -> GlossaryCategory | None:
        """Get category by ID.

        Args:
            category_id: Category ID.

        Returns:
            Category or None.
        """
        return await self.category_repo.get_by_id(category_id)

    async def create_category(
        self,
        *,
        name: str,
        description: str | None = None,
        parent_id: str | None = None,
        actor_id: str | None = None,
    ) -> GlossaryCategory:
        """Create a new category.

        Args:
            name: Category name.
            description: Optional description.
            parent_id: Optional parent category ID.
            actor_id: User creating the category.

        Returns:
            Created category.

        Raises:
            ValueError: If name already exists or parent not found.
        """
        # Check for duplicate name
        existing = await self.category_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Category with name '{name}' already exists")

        # Validate parent if provided
        if parent_id:
            parent = await self.category_repo.get_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent category '{parent_id}' not found")

        category = await self.category_repo.create(
            name=name,
            description=description,
            parent_id=parent_id,
        )

        await self.activity_logger.log(
            ResourceType.CATEGORY,
            category.id,
            ActivityAction.CREATED,
            actor_id=actor_id,
            description=f"Created category: {category.name}",
        )

        return category

    async def update_category(
        self,
        category_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        parent_id: str | None = None,
        actor_id: str | None = None,
    ) -> GlossaryCategory | None:
        """Update a category.

        Args:
            category_id: Category ID.
            name: New name.
            description: New description.
            parent_id: New parent ID.
            actor_id: User updating the category.

        Returns:
            Updated category or None.

        Raises:
            ValueError: If name already exists or parent not found.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return None

        changes = {}

        if name is not None and name != category.name:
            existing = await self.category_repo.get_by_name(name)
            if existing and existing.id != category_id:
                raise ValueError(f"Category with name '{name}' already exists")
            changes["name"] = {"old": category.name, "new": name}
            category.name = name

        if description is not None and description != category.description:
            changes["description"] = {"old": category.description, "new": description}
            category.description = description

        if parent_id is not None and parent_id != category.parent_id:
            if parent_id:
                parent = await self.category_repo.get_by_id(parent_id)
                if not parent:
                    raise ValueError(f"Parent category '{parent_id}' not found")
                # Prevent circular reference
                if parent_id == category_id:
                    raise ValueError("Category cannot be its own parent")
            changes["parent_id"] = {"old": category.parent_id, "new": parent_id}
            category.parent_id = parent_id

        if changes:
            await self.session.flush()
            await self.session.refresh(category)
            await self.activity_logger.log(
                ResourceType.CATEGORY,
                category.id,
                ActivityAction.UPDATED,
                actor_id=actor_id,
                description=f"Updated category: {category.name}",
                metadata={"changes": changes},
            )

        return category

    async def delete_category(
        self,
        category_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete a category.

        Args:
            category_id: Category ID.
            actor_id: User deleting the category.

        Returns:
            True if deleted.
        """
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return False

        category_name = category.name
        deleted = await self.category_repo.delete(category_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.CATEGORY,
                category_id,
                ActivityAction.DELETED,
                actor_id=actor_id,
                description=f"Deleted category: {category_name}",
            )

        return deleted

    # =========================================================================
    # Term Operations
    # =========================================================================

    async def list_terms(
        self,
        *,
        query: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[GlossaryTerm], int]:
        """List terms with filters.

        Args:
            query: Search query.
            category_id: Filter by category.
            status: Filter by status.
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Tuple of (terms, total_count).
        """
        terms = await self.term_repo.search(
            query=query,
            category_id=category_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        total = await self.term_repo.count_filtered(
            query=query,
            category_id=category_id,
            status=status,
        )
        return terms, total

    async def get_term(self, term_id: str) -> GlossaryTerm | None:
        """Get term by ID.

        Args:
            term_id: Term ID.

        Returns:
            Term or None.
        """
        return await self.term_repo.get_by_id(term_id)

    async def create_term(
        self,
        *,
        name: str,
        definition: str,
        category_id: str | None = None,
        status: str = TermStatus.DRAFT.value,
        owner_id: str | None = None,
        actor_id: str | None = None,
    ) -> GlossaryTerm:
        """Create a new term.

        Args:
            name: Term name.
            definition: Term definition.
            category_id: Optional category ID.
            status: Term status.
            owner_id: Owner identifier.
            actor_id: User creating the term.

        Returns:
            Created term.

        Raises:
            ValueError: If name already exists or category not found.
        """
        # Check for duplicate name
        existing = await self.term_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Term with name '{name}' already exists")

        # Validate category if provided
        if category_id:
            category = await self.category_repo.get_by_id(category_id)
            if not category:
                raise ValueError(f"Category '{category_id}' not found")

        term = await self.term_repo.create(
            name=name,
            definition=definition,
            category_id=category_id,
            status=status,
            owner_id=owner_id,
        )

        await self.activity_logger.log(
            ResourceType.TERM,
            term.id,
            ActivityAction.CREATED,
            actor_id=actor_id,
            description=f"Created term: {term.name}",
        )

        return term

    async def update_term(
        self,
        term_id: str,
        *,
        name: str | None = None,
        definition: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        owner_id: str | None = None,
        actor_id: str | None = None,
    ) -> GlossaryTerm | None:
        """Update a term with history tracking.

        Args:
            term_id: Term ID.
            name: New name.
            definition: New definition.
            category_id: New category ID.
            status: New status.
            owner_id: New owner.
            actor_id: User updating the term.

        Returns:
            Updated term or None.

        Raises:
            ValueError: If name already exists or category not found.
        """
        term = await self.term_repo.get_by_id(term_id)
        if not term:
            return None

        changes = {}
        history_entries = []

        if name is not None and name != term.name:
            existing = await self.term_repo.get_by_name(name)
            if existing and existing.id != term_id:
                raise ValueError(f"Term with name '{name}' already exists")
            history_entries.append(("name", term.name, name))
            changes["name"] = {"old": term.name, "new": name}
            term.name = name

        if definition is not None and definition != term.definition:
            history_entries.append(("definition", term.definition, definition))
            changes["definition"] = {"old": term.definition, "new": definition}
            term.definition = definition

        if category_id is not None and category_id != term.category_id:
            if category_id:
                category = await self.category_repo.get_by_id(category_id)
                if not category:
                    raise ValueError(f"Category '{category_id}' not found")
            history_entries.append(("category_id", term.category_id, category_id))
            changes["category_id"] = {"old": term.category_id, "new": category_id}
            term.category_id = category_id

        if status is not None and status != term.status:
            old_status = term.status
            history_entries.append(("status", term.status, status))
            changes["status"] = {"old": term.status, "new": status}
            term.status = status

            await self.activity_logger.log(
                ResourceType.TERM,
                term.id,
                ActivityAction.STATUS_CHANGED,
                actor_id=actor_id,
                description=f"Changed status: {old_status} → {status}",
                metadata={"old_status": old_status, "new_status": status},
            )

        if owner_id is not None and owner_id != term.owner_id:
            history_entries.append(("owner_id", term.owner_id, owner_id))
            changes["owner_id"] = {"old": term.owner_id, "new": owner_id}
            term.owner_id = owner_id

        if history_entries:
            # Record history
            for field_name, old_value, new_value in history_entries:
                await self.history_repo.create(
                    term_id=term_id,
                    field_name=field_name,
                    old_value=str(old_value) if old_value else None,
                    new_value=str(new_value) if new_value else None,
                    changed_by=actor_id,
                )

            await self.session.flush()
            await self.session.refresh(term)

            # Log general update (if not just status change)
            if not (len(changes) == 1 and "status" in changes):
                await self.activity_logger.log(
                    ResourceType.TERM,
                    term.id,
                    ActivityAction.UPDATED,
                    actor_id=actor_id,
                    description=f"Updated term: {term.name}",
                    metadata={"changes": changes},
                )

        return term

    async def delete_term(
        self,
        term_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete a term.

        Args:
            term_id: Term ID.
            actor_id: User deleting the term.

        Returns:
            True if deleted.
        """
        term = await self.term_repo.get_by_id(term_id)
        if not term:
            return False

        term_name = term.name
        deleted = await self.term_repo.delete(term_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.TERM,
                term_id,
                ActivityAction.DELETED,
                actor_id=actor_id,
                description=f"Deleted term: {term_name}",
            )

        return deleted

    async def get_term_history(
        self,
        term_id: str,
        *,
        limit: int = 50,
    ) -> Sequence[TermHistory]:
        """Get history for a term.

        Args:
            term_id: Term ID.
            limit: Maximum to return.

        Returns:
            Sequence of history entries.
        """
        return await self.history_repo.get_for_term(term_id, limit=limit)

    # =========================================================================
    # Relationship Operations
    # =========================================================================

    async def get_term_relationships(
        self,
        term_id: str,
    ) -> list[TermRelationship]:
        """Get all relationships for a term.

        Args:
            term_id: Term ID.

        Returns:
            List of relationships.
        """
        return await self.relationship_repo.get_for_term(term_id)

    async def create_relationship(
        self,
        *,
        source_term_id: str,
        target_term_id: str,
        relationship_type: str,
        actor_id: str | None = None,
    ) -> TermRelationship:
        """Create a relationship between terms.

        Args:
            source_term_id: Source term ID.
            target_term_id: Target term ID.
            relationship_type: Type of relationship.
            actor_id: User creating the relationship.

        Returns:
            Created relationship.

        Raises:
            ValueError: If terms not found or relationship exists.
        """
        # Validate source term
        source_term = await self.term_repo.get_by_id(source_term_id)
        if not source_term:
            raise ValueError(f"Source term '{source_term_id}' not found")

        # Validate target term
        target_term = await self.term_repo.get_by_id(target_term_id)
        if not target_term:
            raise ValueError(f"Target term '{target_term_id}' not found")

        # Check for self-reference
        if source_term_id == target_term_id:
            raise ValueError("Cannot create relationship with same term")

        # Check for existing relationship
        existing = await self.relationship_repo.get_existing(
            source_term_id,
            target_term_id,
            relationship_type,
        )
        if existing:
            raise ValueError("Relationship already exists")

        relationship = await self.relationship_repo.create(
            source_term_id=source_term_id,
            target_term_id=target_term_id,
            relationship_type=relationship_type,
        )

        # Log activity on source term
        await self.activity_logger.log(
            ResourceType.TERM,
            source_term_id,
            "relationship_created",
            actor_id=actor_id,
            description=f"Added {relationship_type} relationship: {source_term.name} → {target_term.name}",
            metadata={
                "relationship_id": relationship.id,
                "relationship_type": relationship_type,
                "target_term_id": target_term_id,
                "target_term_name": target_term.name,
            },
        )

        return relationship

    async def delete_relationship(
        self,
        relationship_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete a relationship.

        Args:
            relationship_id: Relationship ID.
            actor_id: User deleting the relationship.

        Returns:
            True if deleted.
        """
        relationship = await self.relationship_repo.get_by_id(relationship_id)
        if not relationship:
            return False

        source_term_id = relationship.source_term_id
        deleted = await self.relationship_repo.delete(relationship_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.TERM,
                source_term_id,
                "relationship_deleted",
                actor_id=actor_id,
                description="Removed term relationship",
            )

        return deleted
