"""
Flask Application — AI Test Automation Agent
----------------------------------------------
Routes:
  GET  /         → Main UI (enter natural language test instructions)
  POST /         → Run the full LangGraph pipeline (NL → parse → generate → execute)
  GET  /sample   → Sample login page (test target)
  POST /sample   → Handle sample login form submission
  POST /run      → Direct JSON actions API (bypass NL parsing)
"""

from flask import Flask, request, jsonify, render_template
from workflow.langgraph_flow import build_graph
from milestone3.main import run_test

app = Flask(__name__)
graph = build_graph()


# ─── Main UI ─────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if not user_input.strip():
            return jsonify({"error": "Please enter a test instruction."}), 400

        try:
            result = graph.invoke({"input": user_input})
            return jsonify({
                "input": user_input,
                "parsed_actions": result.get("actions", []),
                "generated_code": result.get("generated_code", ""),
                "execution_result": result.get("execution_result", {}),
            })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return render_template("index.html")


# ─── Direct JSON Actions API ─────────────────────────────────────────────────

@app.route("/run", methods=["POST"])
def run_actions():
    """
    Accept raw JSON actions and execute them directly.

    Example POST body:
    {
      "actions": [
        {"type": "navigate", "url": "https://www.youtube.com"},
        {"type": "input", "selector": "input[name='search_query']", "value": "lofi music"},
        {"type": "press", "key": "Enter"},
        {"type": "wait", "duration": 5000}
      ]
    }
    """
    data = request.get_json(force=True)
    if not data or "actions" not in data:
        return jsonify({"error": "Request body must contain an 'actions' array."}), 400

    result = run_test(data)
    return jsonify(result)


# ─── Sample Login Page (Test Target) ─────────────────────────────────────────

@app.route("/sample", methods=["GET", "POST"])
def sample_page():
    message = None
    msg_type = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "password123":
            message = "Login successful! Welcome, admin."
            msg_type = "success"
        else:
            message = "Invalid credentials. Please try again."
            msg_type = "error"

    return render_template("test_page.html", message=message, msg_type=msg_type)


if __name__ == "__main__":
    app.run(debug=True)