from flask import Flask, render_template, request
import json
from workflow import workflow
from validator import validate_output
from executor import execute_script

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    json_output = None
    execution_status = None
    playwright_code = None

    if request.method == "POST":
        test_case = request.form["testcase"]

        result = workflow.invoke({
            "input_text": test_case
        })

        parsed = result["parsed_command"]

        # Combine code
        code = result["playwright_code"] + "\n" + result["assertion_code"]

        playwright_code = code

        # Execute script
        success, error = execute_script(code)

        output = {
            "input_test_case": test_case,
            "url": result["url"],
            "parsed_command": {
                "action": parsed.action,
                "target": parsed.target,
                "value": parsed.value,
                "expected_result": parsed.expected_result
            },
            "generated_code": code,
            "validation": validate_output(code),
            "execution": success if success else error
        }

        # ✅ Convert to JSON string
        json_output = json.dumps(output, indent=4)

    return render_template("index.html",
                           json_output=json_output,
                           execution_status=execution_status,
                           playwright_code=playwright_code)


if __name__ == "__main__":
    app.run(debug=True)