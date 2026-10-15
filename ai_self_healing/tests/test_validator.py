
from ai_self_healing.validator import validate_locator

# Sample webpage DOM
dom_content = """
<html>
<body>
    <h1>Welcome</h1>
    <button id="signin-btn">Login</button>
    <button class="signup-btn">Sign Up</button>
</body>
</html>
"""

# Test 1: Existing ID
print("\n========== TEST 1: ID LOCATOR ==========")

result = validate_locator("#signin-btn", dom_content)
print(result)

# Test 2: Existing class
print("\n========== TEST 2: CLASS LOCATOR ==========")

result = validate_locator(".signup-btn", dom_content)
print(result)

# Test 3: Missing ID
print("\n========== TEST 3: INVALID LOCATOR ==========")

result = validate_locator("#login-btn", dom_content)
print(result)
