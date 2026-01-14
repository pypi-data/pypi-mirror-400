"""Sources API tests."""

import pytest


@pytest.mark.asyncio
async def test_list_sources_empty(async_client):
    """Test listing sources when none exist."""
    response = await async_client.get("/api/v1/sources")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_source(async_client, source_factory):
    """Test creating a new source."""
    source_data = source_factory.create(
        name="Test CSV Source",
        type="file",
        config={"path": "/data/test.csv"},
    )

    response = await async_client.post("/api/v1/sources", json=source_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test CSV Source"
    assert data["type"] == "file"
    assert data["config"]["path"] == "/data/test.csv"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_source_invalid_type(async_client):
    """Test creating source with invalid type fails."""
    source_data = {
        "name": "Invalid Source",
        "type": "invalid_type",
        "config": {"path": "/data/test.csv"},
    }

    response = await async_client.post("/api/v1/sources", json=source_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_source_empty_config(async_client):
    """Test creating source with empty config fails."""
    source_data = {
        "name": "Empty Config Source",
        "type": "file",
        "config": {},
    }

    response = await async_client.post("/api/v1/sources", json=source_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_source(async_client, source_factory):
    """Test getting a specific source."""
    # Create source first
    source_data = source_factory.create()
    create_response = await async_client.post("/api/v1/sources", json=source_data)
    source_id = create_response.json()["id"]

    # Get source
    response = await async_client.get(f"/api/v1/sources/{source_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == source_id
    assert data["name"] == source_data["name"]


@pytest.mark.asyncio
async def test_get_source_not_found(async_client):
    """Test getting non-existent source returns 404."""
    response = await async_client.get("/api/v1/sources/nonexistent-id")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_update_source(async_client, source_factory):
    """Test updating a source."""
    # Create source first
    source_data = source_factory.create()
    create_response = await async_client.post("/api/v1/sources", json=source_data)
    source_id = create_response.json()["id"]

    # Update source
    update_data = {"name": "Updated Name"}
    response = await async_client.put(f"/api/v1/sources/{source_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["id"] == source_id


@pytest.mark.asyncio
async def test_update_source_not_found(async_client):
    """Test updating non-existent source returns 404."""
    update_data = {"name": "Updated Name"}
    response = await async_client.put(
        "/api/v1/sources/nonexistent-id", json=update_data
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_source(async_client, source_factory):
    """Test deleting a source."""
    # Create source first
    source_data = source_factory.create()
    create_response = await async_client.post("/api/v1/sources", json=source_data)
    source_id = create_response.json()["id"]

    # Delete source
    response = await async_client.delete(f"/api/v1/sources/{source_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify deletion
    get_response = await async_client.get(f"/api/v1/sources/{source_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_source_not_found(async_client):
    """Test deleting non-existent source returns 404."""
    response = await async_client.delete("/api/v1/sources/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sources_pagination(async_client, source_factory):
    """Test source listing with pagination."""
    # Create multiple sources
    for i in range(5):
        source_data = source_factory.create(name=f"Source {i}")
        await async_client.post("/api/v1/sources", json=source_data)

    # Test pagination
    response = await async_client.get("/api/v1/sources?offset=0&limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["limit"] == 3
