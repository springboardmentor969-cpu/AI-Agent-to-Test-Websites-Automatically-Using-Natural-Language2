import json
from workflow import workflow
from validator import validate_output

test_case = "Click the login button and should see dashboard"

# Run LangGraph workflow
result = workflow.invoke({
    "input_text": test_case
})

parsed = result["parsed_command"]
code = result["generated_code"]

# Create JSON output
output = {
    "input_test_case": test_case,
    "parsed_command": {
        "action": parsed.action,
        "target": parsed.target,
        "value": parsed.value,
        "expected_result": parsed.expected_result
    },
    "generated_code": code,
    "validation": validate_output(code)
}

# Print JSON output
print(json.dumps(output, indent=4))