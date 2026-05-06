from playwright.sync_api import sync_playwright

def run_test():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        browser.close()
    return results

print(run_test())