from flask import Flask, render_template, request
from agent.parser import parse_instruction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        user_input = request.form["instruction"]
        result = parse_instruction(user_input)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
