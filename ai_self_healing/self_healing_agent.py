
from pathlib import Path

from playwright.sync_api import Page, TimeoutError, Error as PlaywrightError

from ai_self_healing.vision_analyzer import analyze_ui_screenshot
from ai_self_healing.recovery import create_recovery_plan


def validate_browser_locator(page: Page, locator: str):

    try:
        element = page.locator(locator)

        # Check 1: Element count
        count = element.count()

        if count == 0:
            return {
                "valid": False,
                "message": "Element not found in browser",
                "match_count": count
            }

        if count > 1:
            return {
                "valid": False,
                "message": "Multiple elements found in browser",
                "match_count": count
            }

        # Check 2: Visibility
        if not element.is_visible():
            return {
                "valid": False,
                "message": "Element is not visible",
                "match_count": count
            }

        # Check 3: Enabled state
        if not element.is_enabled():
            return {
                "valid": False,
                "message": "Element is disabled",
                "match_count": count
            }

        return {
            "valid": True,
            "message": "Element is unique, visible and enabled",
            "match_count": count
        }

    except PlaywrightError as error:
        return {
            "valid": False,
            "message": str(error),
            "match_count": 0
        }


def recover_failed_locator(
    page: Page,
    failed_locator: str,
    screenshot_path: str
):

    original_check = validate_browser_locator(
        page,
        failed_locator
    )

    if original_check["valid"]:

        try:
            page.locator(failed_locator).click(timeout=3000)

            return {
                "success": True,
                "message": "Original locator worked",
                "browser_validation": original_check
            }

        except TimeoutError as error:
            browser_error = str(error)

    else:
        browser_error = original_check["message"]

    dom_content = page.content()

    image_path = Path(screenshot_path)
    image_path.parent.mkdir(parents=True, exist_ok=True)

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

    # Validate AI locator in the actual browser
    browser_validation = validate_browser_locator(
        page,
        new_locator
    )

    if not browser_validation["valid"]:
        return {
            "success": False,
            "message": "AI locator failed browser validation",
            "browser_validation": browser_validation,
            "recovery_plan": recovery_plan
        }

    try:
        page.locator(new_locator).click(timeout=5000)

        return {
            "success": True,
            "message": "Self-healing successful",
            "old_locator": failed_locator,
            "new_locator": new_locator,
            "browser_validation": browser_validation,
            "recovery_plan": recovery_plan
        }

    except TimeoutError:

        return {
            "success": False,
            "message": "AI locator could not be clicked",
            "old_locator": failed_locator,
            "new_locator": new_locator,
            "browser_validation": browser_validation,
            "recovery_plan": recovery_plan
        }
