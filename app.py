from flask import Flask, request
from workflow import graph

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        instruction = request.form["instruction"]

        result = graph.invoke({"instruction": instruction})

        return f"<h3>Generated Actions:</h3><p>{result}</p>"

    return '''
    <h2>Enter Test Instructions</h2>
    <form method="post">
        <textarea name="instruction" rows="6" cols="40"></textarea><br><br>
        <button type="submit">Submit</button>
    </form>
    '''

app.run(debug=True)