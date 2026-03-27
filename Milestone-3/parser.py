import re

def parse_instruction(instruction):
    instruction = instruction.lower()

    actions = []
    platform = None
    query = None
    position = 0

    if "youtube" in instruction:
        platform = "youtube"
    elif "google" in instruction:
        platform = "google"

    match = re.search(r"(search|play|find)\s+(.*)", instruction)

    if match:
        query = match.group(2)
        query = query.split("and click")[0]
        query = query.split("click")[0]
    else:
        if platform:
            query = instruction.replace("open", "")
            query = query.replace("youtube", "")
            query = query.replace("google", "")
            query = query.strip()

    if query:
        for word in ["on youtube", "on google"]:
            query = query.replace(word, "")
        query = query.strip()

    if "click" in instruction:
        if "second" in instruction:
            position = 1
        elif "third" in instruction:
            position = 2
        else:
            position = 0

    if platform:
        actions.append({"action": "open", "platform": platform})

    if query:
        actions.append({"action": "search", "query": query})

    if "click" in instruction:
        actions.append({"action": "click_result", "index": position})

    return actions