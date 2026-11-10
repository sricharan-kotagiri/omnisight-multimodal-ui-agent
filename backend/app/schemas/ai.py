"""
Pydantic v2 schemas for AI-related data.

GeminiResponse is used internally to validate Gemini API responses before
the application acts on them — we never trust raw AI output.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class GeminiResponse(BaseModel):
    """
    Internal schema for validating the JSON returned by Gemini.

    Gemini is instructed (via the prompt) to return JSON matching this shape.
    If validation fails, HealingException is raised rather than using the raw value.
    """
    suggested_locator: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    element_description: str


class AIAnalysisResponse(BaseModel):
    """Full AI analysis record returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    healing_attempt_id: uuid.UUID
    screenshot_b64: Optional[str] = None
    dom_snapshot: Optional[str] = None
    prompt_sent: str
    raw_response: Dict[str, Any]
    parsed_locator: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    model_version: str
    latency_ms: Optional[int] = None
    created_at: datetime
