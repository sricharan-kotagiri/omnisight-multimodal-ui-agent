"""
Shared pytest fixtures for the OmniSight test suite.

Uses an in-memory SQLite database (via aiosqlite) so tests run without
a real PostgreSQL instance.  The FastAPI DB dependency is overridden so
every request uses the test session.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db_session, get_execution_session_factory
from app.database.base import Base
from app.main import app

# ── Test database ─────────────────────────────────────────────────────────────
# Use a named shared in-memory SQLite database so all connections (test session +
# background task sessions) share the same data.
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create an in-memory SQLite engine and build all tables once per session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        # Import all models to register them with Base.metadata
        import app.models.ai_analysis  # noqa: F401
        import app.models.execution  # noqa: F401
        import app.models.execution_log  # noqa: F401
        import app.models.healing_attempt  # noqa: F401
        import app.models.task  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine):
    """Yield a fresh AsyncSession for each test function."""
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_client(test_db: AsyncSession, test_engine):
    """
    Return an AsyncClient wired to the FastAPI app with the DB dependency overridden.

    Both the request-scoped session AND the background-task session factory are
    overridden so execution background tasks write to the same SQLite database.
    """
    # Build a session factory that uses the test engine
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        yield test_db

    def override_get_execution_session_factory():
        return test_session_factory

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_execution_session_factory] = override_get_execution_session_factory

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data() -> dict:
    """Minimal valid payload for creating a task."""
    return {
        "name": "Test Task",
        "description": "A test automation task",
        "target_url": "https://example.com",
        "actions": [
            {
                "type": "navigate",
                "locator": None,
                "value": None,
                "timeout_ms": 30000,
                "requires_approval": False,
            }
        ],
    }


@pytest_asyncio.fixture
async def sample_task(test_client: AsyncClient, sample_task_data: dict) -> dict:
    """Create a task via the API and return the response JSON."""
    response = await test_client.post("/api/v1/tasks", json=sample_task_data)
    assert response.status_code == 201, response.text
    return response.json()
