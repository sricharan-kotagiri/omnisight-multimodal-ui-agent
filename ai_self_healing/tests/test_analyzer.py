
from ai_self_healing.analyzer import analyze_ui_failure

# Step 1: Browser automation failure
error_message = """
TimeoutError: Element with selector '#login-btn' not found.
"""

# Step 2: Current webpage DOM content
dom_content = """
<html>
<head>
    <title>Login Page</title>
</head>
<body>
    <h1>Welcome</h1>
    <button id="signin-btn">Login</button>
</body>
</html>
"""

# Step 3: Send error and DOM to Gemini AI
print("\nAnalyzing UI failure using Gemini AI...")

result = analyze_ui_failure(
    error_message,
    dom_content
)

# Step 4: Display AI analysis
print("\n========== AI ANALYSIS RESULT ==========")
print(result)
print("========================================")
