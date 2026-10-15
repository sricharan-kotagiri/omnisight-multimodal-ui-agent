
from ai_self_healing.config import client


def analyze_ui_failure(error_message, dom_content):

    prompt = f"""
You are an AI UI self-healing agent.

Analyze the browser automation failure using the error message and DOM.

ERROR:
{error_message}

DOM:
{dom_content}

Identify:
1. What caused the failure
2. Which UI element is affected
3. A reliable alternative locator
4. Why the alternative locator should work

Return the answer in this format:

Problem:
Affected Element:
Suggested Locator:
Reason:
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text
