"""Service layer tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from truthound_dashboard.core.services import SourceRepository, SourceService


@pytest.mark.asyncio
async def test_source_repository_create(db_session: AsyncSession):
    """Test creating a source via repository."""
    repo = SourceRepository(db_session)

    source = await repo.create(
        name="Test Source",
        type="file",
        config={"path": "/data/test.csv"},
    )

    assert source.id is not None
    assert source.name == "Test Source"
    assert source.type == "file"
    assert source.is_active is True


@pytest.mark.asyncio
async def test_source_repository_get_by_id(db_session: AsyncSession):
    """Test getting a source by ID."""
    repo = SourceRepository(db_session)

    # Create source
    created = await repo.create(
        name="Test Source",
        type="file",
        config={"path": "/data/test.csv"},
    )

    # Get by ID
    source = await repo.get_by_id(created.id)

    assert source is not None
    assert source.id == created.id
    assert source.name == "Test Source"


@pytest.mark.asyncio
async def test_source_repository_get_by_id_not_found(db_session: AsyncSession):
    """Test getting non-existent source returns None."""
    repo = SourceRepository(db_session)

    source = await repo.get_by_id("nonexistent-id")

    assert source is None


@pytest.mark.asyncio
async def test_source_repository_list(db_session: AsyncSession):
    """Test listing sources."""
    repo = SourceRepository(db_session)

    # Create multiple sources
    for i in range(3):
        await repo.create(
            name=f"Source {i}",
            type="file",
            config={"path": f"/data/test_{i}.csv"},
        )

    # List sources
    sources = await repo.list()

    assert len(sources) == 3


@pytest.mark.asyncio
async def test_source_repository_update(db_session: AsyncSession):
    """Test updating a source."""
    repo = SourceRepository(db_session)

    # Create source
    created = await repo.create(
        name="Original Name",
        type="file",
        config={"path": "/data/test.csv"},
    )

    # Update source
    updated = await repo.update(created.id, name="Updated Name")

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_source_repository_delete(db_session: AsyncSession):
    """Test deleting a source."""
    repo = SourceRepository(db_session)

    # Create source
    created = await repo.create(
        name="To Delete",
        type="file",
        config={"path": "/data/test.csv"},
    )

    # Delete source
    deleted = await repo.delete(created.id)

    assert deleted is True

    # Verify deletion
    source = await repo.get_by_id(created.id)
    assert source is None


@pytest.mark.asyncio
async def test_source_repository_get_active(db_session: AsyncSession):
    """Test getting only active sources."""
    repo = SourceRepository(db_session)

    # Create active source
    await repo.create(
        name="Active Source",
        type="file",
        config={"path": "/data/active.csv"},
    )

    # Create and deactivate source
    inactive = await repo.create(
        name="Inactive Source",
        type="file",
        config={"path": "/data/inactive.csv"},
    )
    await repo.update(inactive.id, is_active=False)

    # Get active sources only
    sources = await repo.get_active()

    assert len(sources) == 1
    assert sources[0].name == "Active Source"


@pytest.mark.asyncio
async def test_source_service_create(db_session: AsyncSession):
    """Test creating a source via service."""
    service = SourceService(db_session)

    source = await service.create(
        name="Test Source",
        type="file",
        config={"path": "/data/test.csv"},
        description="A test source",
    )

    assert source.id is not None
    assert source.name == "Test Source"
    assert source.description == "A test source"


@pytest.mark.asyncio
async def test_source_service_list(db_session: AsyncSession):
    """Test listing sources via service."""
    service = SourceService(db_session)

    # Create sources
    await service.create(name="Source 1", type="file", config={"path": "/a.csv"})
    await service.create(name="Source 2", type="file", config={"path": "/b.csv"})

    # List all
    sources = await service.list()

    assert len(sources) == 2


@pytest.mark.asyncio
async def test_source_service_update(db_session: AsyncSession):
    """Test updating a source via service."""
    service = SourceService(db_session)

    # Create source
    created = await service.create(
        name="Original",
        type="file",
        config={"path": "/data/test.csv"},
    )

    # Update source
    updated = await service.update(
        created.id,
        name="Updated",
        description="New description",
    )

    assert updated is not None
    assert updated.name == "Updated"
    assert updated.description == "New description"


@pytest.mark.asyncio
async def test_source_service_delete(db_session: AsyncSession):
    """Test deleting a source via service."""
    service = SourceService(db_session)

    # Create source
    created = await service.create(
        name="To Delete",
        type="file",
        config={"path": "/data/test.csv"},
    )

    # Delete
    result = await service.delete(created.id)

    assert result is True

    # Verify
    source = await service.get_by_id(created.id)
    assert source is None
