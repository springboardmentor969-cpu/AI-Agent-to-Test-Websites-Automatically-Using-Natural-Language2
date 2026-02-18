from flask import Flask, render_template, request
from agent.groq_agent import app as agent_app, State
from agent.parser import parse_instruction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    actions = None

    if request.method == "POST":
        user_input = request.form["instruction"]

        actions = parse_instruction(user_input)

        response = agent_app.invoke(State(input=user_input))
        result = response["output"]


    return render_template("index.html", result=result, actions=actions)

if __name__ == "__main__":
    app.run(debug=True)
