def validate_output(state):

    if "parsed" not in state:
        raise ValueError("Parsing failed")

    if "generated_code" not in state:
        raise ValueError("Code generation failed")

    return True