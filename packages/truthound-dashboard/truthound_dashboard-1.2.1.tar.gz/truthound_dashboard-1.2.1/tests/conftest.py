"""Test fixtures and configuration.

This module provides shared fixtures for all tests including:
- Database setup and teardown
- Test client for API testing
- Sample data factories
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from truthound_dashboard.config import Settings, reset_settings
from truthound_dashboard.db import Base, get_session_factory, reset_connection
from truthound_dashboard.db import database as db_module
from truthound_dashboard.main import create_app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with in-memory database."""
    reset_settings()
    return Settings(
        data_dir="/tmp/truthound-test",
        log_level="debug",
    )


@pytest_asyncio.fixture
async def db_engine():
    """Create an in-memory test database engine."""
    # Reset any existing connection first
    reset_connection()

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    reset_connection()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing.

    This fixture provides a session that can be used in tests.
    The session is rolled back after each test.
    """
    session_factory = get_session_factory(db_engine)

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for API testing.

    This fixture creates a test client that can be used to make
    requests to the API without starting the actual server.
    """
    # Inject test engine into the global database module
    # This ensures the app uses our in-memory test database
    db_module._engine = db_engine
    db_module._session_factory = get_session_factory(db_engine)

    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Reset after test
    reset_connection()


# Sample data factories
class SourceFactory:
    """Factory for creating test sources."""

    _counter = 0

    @classmethod
    def create(
        cls,
        name: str | None = None,
        type: str = "file",
        config: dict | None = None,
    ) -> dict:
        """Create a source data dictionary."""
        cls._counter += 1
        return {
            "name": name or f"Test Source {cls._counter}",
            "type": type,
            "config": config or {"path": f"/data/test_{cls._counter}.csv"},
        }


@pytest.fixture
def source_factory() -> type[SourceFactory]:
    """Provide the source factory."""
    SourceFactory._counter = 0
    return SourceFactory
