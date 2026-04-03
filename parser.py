def parse_instruction(text):
    text = text.lower()

    search = "iphone"

    if "search" in text:
        search = text.split("search")[-1].strip()

    return {
        "url": "https://www.amazon.in",
        "search": search,
        "actions": [
            f'page.goto("https://www.amazon.in")',
            f'page.fill("input#twotabsearchtextbox", "{search}")',
            'page.keyboard.press("Enter")'
        ]
    }