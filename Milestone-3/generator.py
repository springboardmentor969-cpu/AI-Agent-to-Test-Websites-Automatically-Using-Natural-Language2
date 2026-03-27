def generate_code(commands):
    code = []

    code.append("from playwright.sync_api import sync_playwright")
    code.append("")
    code.append("with sync_playwright() as p:")
    code.append("    browser = p.chromium.launch(headless=False)")
    code.append("    page = browser.new_page()")

    platform = None

    for cmd in commands:

        # OPEN
        if cmd["action"] == "open":
            platform = cmd["platform"]

            if platform == "youtube":
                code.append('    page.goto("https://www.youtube.com")')

            elif platform == "google":
                code.append('    page.goto("https://www.google.com")')

        # SEARCH
        elif cmd["action"] == "search":
            query = cmd["query"]

            if platform == "youtube":
                code.append(f'    page.goto("https://www.youtube.com/results?search_query={query}")')
                code.append('    page.wait_for_selector("ytd-video-renderer")')

            elif platform == "google":
                # 🔥 REDIRECT TO DUCKDUCKGO (NO CAPTCHA)
                code.append(f'    page.goto("https://duckduckgo.com/?q={query}")')
                code.append('    page.wait_for_selector("a[data-testid=\'result-title-a\']")')

        # CLICK
        elif cmd["action"] == "click_result":
            index = cmd["index"]

            if platform == "youtube":
                code.append('    videos = page.query_selector_all("ytd-video-renderer")')
                code.append('    valid = []')
                code.append('    for v in videos:')
                code.append('        link = v.query_selector("a#video-title")')
                code.append('        if link:')
                code.append('            href = link.get_attribute("href")')
                code.append('            if href and "/shorts/" not in href:')
                code.append('                valid.append(link)')
                code.append(f'    valid[{index}].click()')

            elif platform == "google":
                code.append('    results = page.query_selector_all("a[data-testid=\'result-title-a\']")')
                code.append(f'    results[{index}].click()')

    code.append('    page.wait_for_timeout(100000000)')

    return "\n".join(code)