from pathlib import Path

from playwright.sync_api import sync_playwright

def run_test():
    login_file = Path(__file__).with_name("login.html").resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(login_file)

        page.fill("#username", "test")
        page.fill("#password", "1234")

        page.click("#login")

        result = page.inner_text("#result")

        print("Result:", result)

        browser.close()


if __name__ == "__main__":
    run_test()
