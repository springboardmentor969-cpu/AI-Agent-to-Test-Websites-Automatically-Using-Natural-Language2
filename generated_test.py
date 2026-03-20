from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000/login")
    page.fill("#username", "jojosiwanot")
    page.fill("#password", "1234")
    page.click("#login")
    page.wait_for_timeout(500)
    expected_result = "Failed"
    result = page.inner_text("#result")
    print(result)
    if result != expected_result:
        raise AssertionError(f"Expected {expected_result!r}, got {result!r}")
    browser.close()