"""Schemas API endpoints.

This module provides endpoints for schema learning and management.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from truthound_dashboard.schemas import (
    SchemaLearnRequest,
    SchemaResponse,
    SchemaUpdateRequest,
)

from .deps import SchemaServiceDep, SourceServiceDep

router = APIRouter()


@router.get(
    "/sources/{source_id}/schema",
    response_model=SchemaResponse | None,
    summary="Get source schema",
    description="Get the active schema for a data source",
)
async def get_schema(
    service: SchemaServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
) -> SchemaResponse | None:
    """Get the active schema for a source.

    Args:
        service: Injected schema service.
        source_service: Injected source service.
        source_id: Source to get schema for.

    Returns:
        Schema if exists, None otherwise.

    Raises:
        HTTPException: 404 if source not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    schema = await service.get_schema(source_id)
    if schema is None:
        return None
    return SchemaResponse.from_model(schema)


@router.post(
    "/sources/{source_id}/learn",
    response_model=SchemaResponse,
    summary="Learn schema",
    description="Auto-learn schema from data source",
)
async def learn_schema(
    service: SchemaServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    request: SchemaLearnRequest,
) -> SchemaResponse:
    """Learn schema from a data source.

    Args:
        service: Injected schema service.
        source_service: Injected source service.
        source_id: Source to learn schema from.
        request: Learning options.

    Returns:
        Learned schema.

    Raises:
        HTTPException: 404 if source not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    try:
        schema = await service.learn_schema(
            source_id,
            infer_constraints=request.infer_constraints,
        )
        return SchemaResponse.from_model(schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/sources/{source_id}/schema",
    response_model=SchemaResponse,
    summary="Update schema",
    description="Update the schema YAML for a source",
)
async def update_schema(
    service: SchemaServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    request: SchemaUpdateRequest,
) -> SchemaResponse:
    """Update schema YAML for a source.

    Args:
        service: Injected schema service.
        source_service: Injected source service.
        source_id: Source to update schema for.
        request: New schema YAML.

    Returns:
        Updated schema.

    Raises:
        HTTPException: 404 if source or schema not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    schema = await service.update_schema(source_id, request.schema_yaml)
    if schema is None:
        raise HTTPException(
            status_code=404,
            detail="No active schema found. Use /learn to create one first.",
        )
    return SchemaResponse.from_model(schema)
