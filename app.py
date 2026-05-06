from flask import Flask, render_template, request
import json
from parser import parse_instruction
from code_generator import generate_code
from workflow import run_steps

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    instruction = ""
    steps = []
    code = ""
    logs = []
    result = ""
    report = None
    steps_json = ""

    if request.method == "POST":
        instruction = request.form.get("instruction", "").strip()
        action = request.form.get("action", "")

        if instruction:
            steps = parse_instruction(instruction)
            code = generate_code(steps)
            steps_json = json.dumps(steps, indent=4)

            if not steps:
                result = "Parser could not understand the instruction."
            elif action == "parse":
                result = "Instruction parsed successfully."
            elif action == "run":
                logs, report = run_steps(steps)
                result = "Execution completed successfully."
        else:
            result = "Please enter an instruction."

    return render_template(
        "index.html",
        instruction=instruction,
        steps=steps,
        steps_json=steps_json,
        code=code,
        logs=logs,
        result=result,
        report=report
    )

if __name__ == "__main__":
    app.run(debug=True)