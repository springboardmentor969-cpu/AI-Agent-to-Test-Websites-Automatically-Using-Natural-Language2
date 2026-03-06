from flask import Flask, render_template, request, jsonify
from agent import run_agent

app = Flask(__name__)


# Load homepage
@app.route("/")
def home():
    return render_template("index.html")


# Handle user instruction
@app.route("/run", methods=["POST"])
def run():

    data = request.get_json()
    user_input = data.get("user_input")

    result = run_agent(user_input)

    return jsonify({"response": result})


if __name__ == "__main__":
    app.run(debug=True)