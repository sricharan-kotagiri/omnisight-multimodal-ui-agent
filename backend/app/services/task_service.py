"""
Task service — database operations for tasks, executions, logs and healing history.

All functions use the SQLAlchemy 2.0 select() API with async sessions.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TaskNotFoundException
from app.models.execution import Execution
from app.models.execution_log import ExecutionLog
from app.models.healing_attempt import HealingAttempt
from app.models.task import Task
from app.schemas.task import TaskCreate


async def create_task(db: AsyncSession, task_create: TaskCreate) -> Task:
    """
    Persist a new Task record and return it.

    Actions are serialised as a list of dicts so they survive the JSON round-trip.
    """
    task = Task(
        name=task_create.name,
        description=task_create.description,
        target_url=task_create.target_url,
        # Convert each ActionItem to a plain dict for JSON storage
        actions=[action.model_dump() for action in task_create.actions],
        status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Task:
    """
    Fetch a single task by primary key.

    Raises TaskNotFoundException if no matching record exists.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundException(str(task_id))
    return task


async def get_task_latest_execution(
    db: AsyncSession, task_id: uuid.UUID
) -> Optional[Execution]:
    """Return the most-recently-started execution for the given task, or None."""
    result = await db.execute(
        select(Execution)
        .where(Execution.task_id == task_id)
        .order_by(Execution.started_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_execution_logs(
    db: AsyncSession,
    execution_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[ExecutionLog]:
    """Return paginated log entries for the given execution, oldest first."""
    result = await db.execute(
        select(ExecutionLog)
        .where(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.timestamp.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_healing_history(
    db: AsyncSession, execution_id: uuid.UUID
) -> List[HealingAttempt]:
    """Return all healing attempts for the given execution, oldest first."""
    result = await db.execute(
        select(HealingAttempt)
        .where(HealingAttempt.execution_id == execution_id)
        .order_by(HealingAttempt.created_at.asc())
    )
    return list(result.scalars().all())
