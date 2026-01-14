"""Catalog API tests.

Tests for data catalog assets, columns, and tags.
"""

import pytest


@pytest.mark.asyncio
async def test_list_assets_empty(async_client):
    """Test listing assets when none exist."""
    response = await async_client.get("/api/v1/catalog/assets")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_asset(async_client):
    """Test creating a new catalog asset."""
    asset_data = {
        "name": "customers",
        "asset_type": "table",
        "description": "Customer master data",
        "owner_id": "data_team",
    }

    response = await async_client.post("/api/v1/catalog/assets", json=asset_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "customers"
    assert data["asset_type"] == "table"
    assert data["description"] == "Customer master data"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_asset_with_source(async_client, source_factory):
    """Test creating an asset linked to a data source."""
    # Create source first
    source_data = source_factory.create(name="Test DB")
    source_response = await async_client.post("/api/v1/sources", json=source_data)
    source_id = source_response.json()["id"]

    # Create asset with source
    asset_data = {
        "name": "orders",
        "asset_type": "table",
        "source_id": source_id,
    }

    response = await async_client.post("/api/v1/catalog/assets", json=asset_data)

    assert response.status_code == 201
    data = response.json()
    assert data["source_id"] == source_id


@pytest.mark.asyncio
async def test_get_asset(async_client):
    """Test getting a specific asset."""
    # Create asset first
    asset_data = {
        "name": "products",
        "asset_type": "table",
    }
    create_response = await async_client.post(
        "/api/v1/catalog/assets", json=asset_data
    )
    asset_id = create_response.json()["id"]

    # Get asset
    response = await async_client.get(f"/api/v1/catalog/assets/{asset_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == asset_id
    assert data["name"] == "products"


@pytest.mark.asyncio
async def test_get_asset_not_found(async_client):
    """Test getting non-existent asset returns 404."""
    response = await async_client.get("/api/v1/catalog/assets/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_asset(async_client):
    """Test updating an asset."""
    # Create asset first
    create_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "original", "asset_type": "table"},
    )
    asset_id = create_response.json()["id"]

    # Update asset
    update_data = {
        "name": "updated_name",
        "description": "Updated description",
        "quality_score": 85.5,
    }
    response = await async_client.put(
        f"/api/v1/catalog/assets/{asset_id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_name"
    assert data["description"] == "Updated description"
    assert data["quality_score"] == 85.5


@pytest.mark.asyncio
async def test_delete_asset(async_client):
    """Test deleting an asset."""
    # Create asset first
    create_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "to_delete", "asset_type": "file"},
    )
    asset_id = create_response.json()["id"]

    # Delete asset
    response = await async_client.delete(f"/api/v1/catalog/assets/{asset_id}")

    assert response.status_code == 200

    # Verify deletion
    get_response = await async_client.get(f"/api/v1/catalog/assets/{asset_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_assets_with_filter(async_client):
    """Test listing assets with filters."""
    # Create assets of different types
    for asset_type in ["table", "table", "file", "api"]:
        await async_client.post(
            "/api/v1/catalog/assets",
            json={"name": f"asset_{asset_type}", "asset_type": asset_type},
        )

    # Filter by type
    response = await async_client.get("/api/v1/catalog/assets?asset_type=table")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert all(a["asset_type"] == "table" for a in data["data"])


@pytest.mark.asyncio
async def test_create_column(async_client):
    """Test adding a column to an asset."""
    # Create asset first
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "users", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Create column
    column_data = {
        "name": "user_id",
        "data_type": "uuid",
        "description": "Primary key",
        "is_primary_key": True,
        "is_nullable": False,
    }

    response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/columns", json=column_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "user_id"
    assert data["data_type"] == "uuid"
    assert data["is_primary_key"] is True
    assert data["is_nullable"] is False


@pytest.mark.asyncio
async def test_get_asset_columns(async_client):
    """Test getting columns for an asset."""
    # Create asset
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "employees", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Add columns
    columns = [
        {"name": "id", "data_type": "integer", "is_primary_key": True},
        {"name": "name", "data_type": "string"},
        {"name": "email", "data_type": "string"},
    ]
    for col in columns:
        await async_client.post(
            f"/api/v1/catalog/assets/{asset_id}/columns", json=col
        )

    # Get columns
    response = await async_client.get(f"/api/v1/catalog/assets/{asset_id}/columns")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_update_column(async_client):
    """Test updating a column."""
    # Create asset and column
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "test_table", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    column_response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/columns",
        json={"name": "original_col", "data_type": "string"},
    )
    column_id = column_response.json()["id"]

    # Update column
    update_data = {
        "name": "updated_col",
        "description": "Updated description",
        "sensitivity_level": "confidential",
    }
    response = await async_client.put(
        f"/api/v1/catalog/columns/{column_id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_col"
    assert data["sensitivity_level"] == "confidential"


@pytest.mark.asyncio
async def test_delete_column(async_client):
    """Test deleting a column."""
    # Create asset and column
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "test_table", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    column_response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/columns",
        json={"name": "to_delete", "data_type": "string"},
    )
    column_id = column_response.json()["id"]

    # Delete column
    response = await async_client.delete(f"/api/v1/catalog/columns/{column_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_map_column_to_term(async_client):
    """Test mapping a column to a glossary term."""
    # Create term
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Customer ID",
            "definition": "Unique customer identifier",
            "status": "approved",
        },
    )
    term_id = term_response.json()["id"]

    # Create asset and column
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "customers", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    column_response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/columns",
        json={"name": "customer_id", "data_type": "uuid"},
    )
    column_id = column_response.json()["id"]

    # Map column to term
    response = await async_client.put(
        f"/api/v1/catalog/columns/{column_id}/term",
        json={"term_id": term_id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["term_id"] == term_id


@pytest.mark.asyncio
async def test_unmap_column_from_term(async_client):
    """Test removing term mapping from a column."""
    # Create term, asset, column, and mapping
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Order ID",
            "definition": "Unique order identifier",
            "status": "approved",
        },
    )
    term_id = term_response.json()["id"]

    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "orders", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    column_response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/columns",
        json={"name": "order_id", "data_type": "uuid"},
    )
    column_id = column_response.json()["id"]

    # Map then unmap
    await async_client.put(
        f"/api/v1/catalog/columns/{column_id}/term",
        json={"term_id": term_id},
    )

    response = await async_client.delete(
        f"/api/v1/catalog/columns/{column_id}/term"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["term_id"] is None


@pytest.mark.asyncio
async def test_add_tag(async_client):
    """Test adding a tag to an asset."""
    # Create asset
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "sensitive_data", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Add tag
    tag_data = {"tag_name": "pii", "tag_value": "true"}

    response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/tags", json=tag_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tag_name"] == "pii"
    assert data["tag_value"] == "true"


@pytest.mark.asyncio
async def test_get_asset_tags(async_client):
    """Test getting tags for an asset."""
    # Create asset
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "tagged_asset", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Add tags
    tags = [
        {"tag_name": "department", "tag_value": "finance"},
        {"tag_name": "compliance", "tag_value": "gdpr"},
    ]
    for tag in tags:
        await async_client.post(
            f"/api/v1/catalog/assets/{asset_id}/tags", json=tag
        )

    # Get tags
    response = await async_client.get(f"/api/v1/catalog/assets/{asset_id}/tags")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_remove_tag(async_client):
    """Test removing a tag from an asset."""
    # Create asset and tag
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "test_asset", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    tag_response = await async_client.post(
        f"/api/v1/catalog/assets/{asset_id}/tags",
        json={"tag_name": "to_remove"},
    )
    tag_id = tag_response.json()["id"]

    # Remove tag
    response = await async_client.delete(f"/api/v1/catalog/tags/{tag_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_assets_by_source(async_client, source_factory):
    """Test filtering assets by data source."""
    # Create sources
    source1_data = source_factory.create(name="Source 1")
    source1_response = await async_client.post("/api/v1/sources", json=source1_data)
    source1_id = source1_response.json()["id"]

    source2_data = source_factory.create(name="Source 2")
    source2_response = await async_client.post("/api/v1/sources", json=source2_data)
    source2_id = source2_response.json()["id"]

    # Create assets for each source
    await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "asset1", "asset_type": "table", "source_id": source1_id},
    )
    await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "asset2", "asset_type": "table", "source_id": source1_id},
    )
    await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "asset3", "asset_type": "table", "source_id": source2_id},
    )

    # Filter by source
    response = await async_client.get(
        f"/api/v1/catalog/assets?source_id={source1_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert all(a["source_id"] == source1_id for a in data["data"])
