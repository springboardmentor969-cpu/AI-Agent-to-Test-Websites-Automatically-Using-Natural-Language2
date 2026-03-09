def parse_instruction(text):

    steps = []

    lines = text.lower().split("\n")

    for line in lines:

        if "open" in line:
            steps.append("OPEN PAGE")

        elif "username" in line:
            steps.append("ENTER USERNAME")

        elif "password" in line:
            steps.append("ENTER PASSWORD")

        elif "click" in line:
            steps.append("CLICK BUTTON")

    return steps