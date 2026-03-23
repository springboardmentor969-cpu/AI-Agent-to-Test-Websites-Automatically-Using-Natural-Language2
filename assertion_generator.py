from schemas import TestCommand

class AssertionGenerator:

    def generate_assertion(self, command: TestCommand) -> str:

        if command.expected_result:
            return f"assert '{command.expected_result}' in page.content()"

        return ""