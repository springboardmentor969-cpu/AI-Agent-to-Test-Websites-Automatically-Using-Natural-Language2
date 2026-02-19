def parse_instruction(instruction: str):
    steps = []

    text = instruction.lower()

    if "open" in text:
        steps.append("open_browser")

    if "login" in text or "click login" in text:
        steps.append("click_login")

    return steps
