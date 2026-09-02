from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.youtube.com", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    consent_buttons = [
        'button:has-text("Accept all")',
        'button:has-text("I agree")',
        'button:has-text("Accept")',
    ]
    for selector in consent_buttons:
        button = page.locator(selector).first
        if button.count() > 0:
            try:
                button.click(timeout=2000)
                page.wait_for_timeout(2000)
                break
            except Exception:
                pass

    search_box = page.locator('input[name="search_query"]').first
    if search_box.count() == 0:
        search_box = page.locator('input#search').first
    if search_box.count() == 0:
        raise RuntimeError("Could not find the YouTube search box")
    search_box.fill("music")
    search_box.press("Enter")
    page.wait_for_timeout(4000)

    first_video = None
    for selector in [
        'a[href*="/watch?v="]:visible',
        "a#video-title:visible",
        "a#video-title-link:visible",
        "ytd-rich-grid-media a#thumbnail:visible",
    ]:
        locator = page.locator(selector).first
        if locator.count() > 0:
            first_video = locator
            break

    if first_video is None:
        page.mouse.wheel(0, 1500)
        page.wait_for_timeout(2000)
        retry_locator = page.locator('a[href*="/watch?v="]:visible').first
        if retry_locator.count() > 0:
            first_video = retry_locator

    if first_video is None:
        raise RuntimeError("Could not find a clickable YouTube video on the page")

    first_video.scroll_into_view_if_needed(timeout=5000)
    first_video.click(timeout=10000)
    page.wait_for_timeout(3000)
    print("Clicked first YouTube video")
    browser.close()