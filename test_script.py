from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.youtube.com")
    time.sleep(3)
    page.fill("input[name=search_query]", "mr english channel and open first video")
    page.keyboard.press("Enter")
    time.sleep(5)
    page.click("ytd-video-renderer a#video-title")
    time.sleep(8)
    if not os.path.exists("static"):
        os.makedirs("static")
    page.screenshot(path="static/screenshot.png")
    time.sleep(2)
    browser.close()