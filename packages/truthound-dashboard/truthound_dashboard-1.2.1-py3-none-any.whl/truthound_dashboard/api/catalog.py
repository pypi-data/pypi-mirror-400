"""Catalog API endpoints.

This module provides REST API endpoints for managing data catalog
assets, columns, and tags.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from truthound_dashboard.core.phase5 import CatalogService
from truthound_dashboard.schemas import (
    AssetCreate,
    AssetListItem,
    AssetListResponse,
    AssetResponse,
    AssetUpdate,
    ColumnCreate,
    ColumnListResponse,
    ColumnResponse,
    ColumnTermMapping,
    ColumnUpdate,
    MessageResponse,
    TagCreate,
    TagResponse,
)

from .deps import SessionDep

router = APIRouter()


# =============================================================================
# Dependencies
# =============================================================================


async def get_catalog_service(session: SessionDep) -> CatalogService:
    """Get catalog service dependency."""
    return CatalogService(session)


CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]


# =============================================================================
# Asset Endpoints
# =============================================================================


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    service: CatalogServiceDep,
    search: Annotated[str | None, Query(description="Search query")] = None,
    asset_type: Annotated[str | None, Query(description="Filter by type")] = None,
    source_id: Annotated[str | None, Query(description="Filter by data source")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> AssetListResponse:
    """List catalog assets with optional filters.

    - **search**: Search in asset name and description
    - **asset_type**: Filter by type (table, file, api)
    - **source_id**: Filter by linked data source
    """
    assets, total = await service.list_assets(
        query=search,
        asset_type=asset_type,
        source_id=source_id,
        offset=offset,
        limit=limit,
    )
    return AssetListResponse(
        data=[AssetListItem.from_model(a) for a in assets],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    service: CatalogServiceDep,
    data: AssetCreate,
) -> AssetResponse:
    """Create a new catalog asset."""
    try:
        columns_data = [c.model_dump() for c in data.columns] if data.columns else None
        tags_data = [t.model_dump() for t in data.tags] if data.tags else None

        asset = await service.create_asset(
            name=data.name,
            asset_type=data.asset_type.value,
            source_id=data.source_id,
            description=data.description,
            owner_id=data.owner_id,
            columns=columns_data,
            tags=tags_data,
        )
        return AssetResponse.from_model(asset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    service: CatalogServiceDep,
    asset_id: str,
) -> AssetResponse:
    """Get a catalog asset by ID."""
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found",
        )
    return AssetResponse.from_model(asset)


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    service: CatalogServiceDep,
    asset_id: str,
    data: AssetUpdate,
) -> AssetResponse:
    """Update a catalog asset."""
    try:
        asset = await service.update_asset(
            asset_id,
            name=data.name,
            asset_type=data.asset_type.value if data.asset_type else None,
            source_id=data.source_id,
            description=data.description,
            owner_id=data.owner_id,
            quality_score=data.quality_score,
        )
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset '{asset_id}' not found",
            )
        return AssetResponse.from_model(asset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/assets/{asset_id}", response_model=MessageResponse)
async def delete_asset(
    service: CatalogServiceDep,
    asset_id: str,
) -> MessageResponse:
    """Delete a catalog asset."""
    deleted = await service.delete_asset(asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found",
        )
    return MessageResponse(message="Asset deleted successfully")


# =============================================================================
# Column Endpoints
# =============================================================================


@router.get("/assets/{asset_id}/columns", response_model=ColumnListResponse)
async def get_asset_columns(
    service: CatalogServiceDep,
    asset_id: str,
) -> ColumnListResponse:
    """Get columns for an asset."""
    # Verify asset exists
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found",
        )

    columns = await service.get_columns(asset_id)
    return ColumnListResponse(
        data=[ColumnResponse.from_model(c) for c in columns],
        total=len(columns),
    )


@router.post("/assets/{asset_id}/columns", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED)
async def create_column(
    service: CatalogServiceDep,
    asset_id: str,
    data: ColumnCreate,
) -> ColumnResponse:
    """Add a column to an asset."""
    try:
        column = await service.create_column(
            asset_id,
            name=data.name,
            data_type=data.data_type,
            description=data.description,
            is_nullable=data.is_nullable,
            is_primary_key=data.is_primary_key,
            sensitivity_level=data.sensitivity_level.value if data.sensitivity_level else None,
        )
        return ColumnResponse.from_model(column)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/columns/{column_id}", response_model=ColumnResponse)
async def update_column(
    service: CatalogServiceDep,
    column_id: str,
    data: ColumnUpdate,
) -> ColumnResponse:
    """Update a column."""
    column = await service.update_column(
        column_id,
        name=data.name,
        data_type=data.data_type,
        description=data.description,
        is_nullable=data.is_nullable,
        is_primary_key=data.is_primary_key,
        sensitivity_level=data.sensitivity_level.value if data.sensitivity_level else None,
    )
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_id}' not found",
        )
    return ColumnResponse.from_model(column)


@router.delete("/columns/{column_id}", response_model=MessageResponse)
async def delete_column(
    service: CatalogServiceDep,
    column_id: str,
) -> MessageResponse:
    """Delete a column."""
    deleted = await service.delete_column(column_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_id}' not found",
        )
    return MessageResponse(message="Column deleted successfully")


# =============================================================================
# Column-Term Mapping Endpoints
# =============================================================================


@router.put("/columns/{column_id}/term", response_model=ColumnResponse)
async def map_column_to_term(
    service: CatalogServiceDep,
    column_id: str,
    data: ColumnTermMapping,
) -> ColumnResponse:
    """Map a column to a glossary term."""
    try:
        column = await service.map_column_to_term(column_id, data.term_id)
        if not column:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Column '{column_id}' not found",
            )
        return ColumnResponse.from_model(column)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/columns/{column_id}/term", response_model=ColumnResponse)
async def unmap_column_from_term(
    service: CatalogServiceDep,
    column_id: str,
) -> ColumnResponse:
    """Remove term mapping from a column."""
    column = await service.unmap_column_from_term(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_id}' not found",
        )
    return ColumnResponse.from_model(column)


# =============================================================================
# Tag Endpoints
# =============================================================================


@router.get("/assets/{asset_id}/tags")
async def get_asset_tags(
    service: CatalogServiceDep,
    asset_id: str,
) -> list[TagResponse]:
    """Get tags for an asset."""
    # Verify asset exists
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found",
        )

    tags = await service.get_tags(asset_id)
    return [TagResponse.from_model(t) for t in tags]


@router.post("/assets/{asset_id}/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def add_tag(
    service: CatalogServiceDep,
    asset_id: str,
    data: TagCreate,
) -> TagResponse:
    """Add a tag to an asset."""
    try:
        tag = await service.add_tag(
            asset_id,
            tag_name=data.tag_name,
            tag_value=data.tag_value,
        )
        return TagResponse.from_model(tag)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/tags/{tag_id}", response_model=MessageResponse)
async def remove_tag(
    service: CatalogServiceDep,
    tag_id: str,
) -> MessageResponse:
    """Remove a tag."""
    deleted = await service.remove_tag(tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag '{tag_id}' not found",
        )
    return MessageResponse(message="Tag removed successfully")
