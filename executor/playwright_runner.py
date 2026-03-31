"""
Playwright Execution Engine
----------------------------
Executes structured JSON actions directly using the Playwright **sync** API.

Features:
- Adaptive DOM Mapping: Fallbacks for locating elements dynamically.
- Performance Timing: Tracks execution time per step.
- Rich Reporting: Returns a structured JSON report via TestReport.
"""

import time
import re
import os
import glob
from playwright.sync_api import sync_playwright, expect
from reporting.report_builder import TestReport

# ─── Screenshot directory ────────────────────────────────────────────────────
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "screenshots")

def _ensure_screenshot_dir():
    """Create screenshots directory and clear old screenshots."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    for f in glob.glob(os.path.join(SCREENSHOT_DIR, "*.png")):
        try:
            os.remove(f)
        except OSError:
            pass

def _take_screenshot(page, step_index: int, action_type: str) -> str:
    """Take a screenshot and return the URL path for the frontend."""
    try:
        filename = f"step_{step_index}_{action_type}_{int(time.time() * 1000)}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        page.screenshot(path=filepath, full_page=False)
        return f"/static/screenshots/{filename}"
    except Exception as e:
        print(f"[Screenshot] Failed to capture: {e}")
        return ""

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
        if a.get("type", "").lower() == "navigate"
    )

# ─── Robust Locators ─────────────────────────────────────────────────────────

def _robust_click(page, selector: str):
    """Attempt primary selector, then dynamically fallback to text or roles."""
    # 1. Primary selector
    try:
        page.locator(selector).first.click(timeout=3000)
        return
    except Exception:
        pass

    # 2. Text match (if the selector looks like a plain label instead of CSS)
    if not any(char in selector for char in ["#", ".", "[", ">"]):
        try:
            page.get_by_text(selector, exact=False).first.click(timeout=3000)
            return
        except Exception:
            pass
        
        try:
            page.get_by_role("button", name=selector).first.click(timeout=3000)
            return
        except Exception:
            pass
            
        try:
            page.get_by_role("link", name=selector).first.click(timeout=3000)
            return
        except Exception:
            pass

    raise Exception(f"Could not locate element to click using selector or fallbacks: '{selector}'")

def _robust_fill(page, selector: str, value: str):
    try:
        loc = page.locator(selector).first
        loc.click(timeout=3000)
        loc.fill(value)
        return
    except Exception:
        pass
        
    try:
        loc = page.get_by_placeholder(selector, exact=False).first
        loc.click(timeout=3000)
        loc.fill(value)
        return
    except Exception:
        pass
        
    raise Exception(f"Could not locate element to fill using selector or fallbacks: '{selector}'")

# ─── Per-action executors ────────────────────────────────────────────────────

def _exec_navigate(page, action, is_youtube):
    page.goto(action["url"])
    page.wait_for_load_state("domcontentloaded")
    if is_youtube:
        page.wait_for_timeout(2000)


def _exec_input(page, action, is_youtube):
    selector = action["selector"]
    value = action["value"]
    
    _robust_fill(page, selector, value)
    
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

    _robust_click(page, selector)


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
        expect(page.locator(selector)).to_be_visible(timeout=5000)
    elif condition == "text_present":
        expect(page.locator(selector)).to_contain_text(value, timeout=5000)
    elif condition == "url_contains":
        expect(page).to_have_url(re.compile(value), timeout=5000)
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
    Execute a list of structured actions and return a detailed JSON report.
    Captures a browser screenshot after every action step.
    """
    is_youtube = _detect_headed_mode(actions)
    if is_youtube:
        headless = False

    slow_mo = 100 if is_youtube else 20

    # Prepare screenshot directory (clear old screenshots)
    _ensure_screenshot_dir()
    
    report = TestReport("Automated LangGraph Browser Test")

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
            for idx, action in enumerate(actions, start=1):
                action_type = str(action.get("type", "")).lower()
                executor = _EXECUTORS.get(action_type)

                step_start_time = time.time()

                if executor is None:
                    step_duration = time.time() - step_start_time
                    screenshot_url = _take_screenshot(page, idx, "unknown")
                    report.add_step(
                        action=action, 
                        status="fail", 
                        details=f"Unknown action type '{action_type}'", 
                        execution_time=step_duration,
                        screenshot=screenshot_url
                    )
                    break

                try:
                    executor(page, action, is_youtube)
                    step_duration = time.time() - step_start_time
                    screenshot_url = _take_screenshot(page, idx, action_type)
                    report.add_step(
                        action=action, 
                        status="pass", 
                        execution_time=step_duration,
                        screenshot=screenshot_url
                    )
                except Exception as e:
                    step_duration = time.time() - step_start_time
                    screenshot_url = _take_screenshot(page, idx, action_type)
                    report.add_step(
                        action=action, 
                        status="fail", 
                        details=str(e), 
                        execution_time=step_duration,
                        screenshot=screenshot_url
                    )
                    break

        finally:
            # Capture final state screenshot
            try:
                final_url = _take_screenshot(page, 0, "final_state")
                if final_url:
                    report.final_screenshot = final_url
            except Exception:
                pass

            if not headless:
                try:
                    page.wait_for_timeout(2000)
                except Exception:
                    pass
            else:
                page.wait_for_timeout(1000)

            try:
                context.close()
                browser.close()
            except Exception:
                pass

    return report.to_dict()
