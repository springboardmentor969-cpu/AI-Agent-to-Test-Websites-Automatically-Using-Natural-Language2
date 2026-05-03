from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000")

    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "1234")
    page.click("button[type='submit']")

    page.wait_for_timeout(5000)
    browser.close()
