from ai_self_healing.validator import validate_locator
import re


def extract_suggested_locator(ai_response):

    if not ai_response:
        raise ValueError("AI response is empty")

    match = re.search(
        r"Suggested Locator:\s*`?([^`\n]+)`?",
        ai_response,
        re.IGNORECASE
    )

    if not match:
        raise ValueError("Suggested locator not found")

    locator = match.group(1).strip().strip("\"'")

    # Remove Playwright locator() wrapper
    wrapper_match = re.fullmatch(
        r'(?:page\.)?locator\(\s*([\'"])(.*?)\1\s*\)',
        locator
    )

    if wrapper_match:
        locator = wrapper_match.group(2)

    return locator


def create_recovery_plan(ai_response, dom_content):

    locator = extract_suggested_locator(ai_response)

    validation = validate_locator(
        locator,
        dom_content
    )

    return {
        "suggested_locator": locator,
        "validation": validation,
        "status": (
            "ready_for_browser_retry"
            if validation["valid"]
            else "validation_failed"
        )
    }