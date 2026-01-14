"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test health endpoint returns ok status."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_version(async_client):
    """Test health endpoint returns correct version."""
    from truthound_dashboard import __version__

    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == __version__
