from flask import Flask, render_template, request
from agent import app as agent_app

app = Flask(__name__)

# show page


@app.route("/")
def home():
    return render_template("index.html")

# handle form submit


@app.route("/run", methods=["POST"])
def run_agent():
    instruction = request.form.get("instruction")

    # send instruction to LangGraph agent
    agent_app.invoke({"input": instruction})

    return "Instruction processed: " + instruction


if __name__ == "__main__":
    app.run(debug=True)
