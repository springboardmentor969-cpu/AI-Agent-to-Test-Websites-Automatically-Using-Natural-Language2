def validate_generated_action(state):

    if "actions" not in state:
        raise Exception("Parsing failed — no actions found")

    if len(state["actions"]) == 0:
        raise Exception("Empty actions list")

    return state
