import re
from schemas import TestCommand

class InstructionParser:

    def parse(self, text: str):
        text = text.lower()

        # Detect website
        url_match = re.search(r"(https?://\S+|www\.\S+|\w+\.com)", text)
        url = url_match.group(0) if url_match else "example.com"

        # Detect action
        if "click" in text:
            action = "click"
        elif "enter" in text or "search" in text:
            action = "input"
        else:
            action = "unknown"

        # Detect value (search text)
        value_match = re.search(r'"(.*?)"', text)
        value = value_match.group(1) if value_match else None

        # Default target
        target = "search"

        # Expected result
        expected_match = re.search(r"should\s+see\s+(.+)", text)
        expected = expected_match.group(1) if expected_match else None

        return TestCommand(
            action=action,
            target=target,
            value=value,
            expected_result=expected
        ), url