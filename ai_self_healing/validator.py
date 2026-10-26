
from bs4 import BeautifulSoup
from lxml import etree
import re


def validate_locator(locator, dom_content):

    if not locator:
        return {
            "valid": False,
            "message": "Locator is empty",
            "match_count": 0
        }

    if not dom_content:
        return {
            "valid": False,
            "message": "DOM content is empty",
            "match_count": 0
        }

    try:

        soup = BeautifulSoup(dom_content, "html.parser")

        # Detect XPath locator
        if locator.startswith("/") or locator.startswith("("):

            parser = etree.HTMLParser()
            tree = etree.HTML(dom_content, parser)

            elements = tree.xpath(locator)

            match_count = len(elements)

            if match_count == 0:
                return {
                    "valid": False,
                    "message": "XPath locator not found in DOM",
                    "match_count": 0
                }

            if match_count > 1:
                return {
                    "valid": False,
                    "message": "XPath locator is ambiguous",
                    "match_count": match_count
                }

            return {
                "valid": True,
                "message": "Unique XPath locator found in DOM",
                "element": elements[0].tag,
                "match_count": 1
            }

        # CSS selector validation
        elements = soup.select(locator)
        match_count = len(elements)

        if match_count == 0:
            return {
                "valid": False,
                "message": "Locator not found in DOM",
                "match_count": 0
            }

        if match_count > 1:
            return {
                "valid": False,
                "message": "Locator is ambiguous",
                "match_count": match_count
            }

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
