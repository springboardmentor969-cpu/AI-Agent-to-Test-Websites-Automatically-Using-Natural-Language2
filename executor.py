from playwright.sync_api import sync_playwright
import time

def run_test(parsed):
    steps = []
    start = time.time()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=False)
            page = browser.new_page()

            page.goto(parsed["url"])
            steps.append("Opened Amazon")

            page.wait_for_timeout(2000)

            page.fill("input#twotabsearchtextbox", parsed["search"])
            steps.append(f"Searched {parsed['search']}")

            page.keyboard.press("Enter")
            steps.append("Pressed Enter")

            page.wait_for_timeout(4000)

            page.screenshot(path="static/result.png")
            steps.append("Screenshot taken")

            browser.close()

        end = time.time()

        return {
            "status": "PASS",
            "steps": steps,
            "time": round(end - start, 2)
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "steps": [str(e)],
            "time": 0
        }