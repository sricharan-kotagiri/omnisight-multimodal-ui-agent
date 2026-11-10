"""
FastAPI dependency factories for OmniSight.

Import these in router files to inject database sessions and settings.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.database.base import get_db, get_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for use as a FastAPI dependency."""
    async for session in get_db():
        yield session


def get_settings_dep() -> Settings:
    """Return the application settings singleton (injectable via Depends)."""
    return get_settings()


def get_execution_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Return the session factory used by background execution tasks.

    This is a separate dependency so tests can override it with the test-scoped
    SQLite factory, ensuring background tasks write to the same in-memory DB as
    the test session.
    """
    return get_session_factory()
