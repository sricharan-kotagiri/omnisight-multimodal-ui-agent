"""End-to-End browser test for the OmniSight demo login page."""
import pytest
from playwright.sync_api import sync_playwright, TimeoutError


def test_demo_site_locator_healing(demo_html_uri):
    """
    E2E scenario:
    1. Open local demo login page in headless Chromium.
    2. Try old broken locator '#login-btn' -> expect TimeoutError.
    3. Click the updated locator '#signin-btn' -> success.
    4. Verify success message appears on page.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Step 1: Open demo page
        page.goto(demo_html_uri)

        # Step 2: Attempt broken locator
        with pytest.raises(TimeoutError):
            page.locator("#login-btn").click(timeout=1500)

        # Step 3: Use replacement locator
        healed_button = page.locator("#signin-btn")
        assert healed_button.count() == 1
        assert healed_button.is_visible()
        healed_button.click()

        # Step 4: Verify result text
        message_elem = page.locator("#message")
        assert "Login button clicked successfully" in message_elem.inner_text()

        browser.close()
