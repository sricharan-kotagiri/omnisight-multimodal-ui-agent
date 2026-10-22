
from playwright.sync_api import Page, expect


def test_example_website_title(page: Page):
    page.goto("https://example.com")

    expect(page).to_have_title("Example Domain")


def test_example_website_heading(page: Page):
    page.goto("https://example.com")

    heading = page.get_by_role("heading", name="Example Domain")
    expect(heading).to_be_visible()


def test_example_website_has_description(page: Page):
    page.goto("https://example.com")

    description = page.locator("p")
    expect(description.first).to_be_visible()
    expect(description.first).not_to_be_empty()
