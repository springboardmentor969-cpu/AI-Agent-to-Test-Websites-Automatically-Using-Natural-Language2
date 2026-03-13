# code_generator.py
from schemas import TestCommand

class CodeGenerator:

    def generate(self, command: TestCommand) -> str:
        if command.action == "click":
            return f"driver.find_element('{command.target}').click()"

        if command.action == "input":
            return (
                f"driver.find_element('{command.target}')"
                f".send_keys('{command.value}')"
            )

        if command.action == "verify":
            return (
                f"assert '{command.expected_result}' in driver.current_url"
            )

        return "# Unknown action"