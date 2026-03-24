"""
Playwright Execution Engine
----------------------------
Executes structured JSON actions directly using the Playwright **sync** API.

Instead of generating a script and running it in a subprocess, this module
drives the browser in-process for reliable step tracking, error reporting,
and result collection.

Returns a standardised result dict:
    {"status": "PASS"|"FAIL", "steps_executed": N, "error": None|str}
"""

import re
from playwright.sync_api import sync_playwright, expect

# ─── YouTube helpers ─────────────────────────────────────────────────────────
YOUTUBE_DOMAINS = ("youtube.com", "youtu.be")

YOUTUBE_CLICK_FALLBACKS = [
    "ytd-video-renderer a#thumbnail",
    "ytd-video-renderer #video-title-link",
    "ytd-rich-item-renderer a#thumbnail",
    "a#video-title",
]


def _is_youtube_url(url: str) -> bool:
    if not url:
        return False
    return any(domain in url.lower() for domain in YOUTUBE_DOMAINS)


def _detect_headed_mode(actions: list[dict]) -> bool:
    """Return True if any navigate action points to a media site."""
    return any(
        _is_youtube_url(a.get("url", ""))
        for a in actions
        if a.get("type") == "navigate"
    )


# ─── Per-action executors ────────────────────────────────────────────────────

def _exec_navigate(page, action, is_youtube):
    page.goto(action["url"])
    page.wait_for_load_state("domcontentloaded")
    if is_youtube:
        page.wait_for_timeout(2000)


def _exec_input(page, action, is_youtube):
    selector = action["selector"]
    value = action["value"]
    page.locator(selector).click()
    page.locator(selector).fill(value)
    if is_youtube:
        page.wait_for_timeout(500)


def _exec_click(page, action, is_youtube):
    selector = action.get("selector")

    if is_youtube and selector and "thumbnail" in selector.lower():
        # Try primary, then fallback selectors
        all_selectors = [selector] + [
            s for s in YOUTUBE_CLICK_FALLBACKS if s != selector
        ]
        for sel in all_selectors:
            try:
                page.locator(sel).first.click(timeout=5000)
                page.wait_for_timeout(2000)
                return
            except Exception:
                continue
        raise Exception("Could not click any video thumbnail")

    page.locator(selector).click()


def _exec_press(page, action, is_youtube):
    page.keyboard.press(action["key"])
    if is_youtube:
        page.wait_for_timeout(3000)  # wait for search results to load


def _exec_wait(page, action, _is_youtube):
    duration = action.get("duration", 1000)
    page.wait_for_timeout(duration)


def _exec_assert(page, action, _is_youtube):
    condition = str(action.get("condition") or "visible")
    selector = str(action.get("selector") or "")
    value = str(action.get("value") or "")

    if condition == "visible":
        expect(page.locator(selector)).to_be_visible()
    elif condition == "text_present":
        expect(page.locator(selector)).to_contain_text(value)
    elif condition == "url_contains":
        expect(page).to_have_url(re.compile(value))
    else:
        raise ValueError(f"Unsupported assertion condition: '{condition}'")


_EXECUTORS = {
    "navigate": _exec_navigate,
    "input":    _exec_input,
    "click":    _exec_click,
    "press":    _exec_press,
    "wait":     _exec_wait,
    "assert":   _exec_assert,
}


# ─── Main entry point ────────────────────────────────────────────────────────

def execute_actions(actions: list[dict], headless: bool = True) -> dict:
    """
    Execute a list of structured actions in a Playwright browser.

    Parameters
    ----------
    actions : list[dict]
        The "actions" array from the input JSON.
    headless : bool
        Browser mode.  Automatically overridden to False for YouTube URLs.

    Returns
    -------
    dict
        {"status": "PASS"|"FAIL", "steps_executed": int, "error": None|str}
    """
    is_youtube = _detect_headed_mode(actions)
    if is_youtube:
        headless = False

    slow_mo = 100 if is_youtube else 0
    steps_executed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            for action in actions:
                action_type = str(action.get("type") or "").lower()
                executor = _EXECUTORS.get(action_type)

                if executor is None:
                    print(f"[Executor] WARNING: unknown action '{action_type}' — skipped")
                    steps_executed += 1
                    continue

                print(f"[Executor] Step {steps_executed + 1}: {action_type} {action}")
                executor(page, action, is_youtube)
                steps_executed += 1

            return {
                "status": "PASS",
                "steps_executed": steps_executed,
                "error": None,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "steps_executed": steps_executed,
                "error": str(exc),
            }

        finally:
            if not headless:
                try:
                    print("[Executor] Waiting for user to close the browser manually...")
                    page.wait_for_event("close", timeout=0)
                except Exception:
                    pass
            else:
                page.wait_for_timeout(2000)

            try:
                context.close()
                browser.close()
            except Exception:
                pass
