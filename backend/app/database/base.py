"""
SQLAlchemy 2.0 async database setup for OmniSight.

Provides:
- Async engine (create_async_engine)
- Async session factory (async_sessionmaker)
- Declarative base class (Base) shared by all models
- get_db() dependency generator for FastAPI
- create_tables() / close_db() lifecycle helpers called from main.py lifespan
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

# ── Engine & session factory ──────────────────────────────────────────────────
# Built lazily so that unit tests can supply a different DATABASE_URL before
# the engine is created.

_engine = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine():
    global _engine, _async_session_factory
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
            echo=settings.is_development,
        )
        _async_session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the module-level async session factory, creating it if needed."""
    _get_engine()  # ensures factory is initialised
    assert _async_session_factory is not None
    return _async_session_factory


# ── Declarative base ──────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Shared declarative base for all OmniSight models."""
    pass


# ── FastAPI dependency ────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator that yields a database session.

    Usage (FastAPI):
        db: AsyncSession = Depends(get_db)
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Lifecycle helpers ─────────────────────────────────────────────────────────

async def create_tables() -> None:
    """
    Create all database tables based on the registered models.

    All model modules must be imported before this function is called so that
    their classes are registered with Base.metadata.  The imports below ensure
    that is the case regardless of the caller's import order.
    """
    # Import models to register them with Base.metadata
    import app.models.task  # noqa: F401
    import app.models.execution  # noqa: F401
    import app.models.healing_attempt  # noqa: F401
    import app.models.execution_log  # noqa: F401
    import app.models.ai_analysis  # noqa: F401

    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine connection pool during application shutdown."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
