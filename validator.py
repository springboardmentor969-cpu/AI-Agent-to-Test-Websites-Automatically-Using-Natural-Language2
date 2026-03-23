def validate_output(code: str) -> bool:
    if not code:
        return False
    if "Unknown" in code:
        return False
    return True