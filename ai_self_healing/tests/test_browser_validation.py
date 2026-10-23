
from playwright.sync_api import sync_playwright

from ai_self_healing.self_healing_agent import validate_browser_locator


html = """
<html>
<body>
    <button id="visible-btn">Visible Button</button>

    <button id="hidden-btn" style="display: none;">
        Hidden Button
    </button>

    <button id="disabled-btn" disabled>
        Disabled Button
    </button>
</body>
</html>
"""


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.set_content(html)

    # Test 1: Visible element
    result = validate_browser_locator(
        page,
        "#visible-btn"
    )

    print("Visible Element Test:")
    print(result)

    assert result["valid"] is True
    assert result["match_count"] == 1

    # Test 2: Hidden element
    result = validate_browser_locator(
        page,
        "#hidden-btn"
    )

    print("\nHidden Element Test:")
    print(result)

    assert result["valid"] is False

    # Test 3: Disabled element
    result = validate_browser_locator(
        page,
        "#disabled-btn"
    )

    print("\nDisabled Element Test:")
    print(result)

    assert result["valid"] is False

    # Test 4: Duplicate elements
    page.set_content("""
    <html>
    <body>
        <button class="duplicate-btn">Button 1</button>
        <button class="duplicate-btn">Button 2</button>
    </body>
    </html>
    """)

    result = validate_browser_locator(
        page,
        ".duplicate-btn"
    )

    print("\nDuplicate Element Test:")
    print(result)

    assert result["valid"] is False
    assert result["match_count"] == 2

    # Test 5: Invalid locator
    result = validate_browser_locator(
        page,
        "button["
    )

    print("\nInvalid Locator Test:")
    print(result)

    assert result["valid"] is False

    print("\nAll browser validation tests passed!")

    browser.close()
