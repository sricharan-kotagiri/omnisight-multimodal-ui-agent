"""
AIAnalysis model — stores the full context sent to Gemini and the response received.

Linked 1-to-1 to a HealingAttempt so we can audit every AI call.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.healing_attempt import HealingAttempt


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    healing_attempt_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("healing_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The screenshot sent to Gemini (base-64 encoded), may be omitted in some flows
    screenshot_b64: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    dom_snapshot: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    prompt_sent: Mapped[str] = mapped_column(sa.Text, nullable=False)
    raw_response: Mapped[dict] = mapped_column(sa.JSON, nullable=False)

    parsed_locator: Mapped[str | None] = mapped_column(sa.String(1024), nullable=True)
    confidence: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    model_version: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    healing_attempt: Mapped["HealingAttempt"] = relationship(
        "HealingAttempt",
        back_populates="ai_analysis",
    )
