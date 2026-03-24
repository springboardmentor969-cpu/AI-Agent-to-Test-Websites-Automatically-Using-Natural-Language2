"""
Tests for generator/assertion_generator.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.assertion_generator import generate_assertion


def test_visible_assertion():
    action = {"selector": "#dashboard", "condition": "visible"}
    result = generate_assertion(action)
    assert result == 'expect(page.locator("#dashboard")).to_be_visible()'
    print("✅  test_visible_assertion passed")


def test_text_present_assertion():
    action = {"selector": "#message", "condition": "text_present", "value": "Welcome"}
    result = generate_assertion(action)
    assert result == 'expect(page.locator("#message")).to_contain_text("Welcome")'
    print("✅  test_text_present_assertion passed")


def test_url_contains_assertion():
    action = {"condition": "url_contains", "value": "dashboard"}
    result = generate_assertion(action)
    assert result == 'expect(page).to_have_url(re.compile(r"dashboard"))'
    print("✅  test_url_contains_assertion passed")


def test_default_condition_is_visible():
    action = {"selector": "#elem"}
    result = generate_assertion(action)
    assert "to_be_visible" in result
    print("✅  test_default_condition_is_visible passed")


def test_unsupported_condition_raises():
    action = {"selector": "#x", "condition": "color_is_red"}
    try:
        generate_assertion(action)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported assertion condition" in str(e)
    print("✅  test_unsupported_condition_raises passed")


if __name__ == "__main__":
    test_visible_assertion()
    test_text_present_assertion()
    test_url_contains_assertion()
    test_default_condition_is_visible()
    test_unsupported_condition_raises()
    print("\n🎉  All assertion generator tests passed!")
