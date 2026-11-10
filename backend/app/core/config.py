"""
Application configuration for OmniSight.

Loads settings from environment variables and .env file using Pydantic BaseSettings.
All secrets must be provided via environment — nothing is hardcoded here.
"""

import secrets
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://omnisight:omnisight@localhost:5432/omnisight"

    # ── Gemini AI ─────────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # ── Application ───────────────────────────────────────────────────────────
    app_env: str = "development"
    # Default secret generated at startup; override via SECRET_KEY env var in production
    secret_key: str = secrets.token_hex(32)
    log_level: str = "INFO"

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Self-Healing ──────────────────────────────────────────────────────────
    max_healing_retries: int = 3
    healing_confidence_threshold: float = 0.7

    # ── Browser ───────────────────────────────────────────────────────────────
    browser_timeout_ms: int = 30000

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        """Accept both a comma-separated string and a pre-parsed list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    @property
    def is_development(self) -> bool:
        """True when running in the development environment."""
        return self.app_env == "development"


# Module-level singleton — initialised lazily on first call
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
