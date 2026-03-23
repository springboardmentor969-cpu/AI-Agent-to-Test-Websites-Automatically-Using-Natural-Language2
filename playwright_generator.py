from schemas import TestCommand

class PlaywrightGenerator:

    def generate(self, command: TestCommand, url: str) -> str:

        code = f'page.goto("https://{url}")\n'

        if command.action == "input" and command.value:
            code += f"""
page.fill('input', '{command.value}')
page.press('input', 'Enter')
"""

        elif command.action == "click":
            code += f"page.click('text={command.target}')\n"

        return code