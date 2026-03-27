def parse_instruction(user_input):

    instruction = user_input.lower().strip()

    commands = instruction.split(" and ")

    parsed_commands = []

    for cmd in commands:

        parsed = {
            "action": None,
            "target": None,
            "value": None
        }

        if "search" in cmd:

            parsed["action"] = "search"
            parsed["target"] = "google"

            value = cmd.replace("search", "")
            value = value.replace("for", "")
            parsed["value"] = value.strip()

        elif "open" in cmd:

            parsed["action"] = "open"

            target = cmd.replace("open", "")
            target = target.replace("website", "")
            parsed["target"] = target.strip()

        elif "click" in cmd:

            parsed["action"] = "click"

            target = cmd.replace("click", "")
            target = target.replace("button", "")
            parsed["target"] = target.strip()

        elif "enter" in cmd or "type" in cmd:

            parsed["action"] = "enter"

            value = cmd.replace("enter", "")
            value = value.replace("type", "")

            parsed["target"] = "input field"
            parsed["value"] = value.strip()

        else:

            parsed["action"] = "unknown"

        parsed_commands.append(parsed)

    return parsed_commands