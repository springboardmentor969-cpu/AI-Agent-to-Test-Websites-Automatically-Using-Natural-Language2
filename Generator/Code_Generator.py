def generate_playwright_code(command):

    action = command["action"]
    target = command["target"]
    value = command["value"]

    if action == "open":
        return f"await page.goto('{value}')"

    elif action == "click":
        return f"await page.click('{target}')"

    elif action == "enter" or action == "type":
        return f"await page.fill('{target}','{value}')"

    else:
        return "Unknown action"