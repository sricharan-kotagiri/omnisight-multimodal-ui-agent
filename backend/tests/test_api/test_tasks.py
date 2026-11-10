"""
Integration tests for the Task API endpoints.

All tests use the in-memory SQLite database injected via conftest.py fixtures.
"""

from __future__ import annotations

import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_health_check(test_client):
    """Health endpoint returns 200 with status=healthy."""
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


async def test_create_task_success(test_client, sample_task_data):
    """Valid task payload returns 201 with the created task."""
    response = await test_client.post("/api/v1/tasks", json=sample_task_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == sample_task_data["name"]
    assert data["status"] == "pending"


async def test_create_task_invalid_url_scheme(test_client):
    """Non-http/https URL scheme should be rejected with 400 or 422."""
    payload = {
        "name": "Bad URL Task",
        "target_url": "ftp://example.com",
        "actions": [{"type": "navigate"}],
    }
    response = await test_client.post("/api/v1/tasks", json=payload)
    assert response.status_code in (400, 422)


async def test_create_task_private_url(test_client):
    """Private IP target URL should be rejected with 400."""
    payload = {
        "name": "Private URL Task",
        "target_url": "http://192.168.1.1",
        "actions": [{"type": "navigate"}],
    }
    response = await test_client.post("/api/v1/tasks", json=payload)
    assert response.status_code in (400, 422)


async def test_create_task_empty_actions(test_client):
    """Empty actions list should return 422."""
    payload = {
        "name": "Empty Actions Task",
        "target_url": "https://example.com",
        "actions": [],
    }
    response = await test_client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


async def test_get_task_success(test_client, sample_task):
    """GET /tasks/{id} returns the task created in the fixture."""
    task_id = sample_task["id"]
    response = await test_client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id


async def test_get_task_not_found(test_client):
    """GET /tasks/{unknown_id} returns 404."""
    fake_id = str(uuid.uuid4())
    response = await test_client.get(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404


async def test_execute_task(test_client, sample_task):
    """POST /tasks/{id}/execute returns 202 with an execution message."""
    task_id = sample_task["id"]
    response = await test_client.post(f"/api/v1/tasks/{task_id}/execute")
    assert response.status_code == 202
    data = response.json()
    assert "message" in data


async def test_get_task_status(test_client, sample_task):
    """After execution, GET /tasks/{id}/status returns a status field."""
    task_id = sample_task["id"]
    # Trigger execution first
    exec_response = await test_client.post(f"/api/v1/tasks/{task_id}/execute")
    assert exec_response.status_code == 202
    # Status should now be available
    status_response = await test_client.get(f"/api/v1/tasks/{task_id}/status")
    assert status_response.status_code == 200
    data = status_response.json()
    assert "status" in data


async def test_get_task_logs(test_client, sample_task):
    """After execution, GET /tasks/{id}/logs returns at least one log entry."""
    task_id = sample_task["id"]
    # Trigger execution to generate logs
    await test_client.post(f"/api/v1/tasks/{task_id}/execute")
    # Retrieve logs
    logs_response = await test_client.get(f"/api/v1/tasks/{task_id}/logs")
    assert logs_response.status_code == 200
    data = logs_response.json()
    assert "logs" in data
    assert len(data["logs"]) >= 1


async def test_get_task_healing(test_client, sample_task):
    """GET /tasks/{id}/healing returns a healing history response (empty list is fine)."""
    task_id = sample_task["id"]
    await test_client.post(f"/api/v1/tasks/{task_id}/execute")
    response = await test_client.get(f"/api/v1/tasks/{task_id}/healing")
    assert response.status_code == 200
    data = response.json()
    assert "attempts" in data
