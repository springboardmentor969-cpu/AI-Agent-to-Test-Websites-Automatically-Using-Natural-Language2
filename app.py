from flask import Flask, render_template, request
from agent import process_instruction
from reporter import generate_report

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result    = None
    execution = None
    report    = None

    if request.method == "POST":
        user_input = request.form.get("instruction", "").strip()

        if user_input:
            output    = process_instruction(user_input)
            result    = output.get("code", "")
            execution = output.get("execution", {})
            report    = generate_report(user_input, result, execution)
        else:
            result = "# Please enter a valid instruction."

    return render_template("index.html", result=result, execution=execution, report=report)


if __name__ == "__main__":
    app.run(debug=True)