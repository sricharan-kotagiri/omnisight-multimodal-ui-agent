from playwright.sync_api import Page

from ai_self_healing.self_healing_agent import recover_failed_locator
from ai_self_healing.ui_patcher import apply_approved_button_fix


def recover_and_patch_ui(
    page: Page,
    failed_locator: str,
    screenshot_path: str,
    approved: bool = False
):
    # Step 1: Try AI-based locator recovery
    recovery_result = recover_failed_locator(
        page,
        failed_locator,
        screenshot_path
    )

    # Step 2: If AI recovery succeeds, stop here
    if recovery_result["success"]:
        return {
            "success": True,
            "stage": "locator_recovery",
            "message": "AI locator recovery successful",
            "recovery_result": recovery_result
        }

    # Step 3: AI recovery failed - request human approval
    if not approved:
        return {
            "success": False,
            "stage": "approval_required",
            "message": "AI recovery failed. Human approval is required before UI patching.",
            "recovery_result": recovery_result,
            "patch_result": None
        }

    # Step 4: Apply approved UI patch
    patch_result = apply_approved_button_fix(
        page,
        approved=True
    )

    # Step 5: Return combined result
    return {
        "success": patch_result["success"],
        "stage": "ui_patching",
        "message": patch_result["message"],
        "recovery_result": recovery_result,
        "patch_result": patch_result
    }