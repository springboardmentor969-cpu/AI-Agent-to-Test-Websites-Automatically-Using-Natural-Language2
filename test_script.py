from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.amazon.in")
    time.sleep(3)
    page.fill("input[type=text]", "us polo shirts")
    page.keyboard.press("Enter")
    time.sleep(5)
    input("Press Enter to close...")
    browser.close()