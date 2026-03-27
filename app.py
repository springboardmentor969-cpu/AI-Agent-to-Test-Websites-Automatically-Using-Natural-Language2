from flask import Flask, request, render_template_string
from parser import parse_instruction
from code_generator import generate_code
from executor import run_test

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Automation Agent</title>
<style>
body {
    background: linear-gradient(to right, #1c3b4a, #2c5364);
    color: white;
    font-family: Arial;
    text-align: center;
}
.container {
    background: #1e1e1e;
    padding: 20px;
    border-radius: 10px;
    width: 500px;
    margin: 100px auto;
}
input {
    width: 90%;
    padding: 10px;
}
button {
    padding: 10px 20px;
    margin-top: 10px;
}
pre {
    text-align: left;
    background: black;
    padding: 10px;
    overflow-x: auto;
}
</style>
</head>

<body>
<div class="container">
<h2>🤖 AI Automation Agent</h2>

<form method="POST">
<input type="text" name="instruction" placeholder="open youtube and search python tutorial"/>
<br>
<button type="submit">Run Agent</button>
</form>

{% if actions %}
<h3>Parsed Actions</h3>
<pre>{{ actions }}</pre>
{% endif %}

{% if code %}
<h3>Generated Code</h3>
<pre>{{ code }}</pre>
{% endif %}

</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    actions = None
    code = None

    if request.method == "POST":
        instruction = request.form["instruction"]

        actions = parse_instruction(instruction)
        code = generate_code(actions)

        run_test(code)   # browser run avthundi

    return render_template_string(HTML, actions=actions, code=code)

if __name__ == "__main__":
    app.run(debug=True)