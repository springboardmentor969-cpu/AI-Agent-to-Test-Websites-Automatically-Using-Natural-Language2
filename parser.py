import re

def parse_instruction(text):
    steps = []
    text = text.strip()

    parts = re.split(r"\n|\s+and\s+|,", text, flags=re.IGNORECASE)

    step_no = 1

    for part in parts:
        part = part.strip()
        lower = part.lower()

        if not part:
            continue

        if lower.startswith("open "):
            url = part[5:].strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                if "." in url:
                    url = "https://" + url
                else:
                    url = "https://www." + url + ".com"

            steps.append({
                "step_no": step_no,
                "action": "open",
                "target": url,
                "value": "",
                "description": f"Open website {url}"
            })

        elif lower.startswith("search "):
            query = re.sub(r"^search\s+(for\s+)?", "", part, flags=re.IGNORECASE).strip()

            steps.append({
                "step_no": step_no,
                "action": "search",
                "target": "search box",
                "value": query,
                "description": f"Search for '{query}'"
            })

        elif lower.startswith("click "):
            target = part[6:].strip()

            steps.append({
                "step_no": step_no,
                "action": "click",
                "target": target,
                "value": "",
                "description": f"Click on '{target}'"
            })

        elif lower.startswith("type "):
            match = re.match(r"type\s+(.+?)\s+into\s+(.+)", part, flags=re.IGNORECASE)
            if match:
                text_value = match.group(1).strip()
                field_name = match.group(2).strip()

                steps.append({
                    "step_no": step_no,
                    "action": "type",
                    "target": field_name,
                    "value": text_value,
                    "description": f"Type '{text_value}' into '{field_name}'"
                })
            else:
                steps.append({
                    "step_no": step_no,
                    "action": "unknown",
                    "target": part,
                    "value": "",
                    "description": f"Unknown instruction: {part}"
                })

        elif lower in ["press enter", "enter"]:
            steps.append({
                "step_no": step_no,
                "action": "press_enter",
                "target": "Enter key",
                "value": "",
                "description": "Press Enter key"
            })

        elif lower.startswith("verify "):
            verify_text = part[7:].strip()

            steps.append({
                "step_no": step_no,
                "action": "verify",
                "target": verify_text,
                "value": "",
                "description": f"Verify text '{verify_text}' is present"
            })

        else:
            steps.append({
                "step_no": step_no,
                "action": "unknown",
                "target": part,
                "value": "",
                "description": f"Unknown instruction: {part}"
            })

        step_no += 1

    return steps