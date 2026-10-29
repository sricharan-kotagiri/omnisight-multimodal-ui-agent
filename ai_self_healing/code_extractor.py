import re


def extract_code_block(ai_response):
    pattern = r"```(?:css|react|jsx|javascript|js|html)?\s*(.*?)```"
    matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)

    if not matches:
        return None

    return matches[0].strip()