
from ai_self_healing.config import client
from ai_self_healing.prompt import build_vision_prompt
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

    prompt = build_vision_prompt(
        browser_error=error_message,
        dom_content=dom_content[:12000]
    )

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
