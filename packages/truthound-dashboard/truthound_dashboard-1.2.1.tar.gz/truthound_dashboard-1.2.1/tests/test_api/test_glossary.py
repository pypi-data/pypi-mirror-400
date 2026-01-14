"""Glossary API tests.

Tests for business glossary terms, categories, and relationships.
"""

import pytest


@pytest.mark.asyncio
async def test_list_terms_empty(async_client):
    """Test listing terms when none exist."""
    response = await async_client.get("/api/v1/glossary/terms")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_term(async_client):
    """Test creating a new glossary term."""
    term_data = {
        "name": "Customer ID",
        "definition": "Unique identifier for a customer in the system",
        "status": "draft",
    }

    response = await async_client.post("/api/v1/glossary/terms", json=term_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Customer ID"
    assert data["definition"] == "Unique identifier for a customer in the system"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_term_with_category(async_client):
    """Test creating a term with a category."""
    # Create category first
    category_data = {"name": "Identifiers", "description": "ID fields"}
    cat_response = await async_client.post(
        "/api/v1/glossary/categories", json=category_data
    )
    category_id = cat_response.json()["id"]

    # Create term with category
    term_data = {
        "name": "Order ID",
        "definition": "Unique identifier for an order",
        "category_id": category_id,
        "status": "approved",
    }

    response = await async_client.post("/api/v1/glossary/terms", json=term_data)

    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == category_id


@pytest.mark.asyncio
async def test_get_term(async_client):
    """Test getting a specific term."""
    # Create term first
    term_data = {
        "name": "Revenue",
        "definition": "Total income from sales",
        "status": "approved",
    }
    create_response = await async_client.post(
        "/api/v1/glossary/terms", json=term_data
    )
    term_id = create_response.json()["id"]

    # Get term
    response = await async_client.get(f"/api/v1/glossary/terms/{term_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == term_id
    assert data["name"] == "Revenue"


@pytest.mark.asyncio
async def test_get_term_not_found(async_client):
    """Test getting non-existent term returns 404."""
    response = await async_client.get("/api/v1/glossary/terms/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_term(async_client):
    """Test updating a term."""
    # Create term first
    term_data = {
        "name": "Original Name",
        "definition": "Original definition",
        "status": "draft",
    }
    create_response = await async_client.post(
        "/api/v1/glossary/terms", json=term_data
    )
    term_id = create_response.json()["id"]

    # Update term
    update_data = {"name": "Updated Name", "status": "approved"}
    response = await async_client.put(
        f"/api/v1/glossary/terms/{term_id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_delete_term(async_client):
    """Test deleting a term."""
    # Create term first
    term_data = {
        "name": "To Delete",
        "definition": "Will be deleted",
        "status": "draft",
    }
    create_response = await async_client.post(
        "/api/v1/glossary/terms", json=term_data
    )
    term_id = create_response.json()["id"]

    # Delete term
    response = await async_client.delete(f"/api/v1/glossary/terms/{term_id}")

    assert response.status_code == 200

    # Verify deletion
    get_response = await async_client.get(f"/api/v1/glossary/terms/{term_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_terms_with_search(async_client):
    """Test listing terms with search filter."""
    # Create multiple terms
    for name in ["Customer", "Customer ID", "Order"]:
        await async_client.post(
            "/api/v1/glossary/terms",
            json={"name": name, "definition": f"Definition for {name}", "status": "draft"},
        )

    # Search for "Customer"
    response = await async_client.get("/api/v1/glossary/terms?search=Customer")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_list_categories(async_client):
    """Test listing categories."""
    # Create categories
    for name in ["Finance", "Operations", "Sales"]:
        await async_client.post(
            "/api/v1/glossary/categories",
            json={"name": name, "description": f"{name} category"},
        )

    response = await async_client.get("/api/v1/glossary/categories")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_create_category(async_client):
    """Test creating a category."""
    category_data = {
        "name": "Financial Metrics",
        "description": "KPIs and financial measurements",
    }

    response = await async_client.post(
        "/api/v1/glossary/categories", json=category_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Financial Metrics"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_category(async_client):
    """Test updating a category."""
    # Create category
    create_response = await async_client.post(
        "/api/v1/glossary/categories",
        json={"name": "Original", "description": "Original desc"},
    )
    category_id = create_response.json()["id"]

    # Update
    response = await async_client.put(
        f"/api/v1/glossary/categories/{category_id}",
        json={"name": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_category(async_client):
    """Test deleting a category."""
    # Create category
    create_response = await async_client.post(
        "/api/v1/glossary/categories",
        json={"name": "To Delete"},
    )
    category_id = create_response.json()["id"]

    # Delete
    response = await async_client.delete(
        f"/api/v1/glossary/categories/{category_id}"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_relationship(async_client):
    """Test creating a relationship between terms."""
    # Create two terms
    term1_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Revenue", "definition": "Total income", "status": "approved"},
    )
    term1_id = term1_response.json()["id"]

    term2_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Sales", "definition": "Income from sales", "status": "approved"},
    )
    term2_id = term2_response.json()["id"]

    # Create relationship
    relationship_data = {
        "source_term_id": term1_id,
        "target_term_id": term2_id,
        "relationship_type": "related",
    }

    response = await async_client.post(
        "/api/v1/glossary/relationships", json=relationship_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["source_term_id"] == term1_id
    assert data["target_term_id"] == term2_id
    assert data["relationship_type"] == "related"


@pytest.mark.asyncio
async def test_get_term_relationships(async_client):
    """Test getting relationships for a term."""
    # Create terms
    term1_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Term A", "definition": "Definition A", "status": "draft"},
    )
    term1_id = term1_response.json()["id"]

    term2_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Term B", "definition": "Definition B", "status": "draft"},
    )
    term2_id = term2_response.json()["id"]

    # Create relationship
    await async_client.post(
        "/api/v1/glossary/relationships",
        json={
            "source_term_id": term1_id,
            "target_term_id": term2_id,
            "relationship_type": "synonym",
        },
    )

    # Get relationships
    response = await async_client.get(
        f"/api/v1/glossary/terms/{term1_id}/relationships"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_delete_relationship(async_client):
    """Test deleting a relationship."""
    # Create terms and relationship
    term1_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Term X", "definition": "Def X", "status": "draft"},
    )
    term1_id = term1_response.json()["id"]

    term2_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Term Y", "definition": "Def Y", "status": "draft"},
    )
    term2_id = term2_response.json()["id"]

    rel_response = await async_client.post(
        "/api/v1/glossary/relationships",
        json={
            "source_term_id": term1_id,
            "target_term_id": term2_id,
            "relationship_type": "related",
        },
    )
    relationship_id = rel_response.json()["id"]

    # Delete relationship
    response = await async_client.delete(
        f"/api/v1/glossary/relationships/{relationship_id}"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_term_history(async_client):
    """Test getting term change history."""
    # Create and update term
    create_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={"name": "Tracked Term", "definition": "Original", "status": "draft"},
    )
    term_id = create_response.json()["id"]

    # Update to generate history
    await async_client.put(
        f"/api/v1/glossary/terms/{term_id}",
        json={"definition": "Updated definition"},
    )

    # Get history
    response = await async_client.get(
        f"/api/v1/glossary/terms/{term_id}/history"
    )

    assert response.status_code == 200
    data = response.json()
    # History should exist (at least for the update)
    assert "data" in data
