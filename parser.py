import re

def parse_test_steps(user_input: str):
    """
    AI Parser that converts natural language instructions
    into structured browser automation steps.
    """

    steps = []

    text = user_input.lower()

    # Open website
    open_match = re.search(r'open (https?://[^\s]+)', text)
    if open_match:
        steps.append({
            "action": "open",
            "url": open_match.group(1)
        })

    # Click button or link
    click_matches = re.findall(r'click (?:on )?(?:the )?([a-zA-Z0-9 _-]+)', text)
    for item in click_matches:
        steps.append({
            "action": "click",
            "target": item.strip()
        })

    # Enter text
    type_matches = re.findall(r'(?:enter|type) (.+?) into ([a-zA-Z0-9 _-]+)', text)
    for value, field in type_matches:
        steps.append({
            "action": "type",
            "text": value.strip(),
            "field": field.strip()
        })

    # Submit
    if "submit" in text:
        steps.append({
            "action": "submit"
        })

    return steps