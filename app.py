from flask import Flask, render_template, request
import json
from workflow import workflow
from validator import validate_output

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    json_output = None

    if request.method == "POST":
        test_case = request.form["testcase"]

        result = workflow.invoke({
            "input_text": test_case
        })

        parsed = result["parsed_command"]
        code = result["generated_code"]

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

        json_output = json.dumps(output, indent=4)

    return render_template("index.html", json_output=json_output)


if __name__ == "__main__":
    app.run(debug=True)