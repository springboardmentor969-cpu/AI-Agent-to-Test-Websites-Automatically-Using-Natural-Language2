from agent.instruction_parser import parse_instruction

# Test the instruction parsing
test_instruction = "Open youtube and search sad songs"
print(f"Testing instruction: {test_instruction}")
print("=" * 50)

steps = parse_instruction(test_instruction)

print(f"Parsed steps: {steps}")
print("=" * 50)

for i, step in enumerate(steps):
    print(f"Step {i+1}: {step}")
    if step["action"] == "open_url":
        print(f"  -> URL to navigate: {step['url']}")
    elif step["action"] == "search":
        print(f"  -> Search for: {step['text']}")
