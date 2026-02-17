from parser import parse_instruction

def run_workflow(user_input):
    parsed = parse_instruction(user_input)
    return parsed


if __name__ == "__main__":
    result = run_workflow("open login page")
    print(result)
