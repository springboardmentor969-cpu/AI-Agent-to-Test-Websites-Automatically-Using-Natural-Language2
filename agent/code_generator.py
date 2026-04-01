def generate_code(actions):

    code = []

    for action in actions:

        action_type = action.get("action")

        # ---------------- OPEN URL ----------------
        if action_type == "open_url":

            url = action.get("url")

            code.append({
                "action": "open_url",
                "details": action,
                "code": f'''
page.goto("{url}")
page.wait_for_load_state("domcontentloaded")
page.wait_for_timeout(3000)
'''
            })

        # ---------------- SEARCH (FIXED) ----------------
        elif action_type == "search":

            query = action.get("query")

            code.append({
                "action": "search",
                "details": action,
                "code": f'''
# -------- YOUTUBE SEARCH FIX --------
try:
    box = page.locator("input#search").first
    if box.count() > 0:
        box.fill("{query}")
        page.keyboard.press("Enter")
    else:
        raise Exception("YT search not found")

except:
    # -------- GENERIC SEARCH --------
    try:
        box = page.locator("input, textarea").first
        box.fill("{query}")
        page.keyboard.press("Enter")
    except:
        print("Search failed")

page.wait_for_load_state("networkidle")
'''
            })

        # ---------------- CLICK (FIXED) ----------------
        elif action_type == "click":

            target = action.get("target", "")

            code.append({
                "action": "click",
                "details": action,
                "code": f'''
clicked = False

page.wait_for_timeout(3000)

# -------- YOUTUBE FIRST VIDEO --------
if "video" in "{target}".lower() or "first" in "{target}".lower():
    try:
        page.wait_for_selector("ytd-video-renderer", timeout=10000)

        videos = page.locator("ytd-video-renderer")

        for i in range(videos.count()):
            video = videos.nth(i)

            # Skip ads
            if video.locator("span:has-text('Ad')").count() > 0:
                continue

            title = video.locator("#video-title").first

            if title.count() > 0 and title.is_visible():
                title.click()
                clicked = True
                break
    except:
        pass


# -------- TEXT CLICK --------
if not clicked:
    try:
        page.locator(f"text={{'{target}'}}").first.click()
        clicked = True
    except:
        pass


# -------- GENERIC FALLBACK --------
if not clicked:
    try:
        page.locator("a").first.click()
        clicked = True
    except:
        pass


if not clicked:
    print("Click failed")

page.wait_for_timeout(3000)
'''
            })

        # ---------------- TYPE ----------------
        elif action_type == "type":

            value = action.get("value")

            code.append({
                "action": "type",
                "details": action,
                "code": f'''
try:
    page.locator("input, textarea").first.fill("{value}")
except:
    print("Type failed")
'''
            })

        # ---------------- WAIT ----------------
        elif action_type == "wait":

            code.append({
                "action": "wait",
                "details": action,
                "code": '''
page.wait_for_timeout(3000)
'''
            })

    return code
