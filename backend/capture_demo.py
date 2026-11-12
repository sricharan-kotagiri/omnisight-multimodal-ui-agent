from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5173"

# Teen screen sizes: phone, tablet, laptop
VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}

OUT_DIR = Path("artifacts")


def wait_for_page(page, heading):
    """Tab tak ruko jab tak page ka heading screen par aa na jaye."""
    page.get_by_role("heading", name=heading, exact=True).wait_for()
    page.wait_for_timeout(300)  # thoda extra time, styles settle hone ke liye


def capture_flow(bug=None):
    """Shop kholo, Home -> Cart -> Checkout tak jao, har page ka screenshot lo."""
    suffix = f"?bug={bug}" if bug else ""
    folder_name = bug or "clean"

    with sync_playwright() as p:
        browser = p.chromium.launch()  # headless = bina window ke

        for vp_name, size in VIEWPORTS.items():
            context = browser.new_context(viewport=size)
            page = context.new_page()

            folder = OUT_DIR / folder_name / vp_name
            folder.mkdir(parents=True, exist_ok=True)

            # 1) Home page
            page.goto(f"{BASE_URL}/{suffix}")
            wait_for_page(page, "Products")
            page.screenshot(path=str(folder / "1_home.png"), full_page=True)

            # 2) "Add to cart" dabao -> Cart page
            page.get_by_text("Add to cart").first.click()
            wait_for_page(page, "Your Cart")
            page.screenshot(path=str(folder / "2_cart.png"), full_page=True)

            # 3) "Go to checkout" dabao -> Checkout page
            page.get_by_text("Go to checkout").click()
            wait_for_page(page, "Checkout")
            page.screenshot(path=str(folder / "3_checkout.png"), full_page=True)

            context.close()

        browser.close()


if __name__ == "__main__":
    # None = bina bug wali clean site
    for bug in [None, "overlap", "low-contrast", "hidden-button", "clipped-button"]:
        print("Capturing:", bug or "clean")
        capture_flow(bug)
    print("Done! Check the artifacts folder.")