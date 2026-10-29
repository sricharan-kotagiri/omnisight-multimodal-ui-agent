from pathlib import Path
from ai_self_healing.config import client
from google.genai import types


def test_screenshot_only_vision_audit():
    screenshot_path = Path("artifacts/vision_audit.png")

    assert screenshot_path.exists()

    prompt = """
You are performing a screenshot-only UI visual audit.

Analyze ONLY the provided screenshot.

Do NOT assume or request HTML, DOM, CSS, source code, or locator information.

Identify any visible UI usability or visual problems.
Pay special attention to missing, hidden, clipped, overlapping, or inaccessible
interactive elements.

Return:
1. Visual issue detected
2. Evidence from the screenshot
3. Recommended UI fix

If an important interactive element appears to be missing or inaccessible,
clearly mention it.
"""

    image_part = types.Part.from_bytes(
        data=screenshot_path.read_bytes(),
        mime_type="image/png"
    )

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=[prompt, image_part]
    )

    print("\n===== SCREENSHOT-ONLY VISION AUDIT =====")
    print(response.text)
    print("=========================================\n")

    assert response.text