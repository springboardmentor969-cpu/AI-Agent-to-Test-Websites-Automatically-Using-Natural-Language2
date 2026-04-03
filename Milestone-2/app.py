from flask import Flask, render_template, request, jsonify
from agent import run_agent

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run():

    data = request.get_json()

    user_input = data.get("user_input")

    result = run_agent(user_input)

    return jsonify({
        "status": "success",
        "input": user_input,
        "parsed": result["parsed"],
        "generated_code": result["generated_code"]
    })


if __name__ == "__main__":
    app.run(debug=True)