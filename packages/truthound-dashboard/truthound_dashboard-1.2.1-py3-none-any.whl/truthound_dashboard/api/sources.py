"""Sources API endpoints.

This module provides CRUD endpoints for managing data sources.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from truthound_dashboard.schemas import (
    MessageResponse,
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceUpdate,
)

from .deps import SourceServiceDep

router = APIRouter()


@router.get(
    "",
    response_model=SourceListResponse,
    summary="List sources",
    description="Get a paginated list of all data sources",
)
async def list_sources(
    service: SourceServiceDep,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum items to return")
    ] = 100,
    active_only: Annotated[
        bool, Query(description="Only return active sources")
    ] = True,
) -> SourceListResponse:
    """List all data sources with pagination.

    Args:
        service: Injected source service.
        offset: Number of items to skip.
        limit: Maximum items to return.
        active_only: Filter to active sources only.

    Returns:
        Paginated list of sources.
    """
    sources = await service.list(offset=offset, limit=limit, active_only=active_only)

    return SourceListResponse(
        data=[SourceResponse.from_model(s) for s in sources],
        total=len(sources),  # TODO: Get actual total count
        offset=offset,
        limit=limit,
    )


@router.post(
    "",
    response_model=SourceResponse,
    status_code=201,
    summary="Create source",
    description="Create a new data source",
)
async def create_source(
    service: SourceServiceDep,
    source: SourceCreate,
) -> SourceResponse:
    """Create a new data source.

    Args:
        service: Injected source service.
        source: Source creation data.

    Returns:
        Created source.
    """
    created = await service.create(
        name=source.name,
        type=source.type,
        config=source.config,
        description=source.description,
    )
    return SourceResponse.from_model(created)


@router.get(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Get source",
    description="Get a specific data source by ID",
)
async def get_source(
    service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
) -> SourceResponse:
    """Get a specific data source.

    Args:
        service: Injected source service.
        source_id: Source unique identifier.

    Returns:
        Source details.

    Raises:
        HTTPException: 404 if source not found.
    """
    source = await service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceResponse.from_model(source)


@router.put(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Update source",
    description="Update an existing data source",
)
async def update_source(
    service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    update: SourceUpdate,
) -> SourceResponse:
    """Update an existing data source.

    Args:
        service: Injected source service.
        source_id: Source unique identifier.
        update: Update data.

    Returns:
        Updated source.

    Raises:
        HTTPException: 404 if source not found.
    """
    updated = await service.update(
        source_id,
        name=update.name,
        config=update.config,
        description=update.description,
        is_active=update.is_active,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceResponse.from_model(updated)


@router.delete(
    "/{source_id}",
    response_model=MessageResponse,
    summary="Delete source",
    description="Delete a data source and all related data",
)
async def delete_source(
    service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
) -> MessageResponse:
    """Delete a data source.

    Args:
        service: Injected source service.
        source_id: Source unique identifier.

    Returns:
        Success message.

    Raises:
        HTTPException: 404 if source not found.
    """
    deleted = await service.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return MessageResponse(message="Source deleted successfully")


@router.post(
    "/{source_id}/test",
    response_model=dict,
    summary="Test source connection",
    description="Test connection to a data source",
)
async def test_source_connection(
    service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
) -> dict:
    """Test connection to a data source.

    Args:
        service: Injected source service.
        source_id: Source unique identifier.

    Returns:
        Connection test result with success status and message.

    Raises:
        HTTPException: 404 if source not found.
    """
    from truthound_dashboard.core.connections import test_connection

    source = await service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    result = await test_connection(source.type, source.config)
    return {"success": True, "data": result}


@router.get(
    "/types/supported",
    response_model=dict,
    summary="Get supported source types",
    description="Get list of supported data source types and their configuration",
)
async def get_supported_types() -> dict:
    """Get list of supported source types.

    Returns:
        List of supported source types with required/optional fields.
    """
    from truthound_dashboard.core.connections import get_supported_source_types

    return {"success": True, "data": get_supported_source_types()}
