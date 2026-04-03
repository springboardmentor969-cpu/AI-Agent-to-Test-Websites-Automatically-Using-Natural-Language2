from flask import Flask, render_template, request, jsonify
from parser import parse_instruction
from executor import run_test

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    instruction = data.get("instruction", "")

    parsed = parse_instruction(instruction)
    result = run_test(parsed)

    return jsonify({
        "status": result["status"],
        "steps": result["steps"],
        "time": result["time"],
        "parsed_actions": parsed["actions"]
    })

@app.route('/result')
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True)