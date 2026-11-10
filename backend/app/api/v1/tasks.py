"""
Task API endpoints — v1.

Routes:
  POST   /tasks                         Create a new task
  GET    /tasks/{task_id}               Get task details
  POST   /tasks/{task_id}/execute       Trigger execution (background)
  GET    /tasks/{task_id}/status        Latest execution status
  GET    /tasks/{task_id}/logs          Execution log entries
  GET    /tasks/{task_id}/healing       Healing attempt history
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.deps import get_db_session, get_execution_session_factory
from app.core.exceptions import SecurityException, TaskNotFoundException
from app.core.security import validate_url
from app.schemas.execution import ExecutionStatusResponse, LogEntry, LogsResponse
from app.schemas.healing import HealingAttemptResponse, HealingHistoryResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.services import execution_service, task_service

router = APIRouter()

# ── Type aliases for injected dependencies ────────────────────────────────────
DB = Annotated[AsyncSession, Depends(get_db_session)]
SessionFactory = Annotated[async_sessionmaker[AsyncSession], Depends(get_execution_session_factory)]


@router.post("", status_code=201, response_model=TaskResponse)
async def create_task(payload: TaskCreate, db: DB) -> TaskResponse:
    """
    Create a new automation task.

    Validates the target URL for SSRF safety before persisting.
    Returns 201 with the created task on success.
    """
    try:
        validate_url(payload.target_url)
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    task = await task_service.create_task(db, payload)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, db: DB) -> TaskResponse:
    """Retrieve full task details by ID."""
    try:
        task = await task_service.get_task(db, task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/execute", status_code=202)
async def execute_task(
    task_id: uuid.UUID,
    db: DB,
    background_tasks: BackgroundTasks,
    session_factory: SessionFactory,
) -> dict:
    """
    Trigger execution of a task as a background job.

    Returns 202 Accepted immediately with the execution_id.
    The actual execution runs after the response is sent.

    Note: In Phase 2 the execution will always end in 'failed' because
    Playwright is not yet integrated.
    """
    # Verify the task exists before queuing the background job
    try:
        task = await task_service.get_task(db, task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    # Pass the injectable session factory so tests can override it
    background_tasks.add_task(
        execution_service.run_execution,
        task_id,
        session_factory,
    )

    return {
        "execution_id": None,  # Actual UUID is assigned inside run_execution
        "message": "Execution queued. Check /status for progress.",
        "task_id": str(task.id),
    }


@router.get("/{task_id}/status", response_model=ExecutionStatusResponse)
async def get_task_status(task_id: uuid.UUID, db: DB) -> ExecutionStatusResponse:
    """Return the status of the most recent execution for a task."""
    # Ensure the task exists
    try:
        await task_service.get_task(db, task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    execution = await task_service.get_task_latest_execution(db, task_id)
    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="No executions found for this task.",
        )
    return ExecutionStatusResponse.model_validate(execution)


@router.get("/{task_id}/logs", response_model=LogsResponse)
async def get_task_logs(
    task_id: uuid.UUID,
    db: DB,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> LogsResponse:
    """
    Return execution log entries for the most recent execution of a task.

    Supports pagination via skip/limit query parameters.
    """
    try:
        await task_service.get_task(db, task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    execution = await task_service.get_task_latest_execution(db, task_id)
    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="No executions found for this task.",
        )

    logs = await task_service.get_execution_logs(db, execution.id, skip=skip, limit=limit)
    return LogsResponse(
        execution_id=execution.id,
        logs=[LogEntry.model_validate(log) for log in logs],
        total=len(logs),
    )


@router.get("/{task_id}/healing", response_model=HealingHistoryResponse)
async def get_task_healing(task_id: uuid.UUID, db: DB) -> HealingHistoryResponse:
    """Return the healing attempt history for the most recent execution of a task."""
    try:
        await task_service.get_task(db, task_id)
    except TaskNotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    execution = await task_service.get_task_latest_execution(db, task_id)
    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="No executions found for this task.",
        )

    attempts = await task_service.get_healing_history(db, execution.id)
    return HealingHistoryResponse(
        task_id=task_id,
        execution_id=execution.id,
        attempts=[HealingAttemptResponse.model_validate(a) for a in attempts],
    )
