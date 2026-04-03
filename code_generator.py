def generate_code(actions):
    code = []

    code.append("from playwright.sync_api import sync_playwright")
    code.append("import time")
    code.append("import os")
    code.append("")
    code.append("with sync_playwright() as p:")
    code.append("    browser = p.chromium.launch(headless=False)")
    code.append("    page = browser.new_page()")

    for action in actions:
        if action["action"] == "open":
            if action["platform"] == "youtube":
                code.append('    page.goto("https://www.youtube.com")')
            code.append("    time.sleep(3)")

        elif action["action"] == "search":
            code.append(f'    page.fill("input[name=search_query]", "{action["query"]}")')
            code.append('    page.keyboard.press("Enter")')
            code.append("    time.sleep(5)")

            code.append('    page.click("ytd-video-renderer a#video-title")')
            code.append("    time.sleep(8)")

            # screenshot
            code.append('    if not os.path.exists("static"):')
            code.append('        os.makedirs("static")')
            code.append('    page.screenshot(path="static/screenshot.png")')

    code.append("    time.sleep(2)")
    code.append("    browser.close()")

    return "\n".join(code)