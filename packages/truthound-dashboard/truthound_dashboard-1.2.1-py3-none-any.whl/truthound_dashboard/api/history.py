"""Validation history API endpoints.

Provides endpoints for validation history and trend analysis.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from truthound_dashboard.core import HistoryService

from .deps import SessionDep

router = APIRouter()


async def get_history_service(session: SessionDep) -> HistoryService:
    """Get history service dependency."""
    return HistoryService(session)


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]


@router.get(
    "/sources/{source_id}/history",
    response_model=dict,
    summary="Get validation history",
    description="Get validation history with trend analysis for a source.",
)
async def get_validation_history(
    source_id: str,
    service: HistoryServiceDep,
    period: Literal["7d", "30d", "90d"] = Query("30d", description="Time period"),
    granularity: Literal["hourly", "daily", "weekly"] = Query(
        "daily", description="Aggregation granularity"
    ),
) -> dict:
    """Get validation history with trend data.

    Args:
        source_id: Source ID.
        service: History service.
        period: Time period to analyze (7d, 30d, 90d).
        granularity: Aggregation granularity (hourly, daily, weekly).

    Returns:
        Dictionary with summary, trend, failure_frequency, and recent_validations.
    """
    try:
        data = await service.get_history(
            source_id,
            period=period,
            granularity=granularity,
        )
        return {"success": True, "data": data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
