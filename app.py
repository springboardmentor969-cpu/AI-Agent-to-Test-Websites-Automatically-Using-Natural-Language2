from flask import Flask, render_template, request
from parser import parse_test_steps
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":
        # Get user instruction from form
        instruction = request.form.get("instruction")   
        if instruction:
            received_msg = f"Received Instruction: {instruction}"
            #  Call AI Parser
            steps = parse_test_steps(instruction)

            # Print in terminal (for debugging)
            print("Parsed Steps:", steps)

            # Convert to pretty JSON for display
            response = received_msg + "\n\nParsed Steps:\n" + json.dumps(steps, indent=2)
        else:
            response = "No instruction provided."

    return render_template("index.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
