from flask import Flask, render_template, request
from agent import graph

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    response = None

    if request.method == "POST":
        user_input = request.form["user_input"]
        result = graph.invoke({"input": user_input})
        response = result["output"]

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)
