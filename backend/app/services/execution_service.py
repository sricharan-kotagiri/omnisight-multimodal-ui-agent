"""
Execution service — manages the lifecycle of a task execution.

PHASE 2 STUB: This service creates the execution record and immediately marks it
as 'failed' with a clear message that Phase 3 (Playwright integration) is not yet
connected.  The stub is intentionally honest — no fake automation is performed.

Phase 3 will replace the stub body with:
1. Launching a Playwright browser
2. Executing each task action via the automation executor
3. Capturing screenshots and DOM snapshots
4. Triggering the self-healing engine on failures
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.exceptions import TaskNotFoundException
from app.models.execution import Execution
from app.models.execution_log import ExecutionLog
from app.models.task import Task


async def run_execution(
    task_id: uuid.UUID,
    session_factory: Optional[async_sessionmaker[AsyncSession]] = None,
) -> None:
    """
    Execute a task by its ID.

    Creates its own database session so it can run as a FastAPI BackgroundTask
    after the HTTP response has already been sent (the request-scoped session
    would be closed by then).

    Args:
        task_id: The UUID of the task to execute.
        session_factory: Optional async_sessionmaker to use for the DB session.
            When None (the default), the application's global session factory is
            used.  Tests pass the test-scoped factory here so the background task
            writes to the same in-memory SQLite database.

    Current behaviour (Phase 2):
    - Creates an Execution record with status='running'.
    - Logs that the automation engine is not yet connected.
    - Immediately marks the execution as 'failed' with an informative message.
    """
    if session_factory is None:
        from app.database.base import get_session_factory
        factory = get_session_factory()
    else:
        factory = session_factory

    async with factory() as db:
        # ── 1. Fetch the task ─────────────────────────────────────────────────
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            raise TaskNotFoundException(str(task_id))

        # ── 2. Create the execution record ────────────────────────────────────
        execution = Execution(
            task_id=task_id,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        # ── 3. Log the start ──────────────────────────────────────────────────
        start_log = ExecutionLog(
            execution_id=execution.id,
            level="info",
            message=(
                "Execution started — automation engine not yet connected (Phase 3)"
            ),
        )
        db.add(start_log)
        await db.commit()

        # ── 4. Mark as failed (Phase 2 stub) ──────────────────────────────────
        execution.status = "failed"
        execution.completed_at = datetime.now(timezone.utc)
        execution.error_message = (
            "Playwright not yet integrated — "
            "Phase 3 will connect the automation engine."
        )
        await db.commit()
