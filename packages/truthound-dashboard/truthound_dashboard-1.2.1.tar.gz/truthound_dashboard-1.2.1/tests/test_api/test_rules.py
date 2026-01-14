"""Rules API tests."""

import pytest

SAMPLE_RULES_YAML = """columns:
  user_id:
    not_null: true
    unique: true
  email:
    pattern: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\\\.[a-zA-Z0-9-.]+$"
  age:
    min: 0
    max: 150
"""


@pytest.fixture
async def source_with_id(async_client, source_factory):
    """Create a source and return its ID."""
    source_data = source_factory.create(name="Test Source for Rules")
    response = await async_client.post("/api/v1/sources", json=source_data)
    return response.json()["id"]


@pytest.mark.asyncio
async def test_list_rules_empty(async_client, source_with_id):
    """Test listing rules when none exist."""
    response = await async_client.get(f"/api/v1/sources/{source_with_id}/rules")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_rule(async_client, source_with_id):
    """Test creating a new rule."""
    rule_data = {
        "name": "Test Rules",
        "description": "Test validation rules",
        "rules_yaml": SAMPLE_RULES_YAML,
    }

    response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=true",
        json=rule_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Rules"
    assert data["description"] == "Test validation rules"
    assert data["is_active"] is True
    assert data["source_id"] == source_with_id
    assert "id" in data
    assert "created_at" in data
    assert data["column_count"] == 3  # user_id, email, age


@pytest.mark.asyncio
async def test_create_rule_invalid_yaml(async_client, source_with_id):
    """Test creating a rule with invalid YAML fails."""
    rule_data = {
        "name": "Invalid Rules",
        "rules_yaml": "invalid: yaml: content:",  # Invalid YAML
    }

    response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules",
        json=rule_data,
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_rule_source_not_found(async_client):
    """Test creating a rule for non-existent source fails."""
    rule_data = {
        "name": "Test Rules",
        "rules_yaml": SAMPLE_RULES_YAML,
    }

    response = await async_client.post(
        "/api/v1/sources/nonexistent-id/rules",
        json=rule_data,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_active_rule(async_client, source_with_id):
    """Test getting the active rule for a source."""
    # Create a rule
    rule_data = {
        "name": "Active Rule",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=true",
        json=rule_data,
    )

    # Get active rule
    response = await async_client.get(f"/api/v1/sources/{source_with_id}/rules/active")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Active Rule"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_active_rule_none(async_client, source_with_id):
    """Test getting active rule when none exists."""
    response = await async_client.get(f"/api/v1/sources/{source_with_id}/rules/active")

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_rule_by_id(async_client, source_with_id):
    """Test getting a specific rule by ID."""
    # Create a rule
    rule_data = {
        "name": "Test Rule",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    create_response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules",
        json=rule_data,
    )
    rule_id = create_response.json()["id"]

    # Get rule
    response = await async_client.get(f"/api/v1/rules/{rule_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rule_id
    assert data["name"] == "Test Rule"


@pytest.mark.asyncio
async def test_get_rule_not_found(async_client):
    """Test getting non-existent rule returns 404."""
    response = await async_client.get("/api/v1/rules/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_rule(async_client, source_with_id):
    """Test updating a rule."""
    # Create a rule
    rule_data = {
        "name": "Original Name",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    create_response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules",
        json=rule_data,
    )
    rule_id = create_response.json()["id"]

    # Update rule
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
    }
    response = await async_client.put(f"/api/v1/rules/{rule_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_rule_yaml(async_client, source_with_id):
    """Test updating rule YAML content."""
    # Create a rule
    rule_data = {
        "name": "Test Rule",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    create_response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules",
        json=rule_data,
    )
    rule_id = create_response.json()["id"]

    # Update YAML
    new_yaml = """columns:
  name:
    not_null: true
"""
    update_data = {"rules_yaml": new_yaml}
    response = await async_client.put(f"/api/v1/rules/{rule_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["column_count"] == 1  # Only 'name' now


@pytest.mark.asyncio
async def test_update_rule_not_found(async_client):
    """Test updating non-existent rule returns 404."""
    update_data = {"name": "Updated Name"}
    response = await async_client.put("/api/v1/rules/nonexistent-id", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_rule(async_client, source_with_id):
    """Test deleting a rule."""
    # Create a rule
    rule_data = {
        "name": "Rule to Delete",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    create_response = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules",
        json=rule_data,
    )
    rule_id = create_response.json()["id"]

    # Delete rule
    response = await async_client.delete(f"/api/v1/rules/{rule_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify deletion
    get_response = await async_client.get(f"/api/v1/rules/{rule_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_rule_not_found(async_client):
    """Test deleting non-existent rule returns 404."""
    response = await async_client.delete("/api/v1/rules/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_activate_rule(async_client, source_with_id):
    """Test activating a rule deactivates others."""
    # Create first rule (active)
    rule1_data = {
        "name": "Rule 1",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    response1 = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=true",
        json=rule1_data,
    )
    rule1_id = response1.json()["id"]

    # Create second rule (should become active)
    rule2_data = {
        "name": "Rule 2",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    response2 = await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=true",
        json=rule2_data,
    )
    rule2_id = response2.json()["id"]

    # Verify rule2 is active
    active_response = await async_client.get(
        f"/api/v1/sources/{source_with_id}/rules/active"
    )
    assert active_response.json()["id"] == rule2_id

    # Activate rule1
    activate_response = await async_client.post(f"/api/v1/rules/{rule1_id}/activate")

    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True

    # Verify rule1 is now active
    active_response = await async_client.get(
        f"/api/v1/sources/{source_with_id}/rules/active"
    )
    assert active_response.json()["id"] == rule1_id


@pytest.mark.asyncio
async def test_list_rules_with_pagination(async_client, source_with_id):
    """Test listing rules with limit."""
    # Create multiple rules
    for i in range(5):
        rule_data = {
            "name": f"Rule {i}",
            "rules_yaml": SAMPLE_RULES_YAML,
        }
        await async_client.post(
            f"/api/v1/sources/{source_with_id}/rules?activate=false",
            json=rule_data,
        )

    # Test with limit
    response = await async_client.get(f"/api/v1/sources/{source_with_id}/rules?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["limit"] == 3


@pytest.mark.asyncio
async def test_list_rules_active_only(async_client, source_with_id):
    """Test listing only active rules."""
    # Create inactive rule
    rule1_data = {
        "name": "Inactive Rule",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=false",
        json=rule1_data,
    )

    # Create active rule
    rule2_data = {
        "name": "Active Rule",
        "rules_yaml": SAMPLE_RULES_YAML,
    }
    await async_client.post(
        f"/api/v1/sources/{source_with_id}/rules?activate=true",
        json=rule2_data,
    )

    # List active only
    response = await async_client.get(
        f"/api/v1/sources/{source_with_id}/rules?active_only=true"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "Active Rule"
