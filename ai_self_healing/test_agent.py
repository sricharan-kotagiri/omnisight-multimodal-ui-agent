
from pathlib import Path
from playwright.sync_api import sync_playwright

from ai_self_healing.self_healing_agent import recover_failed_locator


html_path = Path("ai_self_healing/demo_site/login.html").resolve()
url = html_path.as_uri()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)

    print("Starting reusable self-healing agent...")

    result = recover_failed_locator(
        page=page,
        failed_locator="#login-btn",
        screenshot_path="artifacts/agent_recovery.png"
    )

    print("\n========== AGENT RESULT ==========")
    print(result)

    print("\nSuccess:", result["success"])

    if result["success"]:
        print("Message:", page.locator("#message").inner_text())

    page.wait_for_timeout(3000)
    browser.close()
