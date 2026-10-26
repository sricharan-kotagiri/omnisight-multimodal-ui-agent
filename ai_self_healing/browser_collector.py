from playwright.sync_api import sync_playwright
from pathlib import Path


def collect_browser_data(url):

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_timeout(2000)

        dom_content = page.content()

        screenshot_path = artifacts_dir / "page_screenshot.png"

        page.screenshot(path=str(screenshot_path), full_page=True)

        browser.close()

    return {
        "url": url,
        "dom_content": dom_content,
        "screenshot_path": str(screenshot_path)
    }