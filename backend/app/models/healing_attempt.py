"""
HealingAttempt model — records one attempt by the self-healing engine to recover
from an automation failure.

Each attempt captures the original failing locator, the AI-suggested alternative,
a confidence score, and the final outcome.
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
    from app.models.ai_analysis import AIAnalysis


class HealingAttempt(Base):
    __tablename__ = "healing_attempts"

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

    action_index: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    original_locator: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    failed_action: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    suggested_locator: Mapped[str | None] = mapped_column(sa.String(1024), nullable=True)
    confidence: Mapped[float | None] = mapped_column(sa.Float, nullable=True)

    outcome: Mapped[str] = mapped_column(
        sa.Enum(
            "success", "failed", "skipped",
            name="healing_outcome",
            native_enum=False,
        ),
        nullable=False,
        default="skipped",
    )

    attempt_number: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    error_details: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    execution: Mapped["Execution"] = relationship(
        "Execution",
        back_populates="healing_attempts",
    )
    ai_analysis: Mapped["AIAnalysis | None"] = relationship(
        "AIAnalysis",
        back_populates="healing_attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )
