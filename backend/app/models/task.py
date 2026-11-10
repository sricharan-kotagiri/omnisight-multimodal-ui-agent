"""
Task model — represents an automation task submitted by a user.

Each task has a target URL and a list of actions (stored as JSON).
The status progresses from 'pending' through 'running' to a terminal state.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.execution import Execution


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    target_url: Mapped[str] = mapped_column(sa.String(2048), nullable=False)

    # List of action dicts — stored as JSON
    actions: Mapped[list] = mapped_column(sa.JSON, nullable=False)

    # Task lifecycle status
    status: Mapped[str] = mapped_column(
        sa.Enum(
            "pending", "running", "completed", "failed", "cancelled",
            name="task_status",
            native_enum=False,  # VARCHAR constraint — works with both PG and SQLite
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    executions: Mapped[List["Execution"]] = relationship(
        "Execution",
        back_populates="task",
        cascade="all, delete-orphan",
    )
