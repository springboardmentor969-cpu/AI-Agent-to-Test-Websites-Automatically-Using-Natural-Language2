"""
AI Planner Module
------------------
Uses Google Gemini (via the new google.genai SDK) to convert complex
natural-language instructions into complete Playwright Python scripts.
"""

import os
import time
from dotenv import load_dotenv
from google import genai


SYSTEM_PROMPT = """You are an expert Playwright automation engineer.

The user will give you a natural-language instruction describing what they want
to do in a web browser.  Your job is to produce a **complete, runnable** Python
script using `playwright.async_api` that performs every step described.

RULES:
1. Always use `async_playwright` with `asyncio.run()`.
2. Launch Chromium with `headless=False, slow_mo=600` so the user can watch.
3. Use realistic waits: `wait_for_load_state("domcontentloaded")`,
   `wait_for_timeout(ms)`, or `wait_for_selector(selector)`.
4. Interact with elements using **robust selectors** — prefer `page.locator()`
   with text, role, or placeholder selectors over fragile CSS.
5. For search bars, try common patterns: `input[name="search_query"]`,
   `input[type="search"]`, `input[aria-label="Search"]`, or
   `page.get_by_placeholder(...)`.
6. ALWAYS add `await page.wait_for_timeout(3000)` after navigations and
   after important clicks so the page has time to load.
7. After completing all actions, wait 8 seconds so the user can see the
   result, then close the browser cleanly.
8. Print "TEST PASSED" at the very end if everything succeeds.
9. Wrap everything in try/except — on failure print "TEST FAILED: <reason>".
10. Do NOT use `page.pause()` or `input()` — the script must run unattended.
11. Output ONLY the Python code, no explanations, no markdown fences.
"""

MAX_RETRIES = 3


def generate_ai_script(instruction: str) -> str:
    """
    Send the user's natural-language instruction to Gemini and return
    a complete Playwright Python script.  Automatically retries on
    rate-limit (429) errors.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")

    print(f"[AI Planner] Using API key ending in ...{api_key[-6:]}")
    print(f"[AI Planner] Generating script for: {instruction}")

    client = genai.Client(api_key=api_key)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{SYSTEM_PROMPT}\n\nInstruction: {instruction}",
            )
            script = response.text.strip()

            # Strip markdown code fences if the model adds them
            if script.startswith("```python"):
                script = script[len("```python"):].strip()
            if script.startswith("```"):
                script = script[3:].strip()
            if script.endswith("```"):
                script = script[:-3].strip()

            print(f"[AI Planner] Script generated successfully ({len(script)} chars)")
            return script

        except Exception as exc:
            last_error = exc
            error_msg = str(exc)

            # Auto-retry on rate limit (429)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                wait_secs = 40 * attempt  # 40s, 80s, 120s
                print(f"[AI Planner] Rate limited (attempt {attempt}/{MAX_RETRIES}). "
                      f"Waiting {wait_secs}s before retry...")
                time.sleep(wait_secs)
                continue

            # Non-retryable error — raise immediately
            raise

    # All retries exhausted
    raise last_error
