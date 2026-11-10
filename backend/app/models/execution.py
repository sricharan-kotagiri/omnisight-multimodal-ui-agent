"""
Execution model — one run of an automation task.

A task can have multiple executions (e.g. retries or re-runs).
Each execution tracks its own status, timing, and any errors encountered.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.execution_log import ExecutionLog
    from app.models.healing_attempt import HealingAttempt


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        sa.Enum(
            "running", "success", "failed", "cancelled",
            name="execution_status",
            native_enum=False,
        ),
        nullable=False,
        default="running",
    )

    started_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="executions",
    )
    execution_logs: Mapped[List["ExecutionLog"]] = relationship(
        "ExecutionLog",
        back_populates="execution",
        cascade="all, delete-orphan",
    )
    healing_attempts: Mapped[List["HealingAttempt"]] = relationship(
        "HealingAttempt",
        back_populates="execution",
        cascade="all, delete-orphan",
    )
