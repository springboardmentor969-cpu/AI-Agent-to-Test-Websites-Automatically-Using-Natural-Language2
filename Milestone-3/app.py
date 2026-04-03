from flask import Flask, render_template, request, jsonify
from agent import run_agent

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    instruction = request.json.get("instruction")
    result = run_agent(instruction)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)