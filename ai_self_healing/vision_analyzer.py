from ai_self_healing.config import client
from google.genai import types
from pathlib import Path


def analyze_ui_screenshot(
    screenshot_path,
    error_message,
    dom_content
):

    image_path = Path(screenshot_path)

    if not image_path.exists():
        raise FileNotFoundError("Screenshot not found!")

    prompt = f"""
You are a Multimodal AI UI Self-Healing Agent.

Analyze the website screenshot and DOM content.

BROWSER ERROR:
{error_message}

DOM CONTENT:
{dom_content[:12000]}

Identify:
1. What visual or UI issue is visible?
2. Which UI element is affected?
3. What could have caused the browser failure?
4. Suggest a reliable alternative locator using the DOM.

Return:

Visual Issue:
Affected Element:
Possible Cause:
Suggested Locator:
Reason:
"""

    image_part = types.Part.from_bytes(
        data=image_path.read_bytes(),
        mime_type="image/png"
    )

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=[
            prompt,
            image_part
        ]
    )

    return response.text