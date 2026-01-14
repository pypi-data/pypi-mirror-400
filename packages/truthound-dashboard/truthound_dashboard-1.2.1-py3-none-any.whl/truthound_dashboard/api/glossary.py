"""Glossary API endpoints.

This module provides REST API endpoints for managing business glossary
terms, categories, and relationships.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from truthound_dashboard.core.phase5 import GlossaryService
from truthound_dashboard.schemas import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    MessageResponse,
    RelationshipCreate,
    RelationshipListResponse,
    RelationshipResponse,
    TermCreate,
    TermHistoryListResponse,
    TermHistoryResponse,
    TermListItem,
    TermListResponse,
    TermResponse,
    TermUpdate,
)

from .deps import SessionDep

router = APIRouter()


# =============================================================================
# Dependencies
# =============================================================================


async def get_glossary_service(session: SessionDep) -> GlossaryService:
    """Get glossary service dependency."""
    return GlossaryService(session)


GlossaryServiceDep = Annotated[GlossaryService, Depends(get_glossary_service)]


# =============================================================================
# Term Endpoints
# =============================================================================


@router.get("/terms", response_model=TermListResponse)
async def list_terms(
    service: GlossaryServiceDep,
    search: Annotated[str | None, Query(description="Search query")] = None,
    category_id: Annotated[str | None, Query(description="Filter by category")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> TermListResponse:
    """List glossary terms with optional filters.

    - **search**: Search in term name and definition
    - **category_id**: Filter by category
    - **status**: Filter by status (draft, approved, deprecated)
    """
    terms, total = await service.list_terms(
        query=search,
        category_id=category_id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return TermListResponse(
        data=[TermListItem.from_model(t) for t in terms],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED)
async def create_term(
    service: GlossaryServiceDep,
    data: TermCreate,
) -> TermResponse:
    """Create a new glossary term."""
    try:
        term = await service.create_term(
            name=data.name,
            definition=data.definition,
            category_id=data.category_id,
            status=data.status.value,
            owner_id=data.owner_id,
        )
        return TermResponse.from_model(term)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/terms/{term_id}", response_model=TermResponse)
async def get_term(
    service: GlossaryServiceDep,
    term_id: str,
) -> TermResponse:
    """Get a glossary term by ID."""
    term = await service.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term_id}' not found",
        )
    return TermResponse.from_model(term)


@router.put("/terms/{term_id}", response_model=TermResponse)
async def update_term(
    service: GlossaryServiceDep,
    term_id: str,
    data: TermUpdate,
) -> TermResponse:
    """Update a glossary term."""
    try:
        term = await service.update_term(
            term_id,
            name=data.name,
            definition=data.definition,
            category_id=data.category_id,
            status=data.status.value if data.status else None,
            owner_id=data.owner_id,
        )
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Term '{term_id}' not found",
            )
        return TermResponse.from_model(term)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/terms/{term_id}", response_model=MessageResponse)
async def delete_term(
    service: GlossaryServiceDep,
    term_id: str,
) -> MessageResponse:
    """Delete a glossary term."""
    deleted = await service.delete_term(term_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term_id}' not found",
        )
    return MessageResponse(message="Term deleted successfully")


@router.get("/terms/{term_id}/history", response_model=TermHistoryListResponse)
async def get_term_history(
    service: GlossaryServiceDep,
    term_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> TermHistoryListResponse:
    """Get change history for a term."""
    # Verify term exists
    term = await service.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term_id}' not found",
        )

    history = await service.get_term_history(term_id, limit=limit)
    return TermHistoryListResponse(
        data=[TermHistoryResponse.from_model(h) for h in history],
        total=len(history),
    )


# =============================================================================
# Category Endpoints
# =============================================================================


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    service: GlossaryServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CategoryListResponse:
    """List all glossary categories."""
    categories, total = await service.list_categories(offset=offset, limit=limit)
    return CategoryListResponse(
        data=[CategoryResponse.from_model(c) for c in categories],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    service: GlossaryServiceDep,
    data: CategoryCreate,
) -> CategoryResponse:
    """Create a new glossary category."""
    try:
        category = await service.create_category(
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
        )
        return CategoryResponse.from_model(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    service: GlossaryServiceDep,
    category_id: str,
) -> CategoryResponse:
    """Get a glossary category by ID."""
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )
    return CategoryResponse.from_model(category)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    service: GlossaryServiceDep,
    category_id: str,
    data: CategoryUpdate,
) -> CategoryResponse:
    """Update a glossary category."""
    try:
        category = await service.update_category(
            category_id,
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )
        return CategoryResponse.from_model(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(
    service: GlossaryServiceDep,
    category_id: str,
) -> MessageResponse:
    """Delete a glossary category."""
    deleted = await service.delete_category(category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )
    return MessageResponse(message="Category deleted successfully")


# =============================================================================
# Relationship Endpoints
# =============================================================================


@router.get("/terms/{term_id}/relationships", response_model=RelationshipListResponse)
async def get_term_relationships(
    service: GlossaryServiceDep,
    term_id: str,
) -> RelationshipListResponse:
    """Get all relationships for a term."""
    # Verify term exists
    term = await service.get_term(term_id)
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term '{term_id}' not found",
        )

    relationships = await service.get_term_relationships(term_id)
    return RelationshipListResponse(
        data=[RelationshipResponse.from_model(r) for r in relationships],
        total=len(relationships),
    )


@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    service: GlossaryServiceDep,
    data: RelationshipCreate,
) -> RelationshipResponse:
    """Create a relationship between terms."""
    try:
        relationship = await service.create_relationship(
            source_term_id=data.source_term_id,
            target_term_id=data.target_term_id,
            relationship_type=data.relationship_type.value,
        )
        return RelationshipResponse.from_model(relationship)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/relationships/{relationship_id}", response_model=MessageResponse)
async def delete_relationship(
    service: GlossaryServiceDep,
    relationship_id: str,
) -> MessageResponse:
    """Delete a term relationship."""
    deleted = await service.delete_relationship(relationship_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship '{relationship_id}' not found",
        )
    return MessageResponse(message="Relationship deleted successfully")
