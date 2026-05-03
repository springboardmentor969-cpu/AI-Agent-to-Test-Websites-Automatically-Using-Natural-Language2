# Test exactly like the web interface
from flask import Flask, request
import json
from agent.instruction_parser import parse_instruction
from agent.code_generator import generate_code
import io
import contextlib

# Simulate the web interface execution
def test_web_execution(instruction):
    print(f"WEB EXECUTION TEST: {instruction}")
    print("=" * 50)
    
    # Step 1: Parse instruction (like web interface)
    steps = parse_instruction(instruction)
    print(f"PARSED STEPS: {steps}")
    
    # Step 2: Generate code (like web interface)
    code = generate_code(steps)
    print(f"CODE GENERATED: {len(code)} characters")
    
    # Step 3: Execute code (like web interface)
    try:
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            exec(code)
        
        execution_output = captured_output.getvalue()
        print(f"EXECUTION OUTPUT: {execution_output}")
        
        # Step 4: Parse results (like web interface)
        actual_status = "fail"
        if "TEST_PASSED: True" in execution_output:
            actual_status = "pass"
        elif "RESULTS_OBTAINED: True" in execution_output:
            actual_status = "pass"
            
        print(f"FINAL STATUS: {actual_status}")
        return execution_output, actual_status
        
    except Exception as e:
        error_output = f"Error: {str(e)}"
        print(f"EXECUTION ERROR: {error_output}")
        return error_output, "error"

# Test the problematic instruction
test_web_execution("Open youtube and search sad songs")
print("=" * 50)

# Also test the exact instruction you're using
test_web_execution("Open youtube and search sad songs")
