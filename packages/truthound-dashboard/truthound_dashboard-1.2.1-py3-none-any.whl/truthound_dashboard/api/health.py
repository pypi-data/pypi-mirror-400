"""Health check endpoint.

This module provides health and readiness endpoints for
monitoring and orchestration systems.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from truthound_dashboard import __version__
from truthound_dashboard.schemas import BaseSchema

router = APIRouter()


class HealthResponse(BaseSchema):
    """Health check response schema."""

    status: str
    version: str
    timestamp: str
    checks: dict[str, Any] | None = None


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the server is healthy and responding",
)
async def health_check() -> HealthResponse:
    """Check server health.

    Returns basic health information including version and timestamp.
    """
    return HealthResponse(
        status="ok",
        version=__version__,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Readiness check",
    description="Check if the server is ready to accept requests",
)
async def readiness_check() -> HealthResponse:
    """Check server readiness.

    Performs deeper health checks including database connectivity.
    """
    checks: dict[str, Any] = {}

    # Check database
    try:
        from truthound_dashboard.db import get_session

        async with get_session() as session:
            await session.execute("SELECT 1")
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "message": str(e)}

    # Determine overall status
    all_ok = all(c.get("status") == "ok" for c in checks.values())

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        version=__version__,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks,
    )
