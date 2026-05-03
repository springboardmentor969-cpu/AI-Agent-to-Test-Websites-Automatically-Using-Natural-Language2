from agent.instruction_parser import parse_instruction
from agent.code_generator import generate_code
import io
import contextlib

# Test the exact same flow as the web app
instruction = "Open youtube and search sad songs"
print(f"Testing: {instruction}")
print("=" * 50)

# Parse instruction
steps = parse_instruction(instruction)
print(f"Parsed steps: {steps}")

# Generate code
code = generate_code(steps)
print(f"Generated code snippet:")
print(code.split('page.goto')[1].split(',')[0] if 'page.goto' in code else "No goto found")
print("=" * 50)

# Execute the code
try:
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        exec(code)
    
    execution_output = captured_output.getvalue()
    print(f"Execution output: {execution_output}")
    
    if "TEST_PASSED: True" in execution_output:
        print("✅ SUCCESS: Test passed!")
    else:
        print("❌ FAILED: Test did not pass")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
