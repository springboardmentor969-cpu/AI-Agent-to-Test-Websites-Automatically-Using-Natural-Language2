from flask import Flask, request, jsonify, send_from_directory
from agent.graph import agent_graph

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return "AI Web Testing Agent is Running"

@app.route("/test")
def test_page():
    return send_from_directory("static", "test_page.html")

# ✅ ADD THIS HERE
@app.route("/submit-test", methods=["POST"])
def submit_test():
    data = request.get_json()
    instruction = data.get("instruction", "")

    result = agent_graph.invoke({
        "instruction": instruction,
        "parsed_steps": []
    })

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
