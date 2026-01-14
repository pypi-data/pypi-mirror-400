"""Drift detection API endpoints.

Provides endpoints for drift comparison between datasets.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from truthound_dashboard.core import DriftService
from truthound_dashboard.schemas import (
    DriftCompareRequest,
    DriftComparisonListResponse,
)

from .deps import SessionDep

router = APIRouter()


async def get_drift_service(session: SessionDep) -> DriftService:
    """Get drift service dependency."""
    return DriftService(session)


DriftServiceDep = Annotated[DriftService, Depends(get_drift_service)]


@router.post(
    "/drift/compare",
    response_model=dict,
    summary="Compare datasets for drift",
    description="Compare two datasets to detect data drift.",
)
async def compare_datasets(
    request: DriftCompareRequest,
    service: DriftServiceDep,
) -> dict:
    """Compare two datasets for drift detection.

    Args:
        request: Comparison request with source IDs and options.
        service: Drift service.

    Returns:
        Drift comparison results.
    """
    try:
        comparison = await service.compare(
            baseline_source_id=request.baseline_source_id,
            current_source_id=request.current_source_id,
            columns=request.columns,
            method=request.method,
            threshold=request.threshold,
            sample_size=request.sample_size,
        )

        return {
            "success": True,
            "data": {
                "id": comparison.id,
                "baseline_source_id": comparison.baseline_source_id,
                "current_source_id": comparison.current_source_id,
                "has_drift": comparison.has_drift,
                "has_high_drift": comparison.has_high_drift,
                "total_columns": comparison.total_columns,
                "drifted_columns": comparison.drifted_columns,
                "drift_percentage": comparison.drift_percentage,
                "result": comparison.result_json,
                "config": comparison.config,
                "created_at": (
                    comparison.created_at.isoformat() if comparison.created_at else None
                ),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/drift/comparisons",
    response_model=DriftComparisonListResponse,
    summary="List drift comparisons",
    description="List all drift comparisons with optional filters.",
)
async def list_comparisons(
    service: DriftServiceDep,
    baseline_source_id: str | None = Query(
        None, description="Filter by baseline source"
    ),
    current_source_id: str | None = Query(None, description="Filter by current source"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> DriftComparisonListResponse:
    """List drift comparisons.

    Args:
        service: Drift service.
        baseline_source_id: Optional baseline source ID filter.
        current_source_id: Optional current source ID filter.
        limit: Maximum results to return.

    Returns:
        List of drift comparisons.
    """
    comparisons = await service.list_comparisons(
        baseline_source_id=baseline_source_id,
        current_source_id=current_source_id,
        limit=limit,
    )

    return DriftComparisonListResponse(
        success=True,
        data=[
            {
                "id": c.id,
                "baseline_source_id": c.baseline_source_id,
                "current_source_id": c.current_source_id,
                "has_drift": c.has_drift,
                "has_high_drift": c.has_high_drift,
                "total_columns": c.total_columns,
                "drifted_columns": c.drifted_columns,
                "drift_percentage": c.drift_percentage,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in comparisons
        ],
        total=len(comparisons),
    )


@router.get(
    "/drift/comparisons/{comparison_id}",
    response_model=dict,
    summary="Get drift comparison",
    description="Get a specific drift comparison by ID.",
)
async def get_comparison(
    comparison_id: str,
    service: DriftServiceDep,
) -> dict:
    """Get a drift comparison by ID.

    Args:
        comparison_id: Comparison ID.
        service: Drift service.

    Returns:
        Drift comparison details.
    """
    comparison = await service.get_comparison(comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Comparison not found")

    return {
        "success": True,
        "data": {
            "id": comparison.id,
            "baseline_source_id": comparison.baseline_source_id,
            "current_source_id": comparison.current_source_id,
            "has_drift": comparison.has_drift,
            "has_high_drift": comparison.has_high_drift,
            "total_columns": comparison.total_columns,
            "drifted_columns": comparison.drifted_columns,
            "drift_percentage": comparison.drift_percentage,
            "result": comparison.result_json,
            "config": comparison.config,
            "created_at": (
                comparison.created_at.isoformat() if comparison.created_at else None
            ),
            "updated_at": (
                comparison.updated_at.isoformat() if comparison.updated_at else None
            ),
        },
    }
