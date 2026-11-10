"""
Pydantic v2 schemas for Task-related API requests and responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, field_validator


class ActionType(str, Enum):
    """Supported automation action types."""
    navigate = "navigate"
    click = "click"
    fill = "fill"
    scroll = "scroll"
    wait = "wait"
    select = "select"
    screenshot = "screenshot"


class ActionItem(BaseModel):
    """A single step in an automation task."""
    type: ActionType
    locator: Optional[str] = None
    value: Optional[str] = None
    timeout_ms: int = 30000
    requires_approval: bool = False


class TaskCreate(BaseModel):
    """Payload for POST /api/v1/tasks."""
    name: str
    description: Optional[str] = None
    target_url: str
    actions: List[ActionItem]

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task name must not be blank.")
        if len(v) > 255:
            raise ValueError("Task name must be 255 characters or fewer.")
        return v

    @field_validator("target_url", mode="before")
    @classmethod
    def validate_target_url(cls, v: object) -> str:
        """Ensure the URL is a valid http/https URL and return it as a plain string."""
        # Validate via AnyHttpUrl then coerce to str so the model stores a string
        url_obj = AnyHttpUrl(str(v))  # raises ValidationError if invalid
        return str(url_obj)

    @field_validator("actions")
    @classmethod
    def actions_not_empty(cls, v: List[ActionItem]) -> List[ActionItem]:
        if not v:
            raise ValueError("A task must have at least one action.")
        return v


class TaskUpdate(BaseModel):
    """Payload for PATCH /api/v1/tasks/{task_id} (future use)."""
    name: Optional[str] = None
    description: Optional[str] = None


class TaskResponse(BaseModel):
    """Task representation returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    target_url: str
    actions: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""
    items: List[TaskResponse]
    total: int
