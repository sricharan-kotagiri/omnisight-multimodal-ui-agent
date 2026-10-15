
from bs4 import BeautifulSoup


def validate_locator(locator, dom_content):

    if not locator:
        return {
            "valid": False,
            "message": "Locator is empty"
        }

    if not dom_content:
        return {
            "valid": False,
            "message": "DOM content is empty"
        }

    try:
        soup = BeautifulSoup(dom_content, "html.parser")

        # CSS ID selector
        if locator.startswith("#"):
            element = soup.find(id=locator[1:])

        # CSS class selector
        elif locator.startswith("."):
            element = soup.find(
                class_=locator[1:]
            )

        # HTML tag selector
        else:
            element = soup.find(locator)

        if element:
            return {
                "valid": True,
                "message": "Locator found in DOM",
                "element": element.name
            }

        return {
            "valid": False,
            "message": "Locator not found in DOM"
        }

    except Exception as error:
        return {
            "valid": False,
            "message": str(error)
        }
