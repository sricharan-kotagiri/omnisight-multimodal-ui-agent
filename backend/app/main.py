"""
OmniSight FastAPI application entry point.

Responsibilities:
- Application factory (FastAPI instance + middleware)
- Lifespan handler: DB table creation on startup, engine disposal on shutdown
- Global exception handler for OmniSightException subclasses
- Health check endpoint
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import OmniSightException
from app.database.base import close_db, create_tables, get_db
from app.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle startup and shutdown events."""
    settings = get_settings()
    setup_logging(level=settings.log_level, is_development=settings.is_development)
    logger.info("Starting OmniSight API...")
    await create_tables()
    logger.info("Database tables created/verified.")
    yield
    await close_db()
    logger.info("OmniSight API shutdown complete.")


# ── Application factory ───────────────────────────────────────────────────────

app = FastAPI(
    title="OmniSight API",
    version="0.1.0",
    description="Multimodal UI Self-Healing & RPA Agent API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — origins are configured via the CORS_ORIGINS env variable
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(OmniSightException)
async def omnisight_exception_handler(
    request: Request, exc: OmniSightException
) -> JSONResponse:
    """Translate any OmniSightException subclass into a structured JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "message": exc.message},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/api/v1/health", tags=["health"])
async def health_check() -> dict:
    """
    Return the operational health of the API.

    Attempts a lightweight DB query; reports 'disconnected' if it fails
    rather than propagating the exception (graceful degradation).
    """
    settings = get_settings()
    db_status = "disconnected"
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            db_status = "connected"
            break
    except Exception:  # noqa: BLE001
        db_status = "disconnected"

    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.app_env,
        "database": db_status,
    }
