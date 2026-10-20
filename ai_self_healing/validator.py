from bs4 import BeautifulSoup


def validate_locator(locator, dom_content):

    # Step 1: Check locator
    if not locator:
        return {
            "valid": False,
            "message": "Locator is empty",
            "match_count": 0
        }

    # Step 2: Check DOM content
    if not dom_content:
        return {
            "valid": False,
            "message": "DOM content is empty",
            "match_count": 0
        }

    # Step 3: Parse HTML
    try:
        soup = BeautifulSoup(dom_content, "html.parser")

        # Step 4: Find matching elements
        elements = soup.select(locator)

        match_count = len(elements)

        # Step 5: No matching element
        if match_count == 0:
            return {
                "valid": False,
                "message": "Locator not found in DOM",
                "match_count": 0
            }

        # Step 6: Multiple matching elements
        if match_count > 1:
            return {
                "valid": False,
                "message": "Locator is ambiguous",
                "match_count": match_count
            }

        # Step 7: Exactly one matching element
        return {
            "valid": True,
            "message": "Unique locator found in DOM",
            "element": elements[0].name,
            "match_count": 1
        }

    except Exception as error:

        return {
            "valid": False,
            "message": str(error),
            "match_count": 0
        }