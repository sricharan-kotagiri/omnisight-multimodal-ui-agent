from pathlib import Path
from ai_self_healing.browser_collector import collect_browser_data


def test_browser_collector():

    result = collect_browser_data("https://example.com")

    assert result["url"] == "https://example.com"
    assert len(result["dom_content"]) > 0
    assert Path(result["screenshot_path"]) == Path("artifacts/page_screenshot.png")

    print("Browser Collector Test Passed!")