"""
Tests for the Healing API endpoints.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_healing_analyze_stub(test_client):
    """POST /healing/analyze returns the Phase 2 stub response."""
    payload = {
        "screenshot_b64": "aGVsbG8=",
        "original_locator": "#submit-btn",
        "failed_action": "click",
        "dom_snapshot": "<html></html>",
        "url": "https://example.com",
        "intended_action": "Click the submit button",
    }
    response = await test_client.post("/api/v1/healing/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "stub"
    assert "AI integration not yet connected" in data["reasoning"]
    assert data["suggested_locator"] is None
