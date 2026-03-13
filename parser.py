# parser.py
import re
from schemas import TestCommand

class InstructionParser:

    def parse(self, text: str) -> TestCommand:
        text = text.lower()

        # Action detection
        if "click" in text:
            action = "click"
        elif "enter" in text or "type" in text:
            action = "input"
        elif "verify" in text or "check" in text:
            action = "verify"
        else:
            action = "unknown"

        # Target extraction
        target_match = re.search(r"(button|field|page)\s+(\w+)", text)
        target = target_match.group(2) if target_match else "unknown"

        # Value extraction
        value_match = re.search(r"enter\s+\"(.+?)\"", text)
        value = value_match.group(1) if value_match else None

        # Expected result
        expected_match = re.search(r"should\s+see\s+(\w+)", text)
        expected = expected_match.group(1) if expected_match else None

        return TestCommand(
            action=action,
            target=target,
            value=value,
            expected_result=expected
        )