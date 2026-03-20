from agent.models import ParsedInstruction


def infer_expected_result(parsed: ParsedInstruction) -> str | None:
    if parsed.expected_result:
        return parsed.expected_result

    if parsed.target_type == "demo_login":
        if parsed.username == "test" and parsed.password == "1234":
            return "Success"
        return "Failed"

    return None
