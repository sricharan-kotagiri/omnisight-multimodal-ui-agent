"""Unit tests for the frontend API client (api_client.py)."""
import pytest
from api_client import ApiClientError, recover_locator, get_health, get_api_paths


def test_recover_locator_rejects_empty_locator():
    """Verify recover_locator raises ApiClientError when failed_locator is blank."""
    with pytest.raises(ApiClientError, match="Enter the Playwright locator that failed"):
        recover_locator(
            api_base_url="http://127.0.0.1:8000",
            site_url="https://example.com",
            failed_locator=""
        )


def test_recover_locator_rejects_invalid_url_scheme():
    """Verify recover_locator raises ApiClientError when URL lacks http:// or https://."""
    with pytest.raises(ApiClientError, match="Enter a complete website address"):
        recover_locator(
            api_base_url="http://127.0.0.1:8000",
            site_url="ftp://example.com",
            failed_locator="#button"
        )


def test_recover_locator_rejects_empty_base_url():
    """Verify recover_locator raises ApiClientError when API address is missing."""
    with pytest.raises(ApiClientError, match="Enter the address of the OmniSight API"):
        recover_locator(
            api_base_url="   ",
            site_url="https://example.com",
            failed_locator="#button"
        )


def test_get_health_rejects_empty_url():
    """Verify get_health raises error if API base URL is empty."""
    with pytest.raises(ApiClientError, match="Enter the address of the OmniSight API"):
        get_health("")
