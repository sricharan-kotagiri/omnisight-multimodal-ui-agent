
from ai_self_healing.validator import validate_locator


dom_content = """
<html>
<body>
    <button id="signin-btn">Login</button>
    <button id="signin-btn">Sign In</button>
</body>
</html>
"""

# Test 1: Duplicate locator
result = validate_locator("#signin-btn", dom_content)

print("Duplicate Locator Test:")
print(result)

assert result["valid"] is False
assert result["match_count"] == 2

print("Duplicate locator correctly rejected!")


# Test 2: Unique locator
unique_dom = """
<html>
<body>
    <button id="signin-btn">Login</button>
</body>
</html>
"""

result = validate_locator("#signin-btn", unique_dom)

print("\nUnique Locator Test:")
print(result)

assert result["valid"] is True
assert result["match_count"] == 1

print("Unique locator successfully validated!")
