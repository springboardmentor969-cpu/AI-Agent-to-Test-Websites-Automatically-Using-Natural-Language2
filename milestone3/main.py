"""
Milestone 3 — Main Entry Point
--------------------------------
Provides the `run_test(actions_json)` API that orchestrates:
  1. Input validation
  2. YouTube auto-detection  →  headed mode
  3. Playwright execution via executor
  4. Standardised result reporting (PASS / FAIL)

Usage:
    from milestone3.main import run_test

    result = run_test({
        "actions": [
            {"type": "navigate", "url": "https://www.youtube.com"},
            {"type": "input", "selector": "input[name='search_query']", "value": "lofi music"},
            {"type": "press", "key": "Enter"},
            {"type": "wait", "duration": 3000},
            {"type": "click", "selector": "ytd-video-renderer a#thumbnail"},
            {"type": "wait", "duration": 5000}
        ]
    })
    print(result)
"""

import json
import sys
import os

# Add project root to path so imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executor.playwright_runner import execute_actions
from generator.code_generator import generate_playwright_code


def run_test(actions_json: dict) -> dict:
    """
    Public API — execute a structured test and return the result.

    Parameters
    ----------
    actions_json : dict
        Must contain an "actions" key with a list of action dicts.
        Each action dict must have at least a "type" key.

    Returns
    -------
    dict
        {
            "status":         "PASS" | "FAIL",
            "steps_executed": int,
            "error":          None | str
        }
    """
    # ── Input validation ──────────────────────────────────────────────────
    if not isinstance(actions_json, dict):
        return {
            "status": "FAIL",
            "steps_executed": 0,
            "error": "Input must be a JSON object (dict) with an 'actions' key.",
        }

    actions = actions_json.get("actions")
    if not actions or not isinstance(actions, list):
        return {
            "status": "FAIL",
            "steps_executed": 0,
            "error": "Missing or empty 'actions' list in input JSON.",
        }

    # ── Generate script (for logging / debugging) ─────────────────────────
    try:
        script, requires_headed = generate_playwright_code(actions)
        print("=" * 60)
        print("GENERATED PLAYWRIGHT SCRIPT")
        print("=" * 60)
        print(script)
        print("=" * 60)
    except Exception as exc:
        print(f"[Code Generator] Warning: could not generate script preview — {exc}")
        requires_headed = False

    # ── Execute ───────────────────────────────────────────────────────────
    headless = not requires_headed
    result = execute_actions(actions, headless=headless)

    print(f"\n{'=' * 60}")
    print(f"TEST RESULT: {result['status']}")
    print(f"Steps executed: {result['steps_executed']}")
    if result["error"]:
        print(f"Error: {result['error']}")
    print(f"{'=' * 60}")

    return result


# ─── Demo / CLI ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example 1: Form automation (will fail without a local server — demo only)
    form_test = {
        "actions": [
            {"type": "navigate", "url": "http://localhost:5000"},
            {"type": "input", "selector": "#username", "value": "admin"},
            {"type": "input", "selector": "#password", "value": "1234"},
            {"type": "click", "selector": "#login"},
            {"type": "assert", "selector": "#dashboard", "condition": "visible"},
        ]
    }

    # Example 2: YouTube automation
    youtube_test = {
        "actions": [
            {"type": "navigate", "url": "https://www.youtube.com"},
            {"type": "input", "selector": "input[name='search_query']", "value": "lofi music"},
            {"type": "press", "key": "Enter"},
            {"type": "wait", "duration": 3000},
            {"type": "click", "selector": "ytd-video-renderer a#thumbnail"},
            {"type": "wait", "duration": 5000},
        ]
    }

    # Pick which test to run based on CLI arg
    if len(sys.argv) > 1 and sys.argv[1] == "youtube":
        print("\n🎵  Running YouTube automation test...\n")
        result = run_test(youtube_test)
    else:
        print("\n📝  Running form automation test...\n")
        print("    (Requires Flask app at localhost:5000)\n")
        result = run_test(form_test)

    print(json.dumps(result, indent=2))
