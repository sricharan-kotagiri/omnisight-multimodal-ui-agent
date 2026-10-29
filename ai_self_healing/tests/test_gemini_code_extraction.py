
from ai_self_healing.config import client
from ai_self_healing.code_extractor import extract_code_block


def test_gemini_code_extraction():
    prompt = """
A web page has a hidden submit button.

Explain the issue briefly and suggest a CSS fix.

IMPORTANT:
- Return the CSS fix inside a fenced CSS code block.
- Include a visibility: visible rule.
- Do not omit the CSS code block.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    ai_response = response.text

    print("\n===== GEMINI ORIGINAL RESPONSE =====")
    print(ai_response)

    extracted_code = extract_code_block(ai_response)

    print("\n===== EXTRACTED CODE ONLY =====")
    print(extracted_code)

    assert extracted_code is not None
    assert "visibility: visible" in extracted_code
    assert "```" not in extracted_code
