from pathlib import Path

from playwright.sync_api import Page, TimeoutError

from ai_self_healing.vision_analyzer import analyze_ui_screenshot
from ai_self_healing.recovery import create_recovery_plan


def recover_failed_locator(
    page: Page,
    failed_locator: str,
    screenshot_path: str
):

    try:
        page.locator(failed_locator).click(timeout=3000)

        return {
            "success": True,
            "message": "Original locator worked"
        }

    except TimeoutError as error:

        browser_error = str(error)

        dom_content = page.content()

        image_path = Path(screenshot_path)
        image_path.parent.mkdir(exist_ok=True)

        page.screenshot(
            path=str(image_path),
            full_page=True
        )

        ai_response = analyze_ui_screenshot(
            screenshot_path,
            browser_error,
            dom_content
        )

        recovery_plan = create_recovery_plan(
            ai_response,
            dom_content
        )

        if not recovery_plan["validation"]["valid"]:
            return {
                "success": False,
                "message": "AI suggested locator is invalid",
                "recovery_plan": recovery_plan
            }

        new_locator = recovery_plan["suggested_locator"]

        try:
            page.locator(new_locator).click(timeout=5000)

            return {
                "success": True,
                "message": "Self-healing successful",
                "old_locator": failed_locator,
                "new_locator": new_locator,
                "recovery_plan": recovery_plan
            }

        except TimeoutError:

            return {
                "success": False,
                "message": "AI locator could not be clicked",
                "old_locator": failed_locator,
                "new_locator": new_locator,
                "recovery_plan": recovery_plan
            }