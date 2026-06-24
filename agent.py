import os
import re
import json
import tempfile
import subprocess
import sys
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables.")
client = Groq(api_key=api_key)


# ---------------------------
# 1. Parser Node
# ---------------------------
def parser_node(state):
    instruction = state.get("instruction", "").strip()
    if not instruction:
        return {"error": "No instruction provided."}

    action_keywords = ["open", "click", "enter", "verify", "submit",
                       "navigate", "select", "type", "check", "fill", "search", "login",
                       "go to", "visit", "launch", "test", "load", "web", "site", "www",
                       "http", ".com", ".org", ".net", ".io"]
    if not any(word in instruction.lower() for word in action_keywords):
        return {"error": "Invalid test instruction. Please provide actionable website test steps."}

    # Normalize common site names to URLs
    site_map = {
        "whatsappweb" : "https://web.whatsapp.com",
        "whatsapp"    : "https://web.whatsapp.com",
        "youtube"     : "https://www.youtube.com",
        "google"      : "https://www.google.com",
        "github"      : "https://www.github.com",
        "facebook"    : "https://www.facebook.com",
        "instagram"   : "https://www.instagram.com",
        "twitter"     : "https://www.twitter.com",
        "linkedin"    : "https://www.linkedin.com",
        "reddit"      : "https://www.reddit.com",
        "gmail"       : "https://mail.google.com",
        "netflix"     : "https://www.netflix.com",
        "amazon"      : "https://www.amazon.com",
    }
    instruction_lower = instruction.lower()
    # whatsappweb must come before whatsapp in site_map (already ordered above)
    for site, url in site_map.items():
        if site in instruction_lower:
            instruction = instruction.lower().replace(site, url)
            break

    prompt = f"""You are a JSON-only API. Output ONLY a raw JSON array. No markdown. No explanation.

Convert: "{instruction}"

Rules:
- ALWAYS include open_page first
- If the instruction is ONLY "open [site]" with NO other action words → ONLY use open_page + verify. Nothing else.
- ONLY add enter_text if instruction contains words like: search, type, enter, fill, write, input
- ONLY add click if instruction contains words like: click, press, submit, tap
- ALWAYS end with verify
- Minimum 2 steps, maximum 4 steps

Examples:

"open https://web.whatsapp.com" ->
[{{"action":"open_page","target":"https://web.whatsapp.com"}},{{"action":"wait","target":"page loaded"}},{{"action":"verify","target":"WhatsApp"}}]

"open https://www.youtube.com and search python" ->
[{{"action":"open_page","target":"https://www.youtube.com"}},{{"action":"enter_text","field":"search_query","value":"python"}},{{"action":"click","target":"search button"}},{{"action":"verify","target":"YouTube"}}]

"open https://www.github.com" ->
[{{"action":"open_page","target":"https://www.github.com"}},{{"action":"wait","target":"page loaded"}},{{"action":"verify","target":"GitHub"}}]

"open https://www.google.com and search cats" ->
[{{"action":"open_page","target":"https://www.google.com"}},{{"action":"enter_text","field":"q","value":"cats"}},{{"action":"click","target":"search button"}},{{"action":"verify","target":"cats - Google Search"}}]

Use only these action types:
- open_page:  {{"action":"open_page","target":"full_url"}}
- enter_text: {{"action":"enter_text","field":"field_name","value":"text"}}
- click:      {{"action":"click","target":"element name"}}
- verify:     {{"action":"verify","target":"expected page title"}}
- wait:       {{"action":"wait","target":"element description"}}

IMPORTANT: For verify step use the REAL website title:
- web.whatsapp.com -> "WhatsApp"
- youtube.com      -> "YouTube"
- google.com       -> "Google"
- github.com       -> "GitHub"
- facebook.com     -> "Facebook"
- instagram.com    -> "Instagram"
- twitter.com      -> "X (formerly Twitter)"
- linkedin.com     -> "LinkedIn"
- reddit.com       -> "Reddit"
- mail.google.com  -> "Gmail"
- netflix.com      -> "Netflix"
- amazon.com       -> "Amazon"
- unknown sites    -> use the site name as title

OUTPUT ONLY THE JSON ARRAY:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only API. Output only a valid JSON array. No markdown, no explanation, no code fences."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        raw_output = response.choices[0].message.content.strip()
        raw_output = re.sub(r"```json|```python|```", "", raw_output).strip()

        start = raw_output.find("[")
        end   = raw_output.rfind("]")
        if start == -1 or end == -1:
            return {"error": f"No JSON array found. AI said: {raw_output[:200]}"}

        parsed_json = json.loads(raw_output[start:end+1])

        if not isinstance(parsed_json, list) or len(parsed_json) == 0:
            return {"error": "Invalid or empty JSON structure returned."}

        return {"parsed_steps": parsed_json}

    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {str(e)}. Raw: {raw_output[:200]}"}
    except Exception as e:
        return {"error": f"Parser error: {str(e)}"}

# ---------------------------
# 2. Generator Node
# ---------------------------
def generator_node(state):
    if "error" in state and "parsed_steps" not in state:
        return {"response": f"# Error: {state['error']}"}

    parsed_steps = state.get("parsed_steps", [])

    lines = []
    lines.append("from playwright.sync_api import sync_playwright, expect")
    lines.append("import re")
    lines.append("")
    lines.append("def run():")
    lines.append("    with sync_playwright() as p:")
    lines.append("        browser = p.chromium.launch(headless=False)")
    lines.append("        context = browser.new_context()")
    lines.append("        page = context.new_page()")
    lines.append("        page.set_default_timeout(30000)  # 30 seconds per action")

    for step in parsed_steps:
        action = step.get("action", "")

        if action == "open_page":
            target = step.get("target", "https://example.com")
            lines.append(f'        page.goto("{target}")  # open page')

        elif action == "enter_text":
            field = step.get("field", "input")
            value = step.get("value", "")
            lines.append(f'        page.locator("input[name=\'{field}\']").fill("{value}")  # enter text')
            
        elif action == "click":
            target = step.get("target", "button").lower()
            if "search" in target:
                lines.append(f'        page.locator("button.ytSearchboxComponentSearchButton").click()  # click search button')
            elif "login" in target or "submit" in target:
                lines.append(f'        page.locator("button[type=\'submit\']").click()  # click submit button')
            else:
                lines.append(f'        page.get_by_role("button", name="{target}").click()  # click element')

        if action == "open_page":
            target = step.get("target", "https://example.com")
            lines.append(f'        page.goto("{target}", wait_until="domcontentloaded", timeout=30000)  # open page')

        elif action == "wait":
            lines.append(f'        page.wait_for_load_state("domcontentloaded")  # wait for page')

    lines.append("        context.close()")
    lines.append("        browser.close()")
    lines.append("")
    lines.append("run()")

    return {"response": "\n".join(lines)}


# ---------------------------
# 3. Executor Node
# ---------------------------
def executor_node(state):
    code = state.get("response", "")

    if not code or code.startswith("# Error"):
        return {"execution_result": {"status": "skipped", "error": "No valid code to execute."}}

    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            tmp_path = f.name
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=60
        )

        os.unlink(tmp_path)

        if result.returncode == 0:
            return {"execution_result": {"status": "passed", "output": result.stdout or "Test completed successfully."}}
        else:
            return {"execution_result": {"status": "failed", "error": result.stderr}}

    except subprocess.TimeoutExpired:
        return {"execution_result": {"status": "failed", "error": "Execution timed out after 60 seconds."}}
    except Exception as e:
        return {"execution_result": {"status": "failed", "error": str(e)}}


# ---------------------------
# 4. LangGraph Workflow
# ---------------------------
workflow = StateGraph(dict)
workflow.add_node("parser",    parser_node)
workflow.add_node("generator", generator_node)
workflow.add_node("executor",  executor_node)
workflow.set_entry_point("parser")
workflow.add_edge("parser",    "generator")
workflow.add_edge("generator", "executor")
workflow.set_finish_point("executor")
app_graph = workflow.compile()


# ---------------------------
# 5. Main Function
# ---------------------------
def process_instruction(instruction):
    result = app_graph.invoke({"instruction": instruction})
    return {
        "code"     : result.get("response", ""),
        "execution": result.get("execution_result", {})
    }