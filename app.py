from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import time
import os

app = Flask(__name__)

RESULT = {}

@app.route("/", methods=["GET", "POST"])
def index():
    global RESULT

    if request.method == "POST":
        instruction = request.form["instruction"]

        steps = []
        screenshot_path = "static/screenshot.png"

        start = time.time()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # STEP 1
            page.goto("https://www.youtube.com")
            steps.append({
                "title": "Step 1: open_url",
                "status": "Success",
                "details": "{'action': 'open_url', 'url': 'https://www.youtube.com'}",
                "code": "page.goto('https://www.youtube.com')"
            })
            time.sleep(3)

            # STEP 2
            page.fill("input[name='search_query']", "mr english channel")
            page.keyboard.press("Enter")
            steps.append({
                "title": "Step 2: search",
                "status": "Success",
                "details": "{'action': 'search', 'query': 'mr english channel'}",
                "code": "page.fill('input[name=search_query]', 'mr english channel'); page.keyboard.press('Enter')"
            })
            time.sleep(4)

            # STEP 3
            page.click("ytd-video-renderer a#video-title")
            steps.append({
                "title": "Step 3: click",
                "status": "Success",
                "details": "{'action': 'click', 'target': 'first video'}",
                "code": "page.click('ytd-video-renderer a#video-title')"
            })
            time.sleep(5)

            # screenshot
            if not os.path.exists("static"):
                os.makedirs("static")

            page.screenshot(path=screenshot_path)

            # browser close delay (important)
            time.sleep(10)

            browser.close()

        end = time.time()

        RESULT = {
            "instruction": instruction,
            "steps": steps,
            "status": "Success",
            "total_steps": len(steps),
            "time": round(end - start, 2),
            "screenshot": screenshot_path
        }

    return render_template("index.html", result=RESULT)


if __name__ == "__main__":
    app.run(debug=True)