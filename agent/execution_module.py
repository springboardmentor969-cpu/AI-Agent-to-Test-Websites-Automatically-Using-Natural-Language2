from playwright.sync_api import sync_playwright
import time
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

AUTH_FILE = "auth.json"


# ---------------- SESSION MANAGEMENT ----------------
def create_context(browser):
    if os.path.exists(AUTH_FILE):
        print("✅ Using saved session")
        return browser.new_context(storage_state=AUTH_FILE)
    else:
        print("⚠️ No session found, starting fresh")
        return browser.new_context()


# ---------------- LLM NEXT ACTION ----------------
def get_next_action(instruction, html):

    prompt = f"""
You are a web automation agent.

Goal:
{instruction}

Current page HTML:
{html[:2000]}

Decide next step.

Allowed:
click, type, wait, done

Return JSON:
{{"action":"...", "target":"...", "value":"..."}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print("LLM next action error:", e)
        return None


# ---------------- EXECUTE LLM ACTION ----------------
def execute_llm_action(page, action):

    try:
        act = action.get("action")

        if act == "click":
            page.locator(f"text={action.get('target', '')}").first.click()

        elif act == "type":
            page.locator("input, textarea").first.fill(action.get("value", ""))

        elif act == "wait":
            page.wait_for_timeout(2000)

        elif act == "done":
            return True

        return False

    except Exception as e:
        print("LLM action failed:", e)
        return False


# ---------------- MAIN EXECUTION ----------------
def execute_test_case(state):

    steps = state["generated_code"]
    instruction = state["instruction"]

    report_steps = []
    start_time = time.time()

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            context = create_context(browser)
            page = context.new_page()

            # -------- EXECUTE PLANNED STEPS --------
            for i, step in enumerate(steps):

                action = step.get("action", "unknown")
                code_block = step.get("code", "")

                try:
                    exec(code_block)

                    report_steps.append({
                        "step": i + 1,
                        "action": action,
                        "details": step.get("details", {}),
                        "code": code_block,   # ✅ FIXED
                        "status": "Success"
                    })

                except Exception as e:

                    report_steps.append({
                        "step": i + 1,
                        "action": action,
                        "details": step.get("details", {}),
                        "code": code_block,   # ✅ FIXED
                        "status": "Failed",
                        "error": str(e)
                    })

                    break  # switch to agent mode

            # -------- LLM AGENT LOOP --------
            for _ in range(5):

                page.wait_for_timeout(2000)

                html = page.content()

                next_action = get_next_action(instruction, html)

                if not next_action:
                    break

                if next_action.get("action") == "done":
                    break

                success = execute_llm_action(page, next_action)

                report_steps.append({
                    "step": len(report_steps) + 1,
                    "action": "llm_" + next_action.get("action", ""),
                    "details": next_action,
                    "code": str(next_action),   # ✅ FIXED
                    "status": "Success" if success else "Failed"
                })

                if not success:
                    break

            # -------- SAVE SESSION --------
            try:
                context.storage_state(path=AUTH_FILE)
                print("✅ Session saved")
            except:
                pass

            # -------- FINAL --------
            page.wait_for_timeout(3000)
            page.screenshot(path="static/execution_result.png")

            browser.close()

        end_time = time.time()

        return {
            "status": "Success",
            "total_steps": len(report_steps),   # ✅ FIXED
            "execution_time": round(end_time - start_time, 2),
            "steps_log": report_steps
        }

    except Exception as e:

        end_time = time.time()

        return {
            "status": "Failed",
            "error": str(e),
            "total_steps": len(report_steps),   # ✅ FIXED
            "execution_time": round(end_time - start_time, 2),
            "steps_log": report_steps
        }
