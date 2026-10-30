
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

html_path = Path("ai_self_healing/demo_site/login.html").resolve()
url = html_path.as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)

    print("Testing old locator: #login-btn")

    try:
        page.locator("#login-btn").click(timeout=3000)

    except TimeoutError:
        print("OLD LOCATOR FAILED!")
        print("UI element may have changed.")

    print("Testing new locator: #signin-btn")

    page.locator("#signin-btn").click()

    print("NEW LOCATOR WORKED!")

    print("Message:", page.locator("#message").inner_text())

    page.wait_for_timeout(3000)
    browser.close()
