"""
ExecutionLog model — structured log entries emitted during an execution.

The column is named 'metadata' in the database but exposed as 'metadata_' on the
Python class to avoid clashing with SQLAlchemy's internal use of the name 'metadata'.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.execution import Execution


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    level: Mapped[str] = mapped_column(
        sa.Enum(
            "debug", "info", "warning", "error",
            name="log_level",
            native_enum=False,
        ),
        nullable=False,
        default="info",
    )
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # 'metadata' is a reserved attribute name in SQLAlchemy's DeclarativeBase.
    # We use 'metadata_' as the Python attribute and 'metadata' as the DB column name.
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",          # explicit DB column name
        sa.JSON,
        nullable=True,
    )

    timestamp: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    execution: Mapped["Execution"] = relationship(
        "Execution",
        back_populates="execution_logs",
    )
