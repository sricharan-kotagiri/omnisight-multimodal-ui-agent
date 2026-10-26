
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

from ai_self_healing.vision_analyzer import analyze_ui_screenshot
from ai_self_healing.recovery import create_recovery_plan


html_path = Path("ai_self_healing/demo_site/login.html").resolve()
url = html_path.as_uri()

artifacts_dir = Path("artifacts")
artifacts_dir.mkdir(exist_ok=True)

screenshot_path = artifacts_dir / "recovery_screenshot.png"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)

    print("\n1. Testing old locator: #login-btn")

    try:
        page.locator("#login-btn").click(timeout=3000)

    except TimeoutError as error:

        print("2. Old locator failed!")

        browser_error = str(error)

        print("3. Collecting DOM and screenshot...")

        dom_content = page.content()

        page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        print("4. Sending data to Gemini Vision AI...")

        ai_response = analyze_ui_screenshot(
            screenshot_path,
            browser_error,
            dom_content
        )

        print("\n========== GEMINI AI ANALYSIS ==========")
        print(ai_response)

        print("\n5. Creating recovery plan...")

        recovery_plan = create_recovery_plan(
            ai_response,
            dom_content
        )

        print("\n========== RECOVERY PLAN ==========")
        print(recovery_plan)

        if recovery_plan["validation"]["valid"]:

            new_locator = recovery_plan["suggested_locator"]

            print("\n6. Retrying with:", new_locator)

            page.locator(new_locator).click(timeout=5000)

            print("7. SELF-HEALING SUCCESS!")

            print("Message:", page.locator("#message").inner_text())

        else:
            print("SELF-HEALING FAILED!")
            print("Locator validation failed.")

    page.wait_for_timeout(3000)
    browser.close()
