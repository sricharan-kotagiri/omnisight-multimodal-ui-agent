"""
Pydantic v2 schemas for Execution-related API responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStatus(str, Enum):
    """Mirrors the execution_status DB enum."""
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class ExecutionResponse(BaseModel):
    """Full execution record returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None


class ExecutionStatusResponse(BaseModel):
    """Lightweight status summary for GET /tasks/{id}/status."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class LogEntry(BaseModel):
    """A single log line from an execution."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    level: str
    message: str
    # The DB column is 'metadata' but the ORM attribute is 'metadata_'
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata_")
    timestamp: datetime


class LogsResponse(BaseModel):
    """List of log entries for a given execution."""
    execution_id: uuid.UUID
    logs: List[LogEntry]
    total: int
