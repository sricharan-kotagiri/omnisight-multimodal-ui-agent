"""
Tests for SQLAlchemy models — verifies that tables are created and basic
CRUD operations work against the in-memory SQLite test database.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.models.task import Task

pytestmark = pytest.mark.asyncio


async def test_create_and_fetch_task(test_db):
    """Verify that a Task record can be persisted and retrieved."""
    task = Task(
        id=uuid.uuid4(),
        name="DB Test Task",
        target_url="https://example.com",
        actions=[{"type": "navigate"}],
        status="pending",
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    result = await test_db.execute(select(Task).where(Task.id == task.id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.name == "DB Test Task"
    assert fetched.status == "pending"
