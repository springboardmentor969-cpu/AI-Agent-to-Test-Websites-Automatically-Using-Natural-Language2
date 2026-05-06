from playwright.sync_api import sync_playwright
from agent import try_click, try_type, try_search
from reporter import generate_report

def run_steps(steps):
    logs = []
    step_results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for step in steps:
                action = step["action"]
                value = step["target"]

                try:
                    if action == "open":
                        logs.append(f"Opening {value}")
                        page.goto(value, wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(500)

                        step_results.append({
                            "step": step["description"],
                            "status": "success",
                            "message": f"Opened {value}",
                            "error": ""
                        })

                    elif action == "search":
                        query = step["value"]
                        logs.append(f"Searching for {query}")

                        searched = try_search(page, query)

                        if searched:
                            logs.append(f"Searched for {query} successfully")
                            page.wait_for_timeout(1500)

                            step_results.append({
                                "step": step["description"],
                                "status": "success",
                                "message": f"Searched for {query}",
                                "error": ""
                            })
                        else:
                            logs.append(f"Could not search for {query}")

                            step_results.append({
                                "step": step["description"],
                                "status": "failed",
                                "message": "",
                                "error": f"Could not perform search for {query}"
                            })

                    elif action == "click":
                        logs.append(f"Clicking {value}")

                        clicked = try_click(page, value)

                        if clicked:
                            logs.append(f"Clicked {value} successfully")
                            page.wait_for_timeout(1500)

                            step_results.append({
                                "step": step["description"],
                                "status": "success",
                                "message": f"Clicked {value}",
                                "error": ""
                            })
                        else:
                            logs.append(f"Could not click {value}")

                            step_results.append({
                                "step": step["description"],
                                "status": "failed",
                                "message": "",
                                "error": f"Could not click {value}"
                            })

                    elif action == "type":
                        text_value = step["value"]
                        field_name = step["target"]

                        logs.append(f"Typing '{text_value}' into {field_name}")

                        typed = try_type(page, field_name, text_value)

                        if typed:
                            logs.append(f"Typed successfully")
                            page.wait_for_timeout(1000)

                            step_results.append({
                                "step": step["description"],
                                "status": "success",
                                "message": f"Typed into {field_name}",
                                "error": ""
                            })
                        else:
                            step_results.append({
                                "step": step["description"],
                                "status": "failed",
                                "message": "",
                                "error": f"Could not find field"
                            })

                    elif action == "press_enter":
                        page.keyboard.press("Enter")

                    elif action == "verify":
                        if value.lower() in page.content().lower():
                            step_results.append({"step": step["description"], "status": "success"})
                        else:
                            step_results.append({"step": step["description"], "status": "failed"})

                except Exception as e:
                    step_results.append({"step": step["description"], "status": "failed", "error": str(e)})

            page.wait_for_timeout(10000)
            browser.close()

    except Exception as e:
        logs.append(f"Browser error: {str(e)}")

    report = generate_report(step_results)

    return logs, report