import re

def try_click(page, value):
    lower_value = value.lower().strip()

    position_words = {
        "first": 0,
        "1st": 0,
        "top": 0,
        "second": 1,
        "2nd": 1,
        "third": 2,
        "3rd": 2,
    }

    for word, index in position_words.items():
        if lower_value.startswith(word + " "):
            target_type = lower_value[len(word):].strip()

            try:
                current_url = page.url.lower()
            except:
                current_url = ""

            try:
                if "youtube.com" in current_url:
                    if "video" in target_type:
                        locator = page.locator("ytd-video-renderer a#video-title").nth(index)
                        locator.click(timeout=3000)
                        return True

                    if "result" in target_type:
                        locator = page.locator("ytd-video-renderer a#video-title").nth(index)
                        locator.click(timeout=3000)
                        return True

                if "google." in current_url:
                    if "result" in target_type or "link" in target_type:
                        locator = page.locator("h3").nth(index)
                        locator.click(timeout=3000)
                        return True

                if "link" in target_type:
                    locator = page.locator("a").nth(index)
                    locator.click(timeout=3000)
                    return True

                if "button" in target_type:
                    locator = page.locator("button").nth(index)
                    locator.click(timeout=3000)
                    return True

                if "video" in target_type:
                    locator = page.locator("a").nth(index)
                    locator.click(timeout=3000)
                    return True

            except:
                pass

    strategies = [
        lambda: page.get_by_role("button", name=value, exact=False).click(timeout=3000),
        lambda: page.get_by_role("link", name=value, exact=False).click(timeout=3000),
        lambda: page.get_by_text(value, exact=False).click(timeout=3000),
        lambda: page.locator(f"text={value}").first.click(timeout=3000),
    ]

    for strategy in strategies:
        try:
            strategy()
            return True
        except:
            pass

    return False


def try_type(page, field, text_value):
    selectors = [
        f"input[name*='{field.lower()}']",
        f"input[placeholder*='{field.lower()}']",
        f"input[id*='{field.lower()}']",
        f"textarea[name*='{field.lower()}']",
        f"textarea[placeholder*='{field.lower()}']",
        f"textarea[id*='{field.lower()}']",
        "input",
        "textarea"
    ]

    for selector in selectors:
        try:
            locator = page.locator(selector).first
            locator.fill(text_value, timeout=3000)
            return True
        except:
            pass

    return False


def try_search(page, query):
    current_url = page.url.lower()

    try:
        if "youtube.com" in current_url:
            search_box = page.locator("input[name='search_query']").first
            search_box.wait_for(state="visible", timeout=2000)
            search_box.click()
            search_box.fill(query)
            search_box.press("Enter")
            return True

        strategies = [
            lambda: page.locator("textarea[name='q']").first,
            lambda: page.locator("input[name='q']").first,
            lambda: page.locator("textarea").first,
            lambda: page.locator("input[type='search']").first,
            lambda: page.locator("input").first,
        ]

        for locator in strategies:
            try:
                box = locator()
                box.wait_for(state="visible", timeout=1200)
                box.click()
                box.fill(query)
                box.press("Enter")
                return True
            except:
                pass

    except:
        pass

    return False