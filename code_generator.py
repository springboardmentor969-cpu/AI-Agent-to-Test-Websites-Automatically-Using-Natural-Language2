def generate_code(steps):
    code = [
        "from playwright.sync_api import sync_playwright",
        "",
        "with sync_playwright() as p:",
        "    browser = p.chromium.launch(headless=False)",
        "    page = browser.new_page()",
    ]

    for step in steps:
        action = step["action"]

        if action == "open":
            code.append(f'    page.goto("{step["target"]}")')
            code.append('    page.wait_for_timeout(1500)')

        elif action == "search":
            code.append('    page.wait_for_timeout(1000)')
            code.append('    try:')
            code.append(f'        box = page.locator("input[name=\'search_query\']").first')
            code.append('        box.wait_for(state="visible", timeout=5000)')
            code.append(f'        box.fill("{step["value"]}")')
            code.append('        box.press("Enter")')
            code.append('    except:')
            code.append('        try:')
            code.append(f'            box = page.locator("textarea[name=\'q\']").first')
            code.append('            box.wait_for(state="visible", timeout=3000)')
            code.append(f'            box.fill("{step["value"]}")')
            code.append('            box.press("Enter")')
            code.append('        except:')
            code.append(f'            box = page.locator("input[name=\'q\']").first')
            code.append('            box.wait_for(state="visible", timeout=3000)')
            code.append(f'            box.fill("{step["value"]}")')
            code.append('            box.press("Enter")')
            code.append('    page.wait_for_timeout(1500)')

        elif action == "click":
            code.append(f'    page.get_by_text("{step["target"]}", exact=False).click()')
            code.append('    page.wait_for_timeout(1500)')

        elif action == "type":
            code.append(f'    page.fill("input", "{step["value"]}")')
            code.append('    page.wait_for_timeout(1000)')

        elif action == "press_enter":
            code.append('    page.keyboard.press("Enter")')
            code.append('    page.wait_for_timeout(1500)')

        elif action == "verify":
            code.append(f'    assert "{step["target"].lower()}" in page.content().lower()')
            code.append('    page.wait_for_timeout(1000)')

        elif action == "unknown":
            code.append(f'    # Unknown step: {step["target"]}')

    code.append("    page.wait_for_timeout(5000)")
    code.append("    browser.close()")

    return "\n".join(code)