from playwright.sync_api import sync_playwright

def execute_script(code):

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # visible browser
            page = browser.new_page()

            exec(code)

            input("Press Enter to close browser...")
            browser.close()

        return "Execution Successful", None

    except Exception as e:
        return None, str(e)