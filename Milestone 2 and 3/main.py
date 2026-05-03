from flask import Flask, render_template, request
from agent.instruction_parser import parse_instruction
from agent.code_generator import generate_code
#from executor.playwright import run_test
import sys
import threading
import json
import os
from datetime import datetime

app = Flask(__name__)

def save_instruction_history(instruction, actual_status, expected_status):
    """Save instruction to history file"""
    history_file = "instruction_history.json"
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new instruction
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instruction": instruction,
        "actual_status": actual_status,
        "expected_status": expected_status
    }
    history.append(new_entry)
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def console_mode():
    """Original console functionality"""
    print("AI Website Testing Agent\n")
    instruction = input("Enter testing instruction:\n")


    steps = parse_instruction(instruction)
    print("\nParsed Steps:")
    print(steps)


    code = generate_code(steps)


    exec(code)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/history')
def history():
    """Display instruction history"""
    history_file = "instruction_history.json"
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Reverse to show most recent first
    history.reverse()
    
    return render_template('history.html', history=history)

@app.route('/execute', methods=['POST'])
def execute():
    instruction = request.form['instruction']
    
    print(f"EXECUTION STARTED: {instruction}")
    
    steps = parse_instruction(instruction)
    print(f"PARSED STEPS: {steps}")
    
    steps_json = json.dumps(steps, indent=2)
    
    code = generate_code(steps)
    print(f"GENERATED CODE: {code[:500]}...")
    
    # Step 3: Execute code and capture output
    try:
        # Execute the Playwright code
        import io
        import contextlib
        
        # Capture stdout to get execution output
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            exec(code)
        
        execution_output = captured_output.getvalue()
        print(f"EXECUTION OUTPUT: {execution_output}")
        
        # Detect PASS / FAIL for actual result - more precise checking
        execution_lines = execution_output.split('\n')
        test_passed_line = None
        results_obtained_line = None
        actual_status = "fail"   # default
        
        for line in execution_lines:
            if "TEST_PASSED:" in line:
                value = line.split("TEST_PASSED:")[1].strip().lower()
                
                if value == "true":
                    actual_status = "pass"
                else:
                    actual_status = "fail"
            elif "RESULTS_OBTAINED:" in line:
                results_obtained_line = line.strip()
        
        # Final check using RESULTS_OBTAINED if TEST_PASSED wasn't found
        if not test_passed_line and results_obtained_line:
            if "True" in results_obtained_line:
                actual_status = "pass"
            else:
                actual_status = "fail"
        # If TEST_PASSED was found, don't override it with RESULTS_OBTAINED logic
        elif "VALIDATION_ERROR" in execution_output:
            actual_status = "fail"
        else:
            actual_status = "fail"
        
        print(f"FINAL STATUS: {actual_status}")

    except AssertionError:
        execution_output = " Assertion Failed"
        actual_status = "fail"

    except BrokenPipeError:
        execution_output = " Browser process ended unexpectedly (Python 3.13 compatibility issue)"
        actual_status = "error"
    except Exception as e:
        error_msg = str(e).lower()
        if "epipe" in error_msg or "broken pipe" in error_msg or "node:events" in error_msg:
            execution_output = " Browser communication error - Code generation successful, but execution disabled due to Python 3.13 compatibility issues. Use Python 3.11/3.12 for full functionality."
            actual_status = "error"
        else:
            execution_output = f" Error: {str(e)}"
            actual_status = "error"
        
        print(f"EXECUTION ERROR: {execution_output}")

    # Expected output based on instruction analysis
    expected_status = "pass"
    expected_output = " Test Passed - Expected Result"
    
    # Determine expected result based on instruction
    instruction_lower = instruction.lower()
    if "invalid" in instruction_lower or "error" in instruction_lower or "fail" in instruction_lower:
        expected_status = "fail"
        expected_output = " Test Failed - Expected Result (Invalid instruction)"
    elif "open " in instruction_lower and not any(website in instruction_lower for website in ["google.com", "youtube.com", "github.com", "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "stackoverflow.com"]):
        # Check if it's trying to open an unknown/invalid website
        url_part = instruction_lower.split("open ")[1].strip() if "open " in instruction_lower else ""
        if not any(valid_site in url_part for valid_site in [".com", ".org", ".net", ".edu", ".gov"]):
            expected_status = "fail"
            expected_output = " Test Failed - Expected Result (Invalid website)"
        else:
            expected_status = "pass"
            expected_output = " Test Passed - Expected Result (Valid website)"
    elif "youtube.com" in instruction_lower and ("search" in instruction_lower or "type" in instruction_lower):
        expected_status = "pass"
        expected_output = " Test Passed - Expected Result (YouTube search should work)"
    elif "google.com" in instruction_lower and ("search" in instruction_lower or "type" in instruction_lower):
        expected_status = "pass"
        expected_output = " Test Passed - Expected Result (Google search should work)"
    elif "github.com" in instruction_lower:
        expected_status = "pass"
        expected_output = " Test Passed - Expected Result (GitHub should load)"
    else:
        expected_status = "pass"
        expected_output = " Test Passed - Expected Result (Valid website)"
    
    # Save instruction to history
    save_instruction_history(instruction, actual_status, expected_status)
    
    return render_template('result.html', 
                         instruction=instruction, 
                         steps=steps_json, 
                         code=code, 
                         actual_output=execution_output, 
                         actual_status=actual_status,
                         expected_output=expected_output,
                         expected_status=expected_status)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
 
        console_mode()
    else:

        print("Starting web server...")
        print("Open http://localhost:8000 in your browser")
        print("Use 'python main.py --console' for console mode")
        app.run(debug=False, port=8000, host='0.0.0.0')