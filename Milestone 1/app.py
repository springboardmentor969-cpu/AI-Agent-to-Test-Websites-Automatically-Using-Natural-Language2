from flask import Flask, render_template, request, jsonify
from agent import graph
from playwright.sync_api import sync_playwright
import traceback
import json

app = Flask(__name__)

def execute_playwright_code(code):
    """
    Execute generated Playwright code in a browser
    """
    try:
        cleaned_code = code.strip()

        if cleaned_code.startswith("```"):
            cleaned_code = cleaned_code.replace("```python", "").replace("```", "").strip()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            
            local_scope = {"page": page}
            exec(cleaned_code, {}, local_scope)
             
            page.wait_for_timeout(5000)
            browser.close()
            
        return {
            "status": "success",
            "message": "✅ Execution Successful"
        }
    except Exception as e:
        error_details = traceback.format_exc()
        return {
            "status": "error",
            "message": f"❌ Execution Failed:\n{error_details}"
        }


@app.route("/", methods=["GET", "POST"])
def index():    
    """
    Main route - handles test case input and execution
    """
    generated_code = None
    execution_status = None
    user_input = None
    parsed_actions = None
    playwright_commands = None

    if request.method == "POST":
        user_input = request.form["user_input"]
        
        # Run through the LangGraph workflow
        print(f"\n{'='*60}")
        print(f"Processing new test case...")
        print(f"{'='*60}\n")
        
        result = graph.invoke({"input": user_input})
        
        # Extract results
        generated_code = result.get("output", "")
        parsed_actions = result.get("parsed_actions", [])
        playwright_commands = result.get("playwright_commands", [])
        
        # Execute the generated code
        execution_result = execute_playwright_code(generated_code)
        execution_status = execution_result["message"]

    return render_template(
        "index.html", 
        generated_code=generated_code, 
        status=execution_status,
        user_input=user_input,
        parsed_actions=parsed_actions,
        playwright_commands=playwright_commands
    )


@app.route("/api/parse", methods=["POST"])
def api_parse():
    """
    API endpoint to just parse without executing
    Useful for testing the parser
    """
    data = request.get_json()
    user_input = data.get("input", "")
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    # Run only the parsing phase
    result = graph.invoke({"input": user_input})
    
    return jsonify({
        "parsed_actions": result.get("parsed_actions", []),
        "playwright_commands": result.get("playwright_commands", []),
        "generated_code": result.get("output", "")
    })


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "milestone": "2"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)








from flask import Flask,render_template, request
from agent import graph
from playwright.sync_api import sync_playwright
import traceback 

app = Flask(__name__)

def execute_playwright_code(code):
    try:
        cleaned_code = code.strip()

        if cleaned_code.startswith("```"):
            cleaned_code = cleaned_code.replace("```python", "").replace("```", "").strip()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            #page.goto("https://demo.playwright.dev/todomvc")
            local_scope = {"page": page}
            exec(cleaned_code,{}, local_scope)
             
            page.wait_for_timeout(5000)
            browser.close()
        return "✅ Execution Successful"
    except Exception as e:
        error_details = traceback.format_exc()
        return f"❌ Execution Failed:\n{error_details}"  
    
@app.route("/", methods=["GET", "POST"])
def index():    
    generated_code = None
    status = None
    user_input = None

    if request.method == "POST":
        user_input = request.form["user_input"]
        result = graph.invoke({"input": user_input})
        generated_code = result["output"]
        status = execute_playwright_code(generated_code)

    return render_template(
        "index.html", 
        generated_code=generated_code, 
        status=status,
        user_input=user_input
    )


if __name__ == "__main__":
    app.run(debug=True)
