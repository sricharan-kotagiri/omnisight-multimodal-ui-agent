"""
Pydantic v2 schemas for Healing-related API requests and responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class HealingOutcome(str, Enum):
    """Mirrors the healing_outcome DB enum."""
    success = "success"
    failed = "failed"
    skipped = "skipped"


class HealingAttemptResponse(BaseModel):
    """Full healing attempt record returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    execution_id: uuid.UUID
    action_index: int
    original_locator: str
    failed_action: str
    suggested_locator: Optional[str] = None
    confidence: Optional[float] = None
    outcome: str
    attempt_number: int
    error_details: Optional[str] = None
    created_at: datetime


class HealingHistoryResponse(BaseModel):
    """All healing attempts for a given task execution."""
    task_id: uuid.UUID
    execution_id: uuid.UUID
    attempts: List[HealingAttemptResponse]


class HealingAnalyzeRequest(BaseModel):
    """Payload for POST /api/v1/healing/analyze."""
    screenshot_b64: str
    original_locator: str
    failed_action: str
    dom_snapshot: Optional[str] = None
    url: str
    intended_action: str


class HealingAnalyzeResponse(BaseModel):
    """Response from POST /api/v1/healing/analyze."""
    suggested_locator: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: str
    model_version: str
    raw_response: Dict[str, Any]
