from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu'
        ]
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    try:
        print(f"Navigating to: https://www.youtube.com")
        page.goto("https://www.youtube.com", timeout=10000)
        page.wait_for_load_state("networkidle")
        print(f"Successfully loaded: {page.title()}")
    except Exception as e:
        print(f"ERROR: {e}")
        raise e
    
    browser.close()
