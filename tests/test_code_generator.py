"""
Tests for generator/code_generator.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.code_generator import generate_playwright_code, _is_youtube_url


# ─── YouTube detection ────────────────────────────────────────────────────────

def test_youtube_detection():
    assert _is_youtube_url("https://www.youtube.com") is True
    assert _is_youtube_url("https://youtu.be/xyz") is True
    assert _is_youtube_url("https://www.google.com") is False
    print("✅  test_youtube_detection passed")


# ─── Basic form actions ──────────────────────────────────────────────────────

def test_form_actions():
    actions = [
        {"type": "navigate", "url": "http://localhost:5000"},
        {"type": "input", "selector": "#username", "value": "admin"},
        {"type": "input", "selector": "#password", "value": "1234"},
        {"type": "click", "selector": "#login"},
        {"type": "assert", "selector": "#dashboard", "condition": "visible"},
    ]
    script, requires_headed = generate_playwright_code(actions)

    # Should NOT require headed mode (no YouTube URL)
    assert requires_headed is False, f"Expected headless but got headed"

    # Script should use sync API
    assert "sync_playwright" in script
    assert "headless=True" in script

    # Script should contain expected operations
    assert 'page.goto("http://localhost:5000")' in script
    assert 'page.locator("#username").fill("admin")' in script
    assert 'page.locator("#password").fill("1234")' in script
    assert 'page.locator("#login").click()' in script
    assert 'expect(page.locator("#dashboard")).to_be_visible()' in script

    print("✅  test_form_actions passed")


# ─── YouTube actions ─────────────────────────────────────────────────────────

def test_youtube_actions():
    actions = [
        {"type": "navigate", "url": "https://www.youtube.com"},
        {"type": "input", "selector": "input[name='search_query']", "value": "lofi music"},
        {"type": "press", "key": "Enter"},
        {"type": "click", "selector": "ytd-video-renderer a#thumbnail"},
        {"type": "wait", "duration": 5000},
    ]
    script, requires_headed = generate_playwright_code(actions)

    # Should require headed mode
    assert requires_headed is True, "Expected headed mode for YouTube"

    # Should use headed settings
    assert "headless=False" in script
    assert "slow_mo=100" in script

    # Should contain YouTube-specific code
    assert "video_clicked" in script  # fallback selector logic
    assert 'page.keyboard.press("Enter")' in script
    assert "page.wait_for_timeout(5000)" in script

    print("✅  test_youtube_actions passed")


# ─── Assertion types ─────────────────────────────────────────────────────────

def test_assertion_types():
    actions = [
        {"type": "navigate", "url": "http://example.com"},
        {"type": "assert", "selector": "#el", "condition": "visible"},
        {"type": "assert", "selector": "#msg", "condition": "text_present", "value": "Hello"},
        {"type": "assert", "condition": "url_contains", "value": "example"},
    ]
    script, _ = generate_playwright_code(actions)

    assert 'expect(page.locator("#el")).to_be_visible()' in script
    assert 'expect(page.locator("#msg")).to_contain_text("Hello")' in script
    assert 'expect(page).to_have_url(re.compile(r"example"))' in script
    assert "import re" in script

    print("✅  test_assertion_types passed")


# ─── Wait and press ──────────────────────────────────────────────────────────

def test_wait_and_press():
    actions = [
        {"type": "navigate", "url": "http://example.com"},
        {"type": "press", "key": "Tab"},
        {"type": "wait", "duration": 2000},
    ]
    script, requires_headed = generate_playwright_code(actions)

    assert requires_headed is False
    assert 'page.keyboard.press("Tab")' in script
    assert "page.wait_for_timeout(2000)" in script

    print("✅  test_wait_and_press passed")


# ─── Unknown action type ─────────────────────────────────────────────────────

def test_unknown_action():
    actions = [
        {"type": "navigate", "url": "http://example.com"},
        {"type": "hover", "selector": "#btn"},
    ]
    script, _ = generate_playwright_code(actions)
    assert "WARNING: unknown action type" in script
    print("✅  test_unknown_action passed")


if __name__ == "__main__":
    test_youtube_detection()
    test_form_actions()
    test_youtube_actions()
    test_assertion_types()
    test_wait_and_press()
    test_unknown_action()
    print("\n🎉  All code generator tests passed!")
