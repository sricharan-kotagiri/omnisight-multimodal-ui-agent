
from ai_self_healing.code_extractor import extract_code_block


def test_extract_css_from_explanatory_response():
    ai_response = (
        "The submit button is hidden.\n"
        "```css\n"
        ".submit-button {\n"
        "    visibility: visible;\n"
        "    display: block;\n"
        "}\n"
        "```\n"
        "This fix makes the button visible."
    )

    extracted = extract_code_block(ai_response)

    assert extracted == (
        ".submit-button {\n"
        "    visibility: visible;\n"
        "    display: block;\n"
        "}"
    )


def test_extract_react_from_explanatory_response():
    ai_response = (
        "Replace the broken button with this component.\n"
        "```jsx\n"
        "<button className=\"submit-button\">\n"
        "    Create Account\n"
        "</button>\n"
        "```\n"
        "This restores the primary action."
    )

    extracted = extract_code_block(ai_response)

    assert extracted == (
        '<button className="submit-button">\n'
        "    Create Account\n"
        "</button>"
    )
