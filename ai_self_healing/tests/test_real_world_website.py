
from playwright.sync_api import sync_playwright
from pathlib import Path

from ai_self_healing.self_healing_agent import recover_failed_locator


URL = "https://the-internet.herokuapp.com/add_remove_elements/"


def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        try:

            print("\n1. Opening real-world website...")

            page.goto(
                URL,
                wait_until="commit",
                timeout=60000
            )

            page.get_by_role(
                "button",
                name="Add Element"
            ).wait_for(
                state="visible",
                timeout=30000
            )

            print("Website opened successfully!")

            print("\n2. Checking actual Add Element button...")

            actual_button = page.get_by_role(
                "button",
                name="Add Element"
            )

            assert actual_button.count() == 1

            print("Actual button found!")

            print("\n3. Starting AI Self-Healing...")

            result = recover_failed_locator(
                page=page,
                failed_locator="#login-btn",
                screenshot_path="artifacts/real_world_recovery.png"
            )

            print("\n========== REAL WORLD RESULT ==========")

            print(result)

            if not result["success"]:

                print("\nSELF-HEALING FAILED!")
                print(result["message"])

                return

            print("\nSELF-HEALING SUCCESS!")

            print(
                "Recovered locator:",
                result["new_locator"]
            )

            print("\n4. Verifying actual browser result...")

            delete_buttons = page.get_by_role(
                "button",
                name="Delete"
            )

            actual_count = delete_buttons.count()

            print("Delete button count:", actual_count)

            assert actual_count >= 1, (
                "Add Element click did not create a Delete button"
            )

            print("\n===================================")
            print("REAL-WORLD TEST PASSED!")
            print("AI successfully recovered the failed locator.")
            print("Replacement locator was validated.")
            print("Add Element button was clicked.")
            print("Delete button appeared successfully.")
            print("===================================")

            page.screenshot(
                path="artifacts/real_world_success.png",
                full_page=True
            )

            page.wait_for_timeout(3000)

        except Exception as error:

            print("\nREAL-WORLD TEST ERROR:")
            print(error)

            raise

        finally:

            browser.close()


if __name__ == "__main__":
    main()
