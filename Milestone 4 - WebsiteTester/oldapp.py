"""
from flask import Flask, render_template, request
from agent import graph

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    response = None

    if request.method == "POST":
        '''username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            response = "Login Successful"
        else:
            response = "Invalid Username or Password"
        '''
        user_input = request.form["user_input"]
        result = graph.invoke({"input": user_input})
        response = result["output"]

    return render_template("index.html", response=response)
"""
'''''
from flask import Flask,render_template, request
from agent import graph
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def execute_playwright_code(code):
    try:
        cleaned_code = code.strip()

        if cleaned_code.startswith("```"):
            cleaned_code = cleaned_code.replace("```python", "").replace("```", "").strip()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            return cleaned_code 
            page.wait_for_timeout(5000)
            browser.close()
        return "✅ Execution Successful"
    except Exception as e:
        return f"❌ Execution Failed: {str(e)}"
    
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
'''