"""
Structured logging setup for OmniSight.

In development: human-readable output with timestamps and colours (standard StreamHandler).
In production:  JSON-formatted output for ingestion by log aggregators (e.g. CloudWatch, GCP).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging(level: str = "INFO", is_development: bool = True) -> None:
    """
    Configure the root logger once at application startup.

    Called from the FastAPI lifespan handler in main.py.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    if is_development:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = _JsonFormatter()

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    # Replace any existing handlers to avoid duplicate output
    root.handlers = [handler]

    # Quieten noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if is_development else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.  Call this at module level: logger = get_logger(__name__)."""
    return logging.getLogger(name)
