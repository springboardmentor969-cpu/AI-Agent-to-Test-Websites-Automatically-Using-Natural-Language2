def generate_code(actions):
    code = []

    code.append("from playwright.sync_api import sync_playwright")
    code.append("import time")
    code.append("")
    code.append("with sync_playwright() as p:")
    code.append("    browser = p.chromium.launch(headless=False)")
    code.append("    page = browser.new_page()")

    for action in actions:
        if action["action"] == "open":
            if action["platform"] == "youtube":
                code.append('    page.goto("https://www.youtube.com")')
            elif action["platform"] == "amazon":
                code.append('    page.goto("https://www.amazon.in")')
            code.append("    time.sleep(3)")

        elif action["action"] == "search":
            code.append(f'    page.fill("input[type=text]", "{action["query"]}")')
            code.append('    page.keyboard.press("Enter")')
            code.append("    time.sleep(5)")

    code.append('    input("Press Enter to close...")')
    code.append("    browser.close()")

    return "\n".join(code)