from agent.instruction_parser import parse_instruction
from agent.code_generator import generate_code

# Test the full pipeline
test_instruction = "Open youtube and search sad songs"
print(f"Testing instruction: {test_instruction}")
print("=" * 50)

steps = parse_instruction(test_instruction)
print(f"Parsed steps: {steps}")
print("=" * 50)

# Generate code
code = generate_code(steps)
print("Generated code:")
print(code[:1000])  # First 1000 chars
print("=" * 50)

# Look for the goto line
import re
goto_match = re.search(r'page\.goto\("([^"]+)"', code)
if goto_match:
    goto_url = goto_match.group(1)
    print(f"URL in goto(): {goto_url}")
else:
    print("No goto() found in code")
