from ai_self_healing.browser_collector import collect_browser_data
from ai_self_healing.vision_analyzer import analyze_ui_screenshot


def test_vision_analyzer():

    print("\nCollecting browser data...")

    browser_data = collect_browser_data("https://example.com")

    print("\nSending screenshot and DOM to Gemini Vision AI...")

    result = analyze_ui_screenshot(
        screenshot_path=browser_data["screenshot_path"],
        error_message="Test error: Login button locator not found",
        dom_content=browser_data["dom_content"]
    )

    print("\n========== GEMINI VISION ANALYSIS ==========")
    print(result)

    assert result is not None
    assert len(result) > 0