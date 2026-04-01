from flask import Flask, render_template, request
from agent.workflow import create_workflow

app = Flask(__name__)

# Initialize workflow
workflow = create_workflow()


# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- RUN AUTOMATION ----------------
@app.route("/run", methods=["POST"])
def run():

    instruction = request.form.get("instruction")

    if not instruction:
        return "No instruction provided"

    try:
        result = workflow(instruction)

        # Safe extraction
        report = result.get("report", {})
        execution_status = result.get("execution_status", "Unknown")

        return render_template(
            "test.html",
            input_text=result.get("instruction", ""),
            parsed_actions=result.get("parsed_actions", []),
            generated_code=result.get("generated_code", []),
            execution_status=execution_status,
            report=report
        )

    except Exception as e:
        return f"Error occurred: {str(e)}"


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
