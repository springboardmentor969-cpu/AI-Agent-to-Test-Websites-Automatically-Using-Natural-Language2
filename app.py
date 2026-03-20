from flask import Flask, render_template, request, send_from_directory

from agent.workflow import run_workflow

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    actions = None
    execution_output = None
    expected_result = None

    if request.method == "POST":
        user_input = request.form["instruction"]

        workflow_result = run_workflow(user_input, execute=True)
        actions = workflow_result["actions"]
        result = workflow_result["generated_code"]
        execution_output = workflow_result.get("execution_output")
        expected_result = workflow_result.get("expected_result")

    return render_template(
        "index.html",
        result=result,
        actions=actions,
        execution_output=execution_output,
        expected_result=expected_result,
    )


@app.route("/login")
def login_page():
    return send_from_directory("agent", "login.html")


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, threaded=True)
