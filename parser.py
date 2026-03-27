def parse_instruction(text):
    actions = []
    text = text.lower()

    if "youtube" in text:
        actions.append({"action": "open", "platform": "youtube"})
    elif "amazon" in text:
        actions.append({"action": "open", "platform": "amazon"})

    if "search" in text:
        query = text.split("search")[-1].strip()
        actions.append({"action": "search", "query": query})

    return actions