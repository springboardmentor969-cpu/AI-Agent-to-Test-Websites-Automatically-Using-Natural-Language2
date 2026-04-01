from agent.instruction_parser import normalize_instruction, parse_instruction


def plan_actions(user_input):

    actions = normalize_instruction(user_input)

    if not actions:
        actions = parse_instruction(user_input)

    return actions
