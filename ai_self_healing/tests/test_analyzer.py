
from unittest.mock import patch, MagicMock
from ai_self_healing.analyzer import analyze_ui_failure


def test_analyze_ui_failure():

    error_message = "TimeoutError: #login-btn not found."

    dom_content = '<button id="signin-btn">Login</button>'

    mock_response = MagicMock()
    mock_response.text = """
    Problem: Login button locator changed.
    Affected Element: Login button
    Suggested Locator: #signin-btn
    Reason: The button exists in the DOM.
    """

    with patch(
        "ai_self_healing.analyzer.client.models.generate_content",
        return_value=mock_response
    ) as mock_gemini:

        result = analyze_ui_failure(error_message, dom_content)

        assert result is not None
        assert "#signin-btn" in result
        mock_gemini.assert_called_once()
