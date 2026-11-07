from playwright.sync_api import sync_playwright

from ai_self_healing.ui_patcher import apply_approved_button_fix


HTML = """
<html>
<body>
    <div class="form-box">
        <button class="submit-button"
                style="display: none;">
            Submit
        </button>
    </div>
</body>
</html>
"""


def test_patch_requires_human_approval():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(HTML)

        result = apply_approved_button_fix(
            page,
            approved=False
        )

        assert result["success"] is False
        assert result["validation"] == "not_run"
        assert not page.locator(".submit-button").is_visible()

        browser.close()


def test_approved_patch_reveals_hidden_button():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(HTML)

        result = apply_approved_button_fix(
            page,
            approved=True
        )

        assert result["success"] is True
        assert result["before"] == "hidden"
        assert result["after"] == "visible"
        assert result["validation"] == "passed"

        button = page.locator(".submit-button")

        assert button.count() == 1
        assert button.is_visible()
        assert button.is_enabled()

        browser.close()


def test_approved_patch_creates_missing_button():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.set_content("""
        <html>
        <body>
            <div class="form-box"></div>
        </body>
        </html>
        """)

        result = apply_approved_button_fix(
            page,
            approved=True
        )

        assert result["success"] is True
        assert result["before"] == "missing"
        assert result["repair_action"] == "created"

        button = page.locator(".submit-button")

        assert button.count() == 1
        assert button.is_visible()
        assert button.is_enabled()

        browser.close()