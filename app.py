from flask import Flask, request, jsonify, render_template
from workflow.langgraph_flow import build_graph


app = Flask(__name__)

graph = build_graph()

@app.route("/", methods=["GET", "POST"])
def index():
    response = None

    if request.method == "POST":
        user_input = request.form["user_input"]
        result = graph.invoke({"input": user_input})
        return jsonify(result)

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)

from workflow.langgraph_flow import build_graph


@app.route("/test", methods=["GET", "POST"])
def test():

    if request.method == "POST":

        instruction = request.form["instruction"]

        result = graph.invoke({
            "input": instruction
        })

        return jsonify(result)

    return render_template("index.html")