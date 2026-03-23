# main.py

from workflow import workflow
from executor import execute_script

test_case = "Click login button and should see Example Domain"

result = workflow.invoke({
    "input_text": test_case
})

playwright_code = result["playwright_code"]
assertion_code = result["assertion_code"]

# Combine both
final_script = f"""
{playwright_code}
{assertion_code}
"""

print("Generated Script:\n", final_script)

# Execute script
output, error = execute_script(final_script)

print("\nExecution Output:", output)
print("Error:", error)