from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    user_input = request.form["testcase"]
    
    print("User Test Case:", user_input)
    
    return f"AI Agent Received: {user_input}"

if __name__ == "__main__":
    app.run(debug=True)
