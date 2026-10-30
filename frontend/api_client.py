"""HTTP client for the OmniSight FastAPI self-healing service."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests


class ApiClientError(RuntimeError):
    """Raised when the API cannot be reached or its response cannot be read."""


def _request_json(method: str, url: str, *, timeout: float = 20, **kwargs: Any) -> dict[str, Any]:
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        raise ApiClientError(
            "Could not reach the OmniSight API. Check that the backend is running and the address is correct."
        ) from exc

    if not response.ok:
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail") or payload.get("message") or "")
        except ValueError:
            detail = response.text[:300]
        message = f"API returned HTTP {response.status_code}."
        raise ApiClientError(f"{message} {detail}" if detail else message)

    try:
        payload = response.json()
    except ValueError as exc:
        raise ApiClientError("The API response was not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ApiClientError("The API should return a JSON object.")
    return payload


def get_health(api_base_url: str) -> dict[str, Any]:
    """Read the backend health endpoint."""
    base_url = api_base_url.strip().rstrip("/")
    if not base_url:
        raise ApiClientError("Enter the address of the OmniSight API.")
    return _request_json("GET", f"{base_url}/health", timeout=5)


def get_api_paths(api_base_url: str) -> dict[str, Any]:
    """Read the operations currently published in FastAPI's OpenAPI document."""
    base_url = api_base_url.strip().rstrip("/")
    if not base_url:
        raise ApiClientError("Enter the address of the OmniSight API.")

    document = _request_json("GET", f"{base_url}/openapi.json", timeout=5)
    paths = document.get("paths")
    if not isinstance(paths, dict):
        raise ApiClientError("The backend OpenAPI document did not contain an API paths object.")
    return paths


def recover_locator(api_base_url: str, site_url: str, failed_locator: str) -> dict[str, Any]:
    """Submit a locator recovery request matching api.models.schemas.RecoveryRequest."""
    parsed = urlparse(site_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ApiClientError("Enter a complete website address starting with http:// or https://.")
    if not failed_locator.strip():
        raise ApiClientError("Enter the Playwright locator that failed.")

    base_url = api_base_url.strip().rstrip("/")
    if not base_url:
        raise ApiClientError("Enter the address of the OmniSight API.")

    return _request_json(
        "POST",
        f"{base_url}/recover",
        json={"url": site_url.strip(), "failed_locator": failed_locator.strip()},
    )
