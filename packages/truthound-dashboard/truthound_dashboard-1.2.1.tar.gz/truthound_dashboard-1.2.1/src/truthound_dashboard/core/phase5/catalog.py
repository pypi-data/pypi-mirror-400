"""Catalog service for Phase 5.

Provides business logic for managing data catalog assets,
columns, and tags.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.db import (
    ActivityAction,
    AssetColumn,
    AssetTag,
    AssetType,
    BaseRepository,
    CatalogAsset,
    GlossaryTerm,
    ResourceType,
    Source,
)

from .activity import ActivityLogger


# =============================================================================
# Repositories
# =============================================================================


class AssetRepository(BaseRepository[CatalogAsset]):
    """Repository for CatalogAsset model operations."""

    model = CatalogAsset

    async def search(
        self,
        *,
        query: str | None = None,
        asset_type: str | None = None,
        source_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[CatalogAsset]:
        """Search assets with filters.

        Args:
            query: Search query (name or description).
            asset_type: Filter by asset type.
            source_id: Filter by data source.
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Sequence of matching assets.
        """
        filters = []

        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    CatalogAsset.name.ilike(search_pattern),
                    CatalogAsset.description.ilike(search_pattern),
                )
            )

        if asset_type:
            filters.append(CatalogAsset.asset_type == asset_type)

        if source_id:
            filters.append(CatalogAsset.source_id == source_id)

        return await self.list(
            offset=offset,
            limit=limit,
            filters=filters if filters else None,
        )

    async def count_filtered(
        self,
        *,
        query: str | None = None,
        asset_type: str | None = None,
        source_id: str | None = None,
    ) -> int:
        """Count assets matching filters.

        Args:
            query: Search query.
            asset_type: Filter by asset type.
            source_id: Filter by data source.

        Returns:
            Total count.
        """
        filters = []

        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    CatalogAsset.name.ilike(search_pattern),
                    CatalogAsset.description.ilike(search_pattern),
                )
            )

        if asset_type:
            filters.append(CatalogAsset.asset_type == asset_type)

        if source_id:
            filters.append(CatalogAsset.source_id == source_id)

        return await self.count(filters if filters else None)

    async def get_by_source(
        self,
        source_id: str,
        *,
        limit: int = 100,
    ) -> Sequence[CatalogAsset]:
        """Get assets for a data source.

        Args:
            source_id: Data source ID.
            limit: Maximum to return.

        Returns:
            Sequence of assets.
        """
        return await self.list(
            limit=limit,
            filters=[CatalogAsset.source_id == source_id],
        )


class ColumnRepository(BaseRepository[AssetColumn]):
    """Repository for AssetColumn model operations."""

    model = AssetColumn

    async def get_for_asset(
        self,
        asset_id: str,
        *,
        limit: int = 500,
    ) -> Sequence[AssetColumn]:
        """Get columns for an asset.

        Args:
            asset_id: Asset ID.
            limit: Maximum to return.

        Returns:
            Sequence of columns.
        """
        return await self.list(
            limit=limit,
            filters=[AssetColumn.asset_id == asset_id],
            order_by=AssetColumn.name,
        )

    async def get_by_term(
        self,
        term_id: str,
        *,
        limit: int = 100,
    ) -> Sequence[AssetColumn]:
        """Get columns mapped to a term.

        Args:
            term_id: Term ID.
            limit: Maximum to return.

        Returns:
            Sequence of columns.
        """
        return await self.list(
            limit=limit,
            filters=[AssetColumn.term_id == term_id],
        )


class TagRepository(BaseRepository[AssetTag]):
    """Repository for AssetTag model operations."""

    model = AssetTag

    async def get_for_asset(
        self,
        asset_id: str,
    ) -> list[AssetTag]:
        """Get tags for an asset.

        Args:
            asset_id: Asset ID.

        Returns:
            List of tags.
        """
        result = await self.session.execute(
            select(AssetTag)
            .where(AssetTag.asset_id == asset_id)
            .order_by(AssetTag.tag_name)
        )
        return list(result.scalars().all())

    async def get_existing(
        self,
        asset_id: str,
        tag_name: str,
    ) -> AssetTag | None:
        """Get existing tag by name.

        Args:
            asset_id: Asset ID.
            tag_name: Tag name.

        Returns:
            Existing tag or None.
        """
        result = await self.session.execute(
            select(AssetTag).where(
                AssetTag.asset_id == asset_id,
                AssetTag.tag_name == tag_name,
            )
        )
        return result.scalar_one_or_none()


# =============================================================================
# Service
# =============================================================================


class CatalogService:
    """Service for managing data catalog.

    Handles asset, column, and tag CRUD operations
    with activity logging.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session
        self.asset_repo = AssetRepository(session)
        self.column_repo = ColumnRepository(session)
        self.tag_repo = TagRepository(session)
        self.activity_logger = ActivityLogger(session)

    # =========================================================================
    # Asset Operations
    # =========================================================================

    async def list_assets(
        self,
        *,
        query: str | None = None,
        asset_type: str | None = None,
        source_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[CatalogAsset], int]:
        """List assets with filters.

        Args:
            query: Search query.
            asset_type: Filter by type.
            source_id: Filter by data source.
            offset: Number to skip.
            limit: Maximum to return.

        Returns:
            Tuple of (assets, total_count).
        """
        assets = await self.asset_repo.search(
            query=query,
            asset_type=asset_type,
            source_id=source_id,
            offset=offset,
            limit=limit,
        )
        total = await self.asset_repo.count_filtered(
            query=query,
            asset_type=asset_type,
            source_id=source_id,
        )
        return assets, total

    async def get_asset(self, asset_id: str) -> CatalogAsset | None:
        """Get asset by ID.

        Args:
            asset_id: Asset ID.

        Returns:
            Asset or None.
        """
        return await self.asset_repo.get_by_id(asset_id)

    async def create_asset(
        self,
        *,
        name: str,
        asset_type: str = AssetType.TABLE.value,
        source_id: str | None = None,
        description: str | None = None,
        owner_id: str | None = None,
        columns: list[dict[str, Any]] | None = None,
        tags: list[dict[str, Any]] | None = None,
        actor_id: str | None = None,
    ) -> CatalogAsset:
        """Create a new asset.

        Args:
            name: Asset name.
            asset_type: Type of asset.
            source_id: Optional data source ID.
            description: Optional description.
            owner_id: Owner identifier.
            columns: Initial columns to create.
            tags: Initial tags to add.
            actor_id: User creating the asset.

        Returns:
            Created asset.

        Raises:
            ValueError: If source not found.
        """
        # Validate source if provided
        if source_id:
            result = await self.session.execute(
                select(Source).where(Source.id == source_id)
            )
            source = result.scalar_one_or_none()
            if not source:
                raise ValueError(f"Data source '{source_id}' not found")

        asset = await self.asset_repo.create(
            name=name,
            asset_type=asset_type,
            source_id=source_id,
            description=description,
            owner_id=owner_id,
        )

        # Create initial columns
        if columns:
            for col_data in columns:
                await self.column_repo.create(
                    asset_id=asset.id,
                    **col_data,
                )

        # Create initial tags
        if tags:
            for tag_data in tags:
                await self.tag_repo.create(
                    asset_id=asset.id,
                    **tag_data,
                )

        await self.session.flush()
        await self.session.refresh(asset)

        await self.activity_logger.log(
            ResourceType.ASSET,
            asset.id,
            ActivityAction.CREATED,
            actor_id=actor_id,
            description=f"Created asset: {asset.name}",
        )

        return asset

    async def update_asset(
        self,
        asset_id: str,
        *,
        name: str | None = None,
        asset_type: str | None = None,
        source_id: str | None = None,
        description: str | None = None,
        owner_id: str | None = None,
        quality_score: float | None = None,
        actor_id: str | None = None,
    ) -> CatalogAsset | None:
        """Update an asset.

        Args:
            asset_id: Asset ID.
            name: New name.
            asset_type: New type.
            source_id: New source ID.
            description: New description.
            owner_id: New owner.
            quality_score: New quality score.
            actor_id: User updating the asset.

        Returns:
            Updated asset or None.

        Raises:
            ValueError: If source not found.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return None

        changes = {}

        if name is not None and name != asset.name:
            changes["name"] = {"old": asset.name, "new": name}
            asset.name = name

        if asset_type is not None and asset_type != asset.asset_type:
            changes["asset_type"] = {"old": asset.asset_type, "new": asset_type}
            asset.asset_type = asset_type

        if source_id is not None and source_id != asset.source_id:
            if source_id:
                result = await self.session.execute(
                    select(Source).where(Source.id == source_id)
                )
                source = result.scalar_one_or_none()
                if not source:
                    raise ValueError(f"Data source '{source_id}' not found")
            changes["source_id"] = {"old": asset.source_id, "new": source_id}
            asset.source_id = source_id

        if description is not None and description != asset.description:
            changes["description"] = {"old": asset.description, "new": description}
            asset.description = description

        if owner_id is not None and owner_id != asset.owner_id:
            changes["owner_id"] = {"old": asset.owner_id, "new": owner_id}
            asset.owner_id = owner_id

        if quality_score is not None and quality_score != asset.quality_score:
            changes["quality_score"] = {"old": asset.quality_score, "new": quality_score}
            asset.update_quality_score(quality_score)

        if changes:
            await self.session.flush()
            await self.session.refresh(asset)
            await self.activity_logger.log(
                ResourceType.ASSET,
                asset.id,
                ActivityAction.UPDATED,
                actor_id=actor_id,
                description=f"Updated asset: {asset.name}",
                metadata={"changes": changes},
            )

        return asset

    async def delete_asset(
        self,
        asset_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete an asset.

        Args:
            asset_id: Asset ID.
            actor_id: User deleting the asset.

        Returns:
            True if deleted.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return False

        asset_name = asset.name
        deleted = await self.asset_repo.delete(asset_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.ASSET,
                asset_id,
                ActivityAction.DELETED,
                actor_id=actor_id,
                description=f"Deleted asset: {asset_name}",
            )

        return deleted

    # =========================================================================
    # Column Operations
    # =========================================================================

    async def get_columns(
        self,
        asset_id: str,
    ) -> Sequence[AssetColumn]:
        """Get columns for an asset.

        Args:
            asset_id: Asset ID.

        Returns:
            Sequence of columns.
        """
        return await self.column_repo.get_for_asset(asset_id)

    async def get_column(self, column_id: str) -> AssetColumn | None:
        """Get column by ID.

        Args:
            column_id: Column ID.

        Returns:
            Column or None.
        """
        return await self.column_repo.get_by_id(column_id)

    async def create_column(
        self,
        asset_id: str,
        *,
        name: str,
        data_type: str | None = None,
        description: str | None = None,
        is_nullable: bool = True,
        is_primary_key: bool = False,
        sensitivity_level: str | None = None,
        actor_id: str | None = None,
    ) -> AssetColumn:
        """Create a new column.

        Args:
            asset_id: Asset ID.
            name: Column name.
            data_type: Data type.
            description: Description.
            is_nullable: Whether nullable.
            is_primary_key: Whether PK.
            sensitivity_level: Sensitivity level.
            actor_id: User creating the column.

        Returns:
            Created column.

        Raises:
            ValueError: If asset not found.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found")

        column = await self.column_repo.create(
            asset_id=asset_id,
            name=name,
            data_type=data_type,
            description=description,
            is_nullable=is_nullable,
            is_primary_key=is_primary_key,
            sensitivity_level=sensitivity_level,
        )

        await self.activity_logger.log(
            ResourceType.COLUMN,
            column.id,
            ActivityAction.CREATED,
            actor_id=actor_id,
            description=f"Created column: {asset.name}.{column.name}",
        )

        return column

    async def update_column(
        self,
        column_id: str,
        *,
        name: str | None = None,
        data_type: str | None = None,
        description: str | None = None,
        is_nullable: bool | None = None,
        is_primary_key: bool | None = None,
        sensitivity_level: str | None = None,
        actor_id: str | None = None,
    ) -> AssetColumn | None:
        """Update a column.

        Args:
            column_id: Column ID.
            name: New name.
            data_type: New data type.
            description: New description.
            is_nullable: New nullable setting.
            is_primary_key: New PK setting.
            sensitivity_level: New sensitivity level.
            actor_id: User updating the column.

        Returns:
            Updated column or None.
        """
        column = await self.column_repo.get_by_id(column_id)
        if not column:
            return None

        changes = {}

        if name is not None and name != column.name:
            changes["name"] = {"old": column.name, "new": name}
            column.name = name

        if data_type is not None and data_type != column.data_type:
            changes["data_type"] = {"old": column.data_type, "new": data_type}
            column.data_type = data_type

        if description is not None and description != column.description:
            changes["description"] = {"old": column.description, "new": description}
            column.description = description

        if is_nullable is not None and is_nullable != column.is_nullable:
            changes["is_nullable"] = {"old": column.is_nullable, "new": is_nullable}
            column.is_nullable = is_nullable

        if is_primary_key is not None and is_primary_key != column.is_primary_key:
            changes["is_primary_key"] = {"old": column.is_primary_key, "new": is_primary_key}
            column.is_primary_key = is_primary_key

        if sensitivity_level is not None and sensitivity_level != column.sensitivity_level:
            changes["sensitivity_level"] = {"old": column.sensitivity_level, "new": sensitivity_level}
            column.sensitivity_level = sensitivity_level

        if changes:
            await self.session.flush()
            await self.session.refresh(column)
            await self.activity_logger.log(
                ResourceType.COLUMN,
                column.id,
                ActivityAction.UPDATED,
                actor_id=actor_id,
                description=f"Updated column: {column.name}",
                metadata={"changes": changes},
            )

        return column

    async def delete_column(
        self,
        column_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Delete a column.

        Args:
            column_id: Column ID.
            actor_id: User deleting the column.

        Returns:
            True if deleted.
        """
        column = await self.column_repo.get_by_id(column_id)
        if not column:
            return False

        column_name = column.name
        deleted = await self.column_repo.delete(column_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.COLUMN,
                column_id,
                ActivityAction.DELETED,
                actor_id=actor_id,
                description=f"Deleted column: {column_name}",
            )

        return deleted

    async def map_column_to_term(
        self,
        column_id: str,
        term_id: str,
        *,
        actor_id: str | None = None,
    ) -> AssetColumn | None:
        """Map a column to a glossary term.

        Args:
            column_id: Column ID.
            term_id: Term ID.
            actor_id: User creating the mapping.

        Returns:
            Updated column or None.

        Raises:
            ValueError: If term not found.
        """
        column = await self.column_repo.get_by_id(column_id)
        if not column:
            return None

        # Validate term exists
        result = await self.session.execute(
            select(GlossaryTerm).where(GlossaryTerm.id == term_id)
        )
        term = result.scalar_one_or_none()
        if not term:
            raise ValueError(f"Term '{term_id}' not found")

        column.map_to_term(term_id)
        await self.session.flush()
        await self.session.refresh(column)

        await self.activity_logger.log(
            ResourceType.COLUMN,
            column.id,
            ActivityAction.MAPPED,
            actor_id=actor_id,
            description=f"Mapped {column.name} to term: {term.name}",
            metadata={"term_id": term_id, "term_name": term.name},
        )

        return column

    async def unmap_column_from_term(
        self,
        column_id: str,
        *,
        actor_id: str | None = None,
    ) -> AssetColumn | None:
        """Remove term mapping from a column.

        Args:
            column_id: Column ID.
            actor_id: User removing the mapping.

        Returns:
            Updated column or None.
        """
        column = await self.column_repo.get_by_id(column_id)
        if not column:
            return None

        if column.term_id is None:
            return column

        column.unmap_term()
        await self.session.flush()
        await self.session.refresh(column)

        await self.activity_logger.log(
            ResourceType.COLUMN,
            column.id,
            ActivityAction.UNMAPPED,
            actor_id=actor_id,
            description=f"Removed term mapping from: {column.name}",
        )

        return column

    # =========================================================================
    # Tag Operations
    # =========================================================================

    async def get_tags(
        self,
        asset_id: str,
    ) -> list[AssetTag]:
        """Get tags for an asset.

        Args:
            asset_id: Asset ID.

        Returns:
            List of tags.
        """
        return await self.tag_repo.get_for_asset(asset_id)

    async def add_tag(
        self,
        asset_id: str,
        *,
        tag_name: str,
        tag_value: str | None = None,
        actor_id: str | None = None,
    ) -> AssetTag:
        """Add a tag to an asset.

        Args:
            asset_id: Asset ID.
            tag_name: Tag name.
            tag_value: Optional tag value.
            actor_id: User adding the tag.

        Returns:
            Created tag.

        Raises:
            ValueError: If asset not found or tag exists.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found")

        # Check for existing tag
        existing = await self.tag_repo.get_existing(asset_id, tag_name)
        if existing:
            raise ValueError(f"Tag '{tag_name}' already exists on this asset")

        tag = await self.tag_repo.create(
            asset_id=asset_id,
            tag_name=tag_name.strip().lower(),
            tag_value=tag_value,
        )

        await self.activity_logger.log(
            ResourceType.ASSET,
            asset_id,
            "tag_added",
            actor_id=actor_id,
            description=f"Added tag: {tag_name}",
            metadata={"tag_name": tag_name, "tag_value": tag_value},
        )

        return tag

    async def remove_tag(
        self,
        tag_id: str,
        *,
        actor_id: str | None = None,
    ) -> bool:
        """Remove a tag.

        Args:
            tag_id: Tag ID.
            actor_id: User removing the tag.

        Returns:
            True if removed.
        """
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            return False

        asset_id = tag.asset_id
        tag_name = tag.tag_name
        deleted = await self.tag_repo.delete(tag_id)

        if deleted:
            await self.activity_logger.log(
                ResourceType.ASSET,
                asset_id,
                "tag_removed",
                actor_id=actor_id,
                description=f"Removed tag: {tag_name}",
                metadata={"tag_name": tag_name},
            )

        return deleted
