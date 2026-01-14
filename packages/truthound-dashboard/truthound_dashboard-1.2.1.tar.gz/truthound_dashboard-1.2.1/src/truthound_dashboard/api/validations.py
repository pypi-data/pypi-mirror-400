"""Validations API endpoints.

This module provides endpoints for running and managing validations.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from truthound_dashboard.schemas import (
    ValidationListItem,
    ValidationListResponse,
    ValidationResponse,
    ValidationRunRequest,
)

from .deps import SourceServiceDep, ValidationServiceDep

router = APIRouter()


@router.post(
    "/sources/{source_id}/validate",
    response_model=ValidationResponse,
    summary="Run validation",
    description="Run validation on a data source",
)
async def run_validation(
    service: ValidationServiceDep,
    source_id: Annotated[str, Path(description="Source ID to validate")],
    request: ValidationRunRequest,
) -> ValidationResponse:
    """Run validation on a data source.

    Args:
        service: Injected validation service.
        source_id: Source to validate.
        request: Validation options.

    Returns:
        Validation result.

    Raises:
        HTTPException: 404 if source not found.
    """
    try:
        validation = await service.run_validation(
            source_id,
            validators=request.validators,
            schema_path=request.schema_path,
            auto_schema=request.auto_schema,
        )
        return ValidationResponse.from_model(validation)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{validation_id}",
    response_model=ValidationResponse,
    summary="Get validation",
    description="Get a specific validation result by ID",
)
async def get_validation(
    service: ValidationServiceDep,
    validation_id: Annotated[str, Path(description="Validation ID")],
) -> ValidationResponse:
    """Get a specific validation result.

    Args:
        service: Injected validation service.
        validation_id: Validation unique identifier.

    Returns:
        Validation details with issues.

    Raises:
        HTTPException: 404 if validation not found.
    """
    validation = await service.get_validation(validation_id)
    if validation is None:
        raise HTTPException(status_code=404, detail="Validation not found")
    return ValidationResponse.from_model(validation)


@router.get(
    "/sources/{source_id}/validations",
    response_model=ValidationListResponse,
    summary="List source validations",
    description="Get validation history for a source",
)
async def list_source_validations(
    service: ValidationServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum items")] = 20,
) -> ValidationListResponse:
    """List validation history for a source.

    Args:
        service: Injected validation service.
        source_service: Injected source service.
        source_id: Source to get validations for.
        limit: Maximum validations to return.

    Returns:
        List of validation summaries.

    Raises:
        HTTPException: 404 if source not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    validations = await service.list_for_source(source_id, limit=limit)

    return ValidationListResponse(
        data=[ValidationListItem.from_model(v) for v in validations],
        total=len(validations),
        limit=limit,
    )
