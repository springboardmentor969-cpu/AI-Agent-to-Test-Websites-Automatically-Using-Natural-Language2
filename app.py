from flask import Flask, render_template, request
from agent import process_instruction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        user_input = request.form.get("instruction")

        if user_input:
            result = process_instruction(user_input)
        else:
            result = "Please enter a valid instruction."

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)