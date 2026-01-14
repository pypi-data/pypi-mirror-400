"""Rules API endpoints.

This module provides endpoints for managing custom validation rules.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from truthound_dashboard.schemas import (
    MessageResponse,
    RuleCreate,
    RuleListItem,
    RuleListResponse,
    RuleResponse,
    RuleUpdate,
)

from .deps import RuleServiceDep, SourceServiceDep

router = APIRouter()


@router.get(
    "/sources/{source_id}/rules",
    response_model=RuleListResponse,
    summary="List source rules",
    description="Get all validation rules for a data source",
)
async def list_source_rules(
    service: RuleServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum items")] = 50,
    active_only: Annotated[bool, Query(description="Only return active rules")] = False,
) -> RuleListResponse:
    """List all rules for a source.

    Args:
        service: Injected rule service.
        source_service: Injected source service.
        source_id: Source to get rules for.
        limit: Maximum rules to return.
        active_only: Only return active rules.

    Returns:
        List of rules.

    Raises:
        HTTPException: 404 if source not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    rules = await service.get_rules_for_source(
        source_id,
        limit=limit,
        active_only=active_only,
    )

    return RuleListResponse(
        data=[RuleListItem.from_model(r) for r in rules],
        total=len(rules),
        limit=limit,
    )


@router.get(
    "/sources/{source_id}/rules/active",
    response_model=RuleResponse | None,
    summary="Get active rule",
    description="Get the currently active rule for a source",
)
async def get_active_rule(
    service: RuleServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
) -> RuleResponse | None:
    """Get the active rule for a source.

    Args:
        service: Injected rule service.
        source_service: Injected source service.
        source_id: Source to get active rule for.

    Returns:
        Active rule or None.

    Raises:
        HTTPException: 404 if source not found.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    rule = await service.get_active_rule(source_id)
    if rule is None:
        return None
    return RuleResponse.from_model(rule)


@router.post(
    "/sources/{source_id}/rules",
    response_model=RuleResponse,
    status_code=201,
    summary="Create rule",
    description="Create a new validation rule for a source",
)
async def create_rule(
    service: RuleServiceDep,
    source_service: SourceServiceDep,
    source_id: Annotated[str, Path(description="Source ID")],
    rule: RuleCreate,
    activate: Annotated[bool, Query(description="Activate this rule")] = True,
) -> RuleResponse:
    """Create a new rule for a source.

    Args:
        service: Injected rule service.
        source_service: Injected source service.
        source_id: Source to create rule for.
        rule: Rule creation data.
        activate: Whether to make this the active rule.

    Returns:
        Created rule.

    Raises:
        HTTPException: 404 if source not found, 400 if YAML is invalid.
    """
    # Verify source exists
    source = await source_service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    try:
        created = await service.create_rule(
            source_id,
            rules_yaml=rule.rules_yaml,
            name=rule.name,
            description=rule.description,
            activate=activate,
        )
        return RuleResponse.from_model(created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="Get rule",
    description="Get a specific rule by ID",
)
async def get_rule(
    service: RuleServiceDep,
    rule_id: Annotated[str, Path(description="Rule ID")],
) -> RuleResponse:
    """Get a specific rule.

    Args:
        service: Injected rule service.
        rule_id: Rule unique identifier.

    Returns:
        Rule details.

    Raises:
        HTTPException: 404 if rule not found.
    """
    rule = await service.get_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return RuleResponse.from_model(rule)


@router.put(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="Update rule",
    description="Update an existing rule",
)
async def update_rule(
    service: RuleServiceDep,
    rule_id: Annotated[str, Path(description="Rule ID")],
    update: RuleUpdate,
) -> RuleResponse:
    """Update an existing rule.

    Args:
        service: Injected rule service.
        rule_id: Rule unique identifier.
        update: Update data.

    Returns:
        Updated rule.

    Raises:
        HTTPException: 404 if rule not found, 400 if YAML is invalid.
    """
    try:
        updated = await service.update_rule(
            rule_id,
            name=update.name,
            description=update.description,
            rules_yaml=update.rules_yaml,
            version=update.version,
            is_active=update.is_active,
        )
        if updated is None:
            raise HTTPException(status_code=404, detail="Rule not found")
        return RuleResponse.from_model(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/rules/{rule_id}",
    response_model=MessageResponse,
    summary="Delete rule",
    description="Delete a rule",
)
async def delete_rule(
    service: RuleServiceDep,
    rule_id: Annotated[str, Path(description="Rule ID")],
) -> MessageResponse:
    """Delete a rule.

    Args:
        service: Injected rule service.
        rule_id: Rule unique identifier.

    Returns:
        Success message.

    Raises:
        HTTPException: 404 if rule not found.
    """
    deleted = await service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return MessageResponse(message="Rule deleted successfully")


@router.post(
    "/rules/{rule_id}/activate",
    response_model=RuleResponse,
    summary="Activate rule",
    description="Activate a rule and deactivate others for the same source",
)
async def activate_rule(
    service: RuleServiceDep,
    rule_id: Annotated[str, Path(description="Rule ID")],
) -> RuleResponse:
    """Activate a rule.

    This will deactivate any other active rules for the same source.

    Args:
        service: Injected rule service.
        rule_id: Rule unique identifier.

    Returns:
        Activated rule.

    Raises:
        HTTPException: 404 if rule not found.
    """
    rule = await service.activate_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return RuleResponse.from_model(rule)
