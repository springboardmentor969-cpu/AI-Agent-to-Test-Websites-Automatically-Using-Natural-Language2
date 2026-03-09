def parse_instruction(instruction):

    steps = instruction.lower().split("\n")

    actions = []

    for step in steps:

        if "open" in step:
            actions.append({"action":"open_url","value":step})

        elif "enter username" in step:
            value = step.replace("enter username","").strip()
            actions.append({"action":"type","field":"username","value":value})

        elif "enter password" in step:
            value = step.replace("enter password","").strip()
            actions.append({"action":"type","field":"password","value":value})

        elif "click" in step:
            actions.append({"action":"click","target":step})

    return actions