"""API dependencies for dependency injection.

This module provides FastAPI dependencies for injecting services
and database sessions into route handlers.

Example:
    @router.get("/sources")
    async def list_sources(
        service: SourceService = Depends(get_source_service)
    ):
        return await service.list()
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.core import (
    DriftService,
    HistoryService,
    ProfileService,
    RuleService,
    ScheduleService,
    SchemaService,
    SourceService,
    ValidationService,
)
from truthound_dashboard.db import get_db_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession for database operations.
    """
    async for session in get_db_session():
        yield session


# Type alias for session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_source_service(session: SessionDep) -> SourceService:
    """Get source service dependency.

    Args:
        session: Database session.

    Returns:
        SourceService instance.
    """
    return SourceService(session)


async def get_validation_service(session: SessionDep) -> ValidationService:
    """Get validation service dependency.

    Args:
        session: Database session.

    Returns:
        ValidationService instance.
    """
    return ValidationService(session)


async def get_schema_service(session: SessionDep) -> SchemaService:
    """Get schema service dependency.

    Args:
        session: Database session.

    Returns:
        SchemaService instance.
    """
    return SchemaService(session)


async def get_profile_service(session: SessionDep) -> ProfileService:
    """Get profile service dependency.

    Args:
        session: Database session.

    Returns:
        ProfileService instance.
    """
    return ProfileService(session)


async def get_rule_service(session: SessionDep) -> RuleService:
    """Get rule service dependency.

    Args:
        session: Database session.

    Returns:
        RuleService instance.
    """
    return RuleService(session)


async def get_history_service(session: SessionDep) -> HistoryService:
    """Get history service dependency.

    Args:
        session: Database session.

    Returns:
        HistoryService instance.
    """
    return HistoryService(session)


async def get_drift_service(session: SessionDep) -> DriftService:
    """Get drift service dependency.

    Args:
        session: Database session.

    Returns:
        DriftService instance.
    """
    return DriftService(session)


async def get_schedule_service(session: SessionDep) -> ScheduleService:
    """Get schedule service dependency.

    Args:
        session: Database session.

    Returns:
        ScheduleService instance.
    """
    return ScheduleService(session)


# Type aliases for service dependencies
SourceServiceDep = Annotated[SourceService, Depends(get_source_service)]
ValidationServiceDep = Annotated[ValidationService, Depends(get_validation_service)]
SchemaServiceDep = Annotated[SchemaService, Depends(get_schema_service)]
ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]
RuleServiceDep = Annotated[RuleService, Depends(get_rule_service)]
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
DriftServiceDep = Annotated[DriftService, Depends(get_drift_service)]
ScheduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]
