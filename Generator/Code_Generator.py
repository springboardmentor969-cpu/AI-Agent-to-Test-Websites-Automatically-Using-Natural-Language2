"""
Code Generator — Playwright Script Builder
--------------------------------------------
Converts a list of structured JSON actions into a complete, runnable
Playwright Python script using the **sync** API.

Supported action types:
  - navigate  → page.goto(url)
  - input     → page.locator(selector).fill(value)
  - click     → page.locator(selector).click()
  - press     → page.keyboard.press(key)
  - wait      → page.wait_for_timeout(duration_ms)
  - assert    → expect(...) via assertion_generator
"""

from generator.assertion_generator import generate_assertion

# ─── YouTube-specific configuration ──────────────────────────────────────────
YOUTUBE_DOMAINS = ("youtube.com", "youtu.be")

YOUTUBE_CLICK_FALLBACKS = [
    "ytd-video-renderer a#thumbnail",
    "ytd-video-renderer #video-title-link",
    "ytd-rich-item-renderer a#thumbnail",
    "a#video-title",
]


def _is_youtube_url(url: str) -> bool:
    """Check if the URL points to a YouTube domain."""
    if not url:
        return False
    return any(domain in url.lower() for domain in YOUTUBE_DOMAINS)


def _generate_step(action: dict, is_youtube: bool = False) -> list[str]:
    """
    Generate one or more lines of Playwright Python code for a single action.

    Parameters
    ----------
    action : dict
        A structured action with at least a "type" key.
    is_youtube : bool
        When True, injects human-like delays and fallback selectors.

    Returns
    -------
    list[str]
        Lines of Python code (no leading indentation).
    """
    action_type = str(action.get("type") or "").lower()
    lines: list[str] = []

    if action_type == "navigate":
        url = action["url"]
        lines.append(f'page.goto("{url}")')
        lines.append('page.wait_for_load_state("domcontentloaded")')
        if is_youtube:
            lines.append("page.wait_for_timeout(2000)  # let YouTube hydrate")

    elif action_type == "input":
        selector = action["selector"]
        value = action["value"]
        lines.append(f'page.locator("{selector}").click()')
        lines.append(f'page.locator("{selector}").fill("{value}")')
        if is_youtube:
            lines.append("page.wait_for_timeout(500)")

    elif action_type == "click":
        selector = action.get("selector")
        if is_youtube and selector and "thumbnail" in selector.lower():
            # Try the primary selector, then fallbacks
            lines.append("# YouTube: try primary selector, then fallbacks")
            lines.append("video_clicked = False")
            all_selectors = [selector] + [
                s for s in YOUTUBE_CLICK_FALLBACKS if s != selector
            ]
            for sel in all_selectors:
                lines.append(f'if not video_clicked:')
                lines.append(f'    try:')
                lines.append(f'        page.locator("{sel}").first.click(timeout=5000)')
                lines.append(f'        video_clicked = True')
                lines.append(f'    except Exception:')
                lines.append(f'        pass')
            lines.append('if not video_clicked:')
            lines.append('    raise Exception("Could not click any video thumbnail")')
            lines.append("page.wait_for_timeout(2000)")
        else:
            lines.append(f'page.locator("{selector}").click()')

    elif action_type == "press":
        key = action["key"]
        lines.append(f'page.keyboard.press("{key}")')
        if is_youtube:
            lines.append(
                "page.wait_for_timeout(3000)  # wait for search results"
            )

    elif action_type == "wait":
        duration = action.get("duration", 1000)
        lines.append(f"page.wait_for_timeout({duration})")

    elif action_type == "assert":
        assertion_code = generate_assertion(action)
        lines.append(assertion_code)

    else:
        lines.append(f'# WARNING: unknown action type "{action_type}" — skipped')

    return lines


def generate_playwright_code(actions: list[dict]) -> tuple[str, bool]:
    """
    Convert a list of structured JSON actions into a complete Playwright
    Python script (sync API).

    Parameters
    ----------
    actions : list[dict]
        The "actions" array from the input JSON.

    Returns
    -------
    tuple[str, bool]
        - The full Python script as a string.
        - Whether headed mode is required (True for YouTube URLs).
    """
    # Detect if any navigation targets YouTube
    requires_headed = any(
        _is_youtube_url(a.get("url", ""))
        for a in actions
        if a.get("type") == "navigate"
    )

    # ── Collect per-step code ─────────────────────────────────────────────
    step_blocks: list[str] = []
    for i, action in enumerate(actions, start=1):
        step_lines = _generate_step(action, is_youtube=requires_headed)
        comment = f"# Step {i}: {action.get('type', 'unknown')}"
        indented = "\n".join(f"        {line}" for line in step_lines)
        step_blocks.append(f"        {comment}\n{indented}")

    steps_code = "\n\n".join(step_blocks)

    # ── Assemble full script ──────────────────────────────────────────────
    headless_flag = "False" if requires_headed else "True"
    slow_mo = "100" if requires_headed else "0"

    needs_re = any(a.get("condition") == "url_contains" for a in actions if a.get("type") == "assert")
    re_import = "import re\n" if needs_re else ""

    script = f'''\
{re_import}from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless={headless_flag}, slow_mo={slow_mo})
        context = browser.new_context()
        page = context.new_page()

        try:
{steps_code}

            print("TEST PASSED")
        except Exception as exc:
            print(f"TEST FAILED: {{exc}}")
            raise
        finally:
            page.wait_for_timeout(3000)
            context.close()
            browser.close()

if __name__ == "__main__":
    run()
'''

    return script, requires_headed