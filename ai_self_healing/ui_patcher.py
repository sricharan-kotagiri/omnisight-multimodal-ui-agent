
from playwright.sync_api import Page


def apply_approved_button_fix(
    page: Page,
    approved: bool = False
):
    if not approved:
        return {
            "success": False,
            "message": "Human approval is required before applying the fix"
        }

    container = page.locator(".form-box")

    if container.count() != 1:
        return {
            "success": False,
            "message": "Form container not found or ambiguous"
        }

    button = page.locator(".submit-button")

    if button.count() == 0:
        container.evaluate("""
            (element) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "submit-button";
                button.textContent = "Create Account";
                element.appendChild(button);
            }
        """)

    elif button.count() == 1:
        button.evaluate("""
            (element) => {
                element.textContent = "Create Account";
                element.style.visibility = "visible";
                element.style.display = "block";
                element.style.opacity = "1";
                element.style.pointerEvents = "auto";
            }
        """)
    else:
        return {
            "success": False,
            "message": "Multiple submit buttons found"
        }

    repaired_button = page.locator(".submit-button")

    repaired_button.evaluate("""
        (element) => {
            element.style.width = "100%";
            element.style.padding = "12px";
            element.style.background = "#2563eb";
            element.style.color = "white";
            element.style.border = "none";
            element.style.borderRadius = "6px";
            element.style.cursor = "pointer";
            element.style.visibility = "visible";
            element.style.display = "block";
            element.style.opacity = "1";
        }
    """)

    if not repaired_button.is_visible():
        return {
            "success": False,
            "message": "Button is still not visible"
        }

    if not repaired_button.is_enabled():
        return {
            "success": False,
            "message": "Button is disabled"
        }

    return {
        "success": True,
        "message": "UI repair successful. Button is visible and enabled.",
        "button_text": repaired_button.inner_text()
    }
