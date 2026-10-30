
from ai_self_healing.recovery import create_recovery_plan

# Sample Gemini response
ai_response = """
Problem:
The login button was not found.

Affected Element:
Login button.

Suggested Locator:
`#signin-btn`

Reason:
The DOM contains a button with this ID.
"""

# Sample webpage DOM
dom_content = """
<html>
<body>
    <h1>Welcome</h1>
    <button id="signin-btn">Login</button>
</body>
</html>
"""

print("\nStarting Recovery Process...")

recovery_plan = create_recovery_plan(
    ai_response,
    dom_content
)

print("\n========== RECOVERY RESULT ==========")

for key, value in recovery_plan.items():
    print(f"{key}: {value}")

print("=====================================")
