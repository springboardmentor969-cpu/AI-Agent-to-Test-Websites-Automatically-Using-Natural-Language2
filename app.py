<<<<<<< HEAD
from flask import Flask, request, render_template_string
from parser import parse_instruction

app = Flask(__name__)

html_page = """
<h2>AI Agent to Test Websites</h2>

<form method="post">

<textarea name="instruction" rows="8" cols="60"
placeholder="Enter test instructions here"></textarea>

<br><br>

<button type="submit">Run Parser</button>

</form>

"""

@app.route("/", methods=["GET","POST"])

def home():

    if request.method == "POST":

        text = request.form["instruction"]

        result = parse_instruction(text)

        return f"<h3>Parsed Steps:</h3><pre>{result}</pre>"

    return html_page
=======
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
>>>>>>> e044d7f8c5917a5c0ff96fcae2f6001f448886aa


if __name__ == "__main__":
    app.run(debug=True)