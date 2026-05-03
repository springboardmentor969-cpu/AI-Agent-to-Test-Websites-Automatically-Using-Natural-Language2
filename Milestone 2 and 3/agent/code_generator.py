def _normalize_url(raw: str) -> str:
    """
    Normalize any user-supplied URL string to a clean https:// URL.
    Handles all casing/format variants:
      youtube / Youtube / YOUTUBE / youtube.com / YouTube.com /
      https://youtube.com / http://www.youtube.com  →  https://www.youtube.com
    """
    clean = raw.strip()
    lower = clean.lower()

    # Remove scheme for inspection
    for prefix in ("https://", "http://"):
        if lower.startswith(prefix):
            lower = lower[len(prefix):]
            break

    # Remove leading www.
    bare = lower.lstrip("www.")

    # Known-site canonical URL table — extend as needed
    KNOWN = {
        "youtube":    "https://www.youtube.com",
        "youtube.com":"https://www.youtube.com",
        "google":     "https://www.google.com",
        "google.com": "https://www.google.com",
        "github":     "https://www.github.com",
        "github.com": "https://www.github.com",
    }

    host = bare.split("/")[0]
    if host in KNOWN:
        return KNOWN[host]

    # Unknown site — just ensure it has a scheme
    if not clean.lower().startswith(("http://", "https://")):
        return "https://" + clean
    return clean


def generate_code(steps):

    code = """
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu'
        ]
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
results_obtained = False
"""
    current_url = ""

    for step in steps:

        # ── open_url ──────────────────────────────────────────────────────────
        if step["action"] == "open_url":
            url = _normalize_url(step["url"])
            current_url = url
            code += f'''    try:
        page.goto("{url}", timeout=15000)
        page.wait_for_load_state("networkidle")
        print("Navigated to: {url}")
    except Exception as e:
        print(f"NAVIGATION FAILED: {{str(e)}}")
        raise e
'''

        # ── click ─────────────────────────────────────────────────────────────
        if step["action"] == "click":
            code += f'    page.click("#{step["element"]}")\n'

        # ── enter_text ────────────────────────────────────────────────────────
        if step["action"] == "enter_text":
            field = step["field"].lower()
            if "email" in field:
                selector = "input[type='email'], input[name*='email'], input[id*='email']"
            elif "password" in field:
                selector = "input[type='password'], input[name*='password']"
            elif "username" in field or "user" in field:
                selector = "input[name*='user'], input[name*='login'], input[id*='user']"
            else:
                selector = f"input[placeholder*='{field}'], input[name*='{field}']"
            code += f'    page.wait_for_selector("{selector}", timeout=10000)\n'
            code += f'    page.fill("{selector}", "{step["text"]}")\n'

        # ── search / enter_instruction_text (identical behaviour) ─────────────
        if step["action"] in ("search", "enter_instruction_text"):
            text_to_enter = step["text"]

            if "google.com" in current_url:
                search_selector = "textarea[name='q']"
            elif "youtube.com" in current_url:
                search_selector = "input[name='search_query']"
            elif "github.com" in current_url:
                search_selector = "input[data-test-id='site-search-input'], input[placeholder*='Search'], input[aria-label*='Search']"
            else:
                search_selector = "input[type='search'], input[name='q'], input[name='search'], textarea[name='q']"

            code += f'''    try:
        page.wait_for_selector("{search_selector}", timeout=10000)
        page.fill("{search_selector}", "{text_to_enter}")
        page.press("{search_selector}", "Enter")
        print("Searched for: {text_to_enter}")
    except Exception as e:
        print(f"SEARCH FAILED: {{str(e)}}")
        raise e
'''
            # Result verification per site
            if "google.com" in current_url:
                code += '''    try:
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_selector("h3", timeout=10000)
        result_count = page.locator("h3").count()
        if result_count == 0:
            result_count = page.locator("div.g").count()
        results_obtained = result_count > 0
        print(f"Google results found: {result_count}")
    except Exception as e:
        results_obtained = False
        print(f"Google result check failed: {str(e)}")
'''
            elif "youtube.com" in current_url:
                code += '''    try:
        page.wait_for_load_state("networkidle", timeout=15000)
        video_count = 0
        for sel in ["ytd-video-renderer", "a#video-title", "[href*='/watch']"]:
            try:
                video_count = page.locator(sel).count()
                if video_count > 0:
                    print(f"YouTube: found {video_count} items via '{sel}'")
                    break
            except:
                pass
        results_obtained = video_count > 0
        print(f"YouTube results found: {video_count}")
    except Exception as e:
        results_obtained = False
        print(f"YouTube result check failed: {str(e)}")
'''
            elif "github.com" in current_url:
                code += '''    try:
        page.wait_for_load_state("networkidle", timeout=15000)
        result_count = 0
        for sel in ["[data-testid='results-list'] li", "li.repo-list-item", "div.search-title"]:
            try:
                result_count = page.locator(sel).count()
                if result_count > 0:
                    print(f"GitHub: found {result_count} items via '{sel}'")
                    break
            except:
                pass
        results_obtained = result_count > 0
        print(f"GitHub results found: {result_count}")
    except Exception as e:
        results_obtained = False
        print(f"GitHub result check failed: {str(e)}")
'''
            else:
                code += '    results_obtained = True  # Generic: assume success if no exception\n'

        # ── click_first_result ────────────────────────────────────────────────
        if step["action"] == "click_first_result":
            if "youtube.com" in current_url:
                code += '''    try:
        first_video = page.locator("a#video-title, ytd-video-renderer a").first
        first_video.wait_for(timeout=10000)
        first_video.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"Clicked first video, now at: {page.url}")
        results_obtained = True
    except Exception as e:
        results_obtained = False
        print(f"Click first video failed: {str(e)}")
'''
            elif "github.com" in current_url:
                code += '''    try:
        first_repo = page.locator("[data-testid='results-list'] li a, li.repo-list-item a").first
        first_repo.wait_for(timeout=10000)
        first_repo.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        print(f"Clicked first repo, now at: {page.url}")
        results_obtained = True
    except Exception as e:
        results_obtained = False
        print(f"Click first result failed: {str(e)}")
'''

    # ── Final validation ───────────────────────────────────────────────────────
    code += """
    try:
        page_title = page.title()
        assert page_title != "", "Page title is empty"
        print(f"Page title: {page_title}")

        if results_obtained:
            print("RESULTS_OBTAINED: True")
            print("TEST_PASSED: True")
        else:
            print("RESULTS_OBTAINED: False")
            print("TEST_PASSED: False")

    except Exception as e:
        print(f"VALIDATION_ERROR: {str(e)}")
        print("RESULTS_OBTAINED: False")
        print("TEST_PASSED: False")

    import time
    time.sleep(2)
    browser.close()
"""

    return code