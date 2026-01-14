"""Collaboration API tests.

Tests for comments and activity tracking.
"""

import pytest


@pytest.mark.asyncio
async def test_create_comment_on_term(async_client):
    """Test creating a comment on a glossary term."""
    # Create term first
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Test Term",
            "definition": "Test definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    # Create comment
    comment_data = {
        "resource_type": "term",
        "resource_id": term_id,
        "content": "This definition needs review.",
        "author_id": "user@example.com",
    }

    response = await async_client.post("/api/v1/comments", json=comment_data)

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This definition needs review."
    assert data["resource_type"] == "term"
    assert data["resource_id"] == term_id
    assert "id" in data


@pytest.mark.asyncio
async def test_create_comment_on_asset(async_client):
    """Test creating a comment on a catalog asset."""
    # Create asset first
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "Test Asset", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Create comment
    comment_data = {
        "resource_type": "asset",
        "resource_id": asset_id,
        "content": "This asset needs documentation.",
    }

    response = await async_client.post("/api/v1/comments", json=comment_data)

    assert response.status_code == 201
    data = response.json()
    assert data["resource_type"] == "asset"


@pytest.mark.asyncio
async def test_get_comments(async_client):
    """Test getting comments for a resource."""
    # Create term
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Commented Term",
            "definition": "Definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    # Create multiple comments
    for i in range(3):
        await async_client.post(
            "/api/v1/comments",
            json={
                "resource_type": "term",
                "resource_id": term_id,
                "content": f"Comment {i}",
            },
        )

    # Get comments
    response = await async_client.get(
        f"/api/v1/comments?resource_type=term&resource_id={term_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_create_reply_comment(async_client):
    """Test creating a reply to a comment."""
    # Create term
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Term with Replies",
            "definition": "Definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    # Create parent comment
    parent_response = await async_client.post(
        "/api/v1/comments",
        json={
            "resource_type": "term",
            "resource_id": term_id,
            "content": "Parent comment",
        },
    )
    parent_id = parent_response.json()["id"]

    # Create reply
    reply_data = {
        "resource_type": "term",
        "resource_id": term_id,
        "content": "Reply to parent",
        "parent_id": parent_id,
    }

    response = await async_client.post("/api/v1/comments", json=reply_data)

    assert response.status_code == 201
    data = response.json()
    assert data["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_update_comment(async_client):
    """Test updating a comment."""
    # Create term and comment
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Term",
            "definition": "Definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    comment_response = await async_client.post(
        "/api/v1/comments",
        json={
            "resource_type": "term",
            "resource_id": term_id,
            "content": "Original content",
        },
    )
    comment_id = comment_response.json()["id"]

    # Update comment
    response = await async_client.put(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Updated content"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_delete_comment(async_client):
    """Test deleting a comment."""
    # Create term and comment
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Term",
            "definition": "Definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    comment_response = await async_client.post(
        "/api/v1/comments",
        json={
            "resource_type": "term",
            "resource_id": term_id,
            "content": "To be deleted",
        },
    )
    comment_id = comment_response.json()["id"]

    # Delete comment
    response = await async_client.delete(f"/api/v1/comments/{comment_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_activities(async_client):
    """Test getting activity feed."""
    response = await async_client.get("/api/v1/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_activities_by_resource(async_client):
    """Test getting activities filtered by resource."""
    # Create term (should generate activity)
    term_response = await async_client.post(
        "/api/v1/glossary/terms",
        json={
            "name": "Activity Term",
            "definition": "Definition",
            "status": "draft",
        },
    )
    term_id = term_response.json()["id"]

    # Add comment (generates activity)
    await async_client.post(
        "/api/v1/comments",
        json={
            "resource_type": "term",
            "resource_id": term_id,
            "content": "Activity comment",
        },
    )

    # Get activities for term
    response = await async_client.get(
        f"/api/v1/activities?resource_type=term&resource_id={term_id}"
    )

    assert response.status_code == 200
    data = response.json()
    # Should have at least the comment activity
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_comment_generates_activity(async_client):
    """Test that creating a comment generates an activity."""
    # Create asset
    asset_response = await async_client.post(
        "/api/v1/catalog/assets",
        json={"name": "Activity Asset", "asset_type": "table"},
    )
    asset_id = asset_response.json()["id"]

    # Create comment
    await async_client.post(
        "/api/v1/comments",
        json={
            "resource_type": "asset",
            "resource_id": asset_id,
            "content": "New comment",
        },
    )

    # Check activities
    response = await async_client.get(
        f"/api/v1/activities?resource_type=asset&resource_id={asset_id}"
    )

    assert response.status_code == 200
    data = response.json()
    # Should have comment activity
    comment_activities = [a for a in data if a.get("action") == "commented"]
    assert len(comment_activities) >= 1


@pytest.mark.asyncio
async def test_get_comments_missing_params(async_client):
    """Test getting comments without required params returns error."""
    response = await async_client.get("/api/v1/comments")

    # Should return 400 for missing required params
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_comment_not_found(async_client):
    """Test deleting non-existent comment returns 404."""
    response = await async_client.delete("/api/v1/comments/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_comment_not_found(async_client):
    """Test updating non-existent comment returns 404."""
    response = await async_client.put(
        "/api/v1/comments/nonexistent-id",
        json={"content": "Updated"},
    )

    assert response.status_code == 404
