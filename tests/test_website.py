
from playwright.sync_api import Page, expect


def test_example_website_title(page: Page):
    page.goto("https://example.com")

    expect(page).to_have_title("Example Domain")
    expect(page.get_by_role("heading", name="Example Domain")).to_be_visible()
