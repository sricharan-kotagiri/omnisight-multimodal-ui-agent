"""Unit tests for DOM locator validation engine."""
import pytest
from ai_self_healing.validator import validate_locator


def test_unique_css_selector(sample_dom):
    """Verify unique selector matches exactly one element."""
    result = validate_locator("#signin-btn", sample_dom)
    assert result["valid"] is True
    assert result["match_count"] == 1
    assert result["element"] == "button"


def test_ambiguous_css_selector(sample_dom):
    """Verify duplicate elements are rejected as ambiguous."""
    result = validate_locator(".duplicate-item", sample_dom)
    assert result["valid"] is False
    assert result["match_count"] == 2
    assert "ambiguous" in result["message"].lower()


def test_missing_element_in_dom(sample_dom):
    """Verify non-existent selector returns valid=False with match_count=0."""
    result = validate_locator("#non-existent-btn", sample_dom)
    assert result["valid"] is False
    assert result["match_count"] == 0


def test_empty_locator():
    """Verify empty locator string is rejected."""
    result = validate_locator("", "<html><body></body></html>")
    assert result["valid"] is False
    assert "empty" in result["message"].lower()


def test_empty_dom():
    """Verify empty DOM content is rejected."""
    result = validate_locator("#btn", "")
    assert result["valid"] is False
    assert "empty" in result["message"].lower()
