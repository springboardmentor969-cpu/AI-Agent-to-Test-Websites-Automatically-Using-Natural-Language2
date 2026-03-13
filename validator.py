# validator.py
def validate_output(code: str) -> bool:
    if not code or "Unknown" in code:
        return False
    return True