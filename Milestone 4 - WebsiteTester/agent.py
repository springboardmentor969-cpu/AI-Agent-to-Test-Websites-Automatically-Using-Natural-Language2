from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
import json
import re

from google import genai
from langgraph.graph import StateGraph, END
from typing import TypedDict

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


MODEL_NAME = "gemini-2.5-flash"



class AgentState(TypedDict):
    input:  str          
    steps:  list[dict]   
    output: str          




KNOWN_DOMAINS = {
    "google":    "https://www.google.com",
    "youtube":   "https://www.youtube.com",
    "github":    "https://www.github.com",
    "bing":      "https://www.bing.com",
    "yahoo":     "https://www.yahoo.com",
    "reddit":    "https://www.reddit.com",
    "twitter":   "https://www.twitter.com",
    "nptel":     "https://www.nptel.ac.in",
    "amazon":    "https://www.amazon.in",
    "flipkart":  "https://www.flipkart.com",
    "linkedin":  "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
}

def normalise_url(raw: str) -> str:
    raw = raw.strip().lower().rstrip("/")
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    base = raw.split(".")[0]
    if base in KNOWN_DOMAINS:
        return KNOWN_DOMAINS[base]
    if "." in raw:
        return "https://" + raw
    return "https://www." + raw + ".com"




PARSE_PROMPT = """\
You are a browser-automation instruction parser.

Convert the user's instruction into a JSON array of action steps.

Allowed action types and their required fields:
  {{"action": "open_url",   "url": "<full https:// URL>"}}
  {{"action": "search",     "text": "<search query>"}}
  {{"action": "click",      "element": "<css selector or description>"}}
  {{"action": "enter_text", "field": "<field name>", "text": "<value>"}}

Rules:
- Always output ONLY a raw JSON array. No markdown, no explanation, no code fences.
- For open_url, always produce a full URL starting with https://.
  Examples:  google  → https://www.google.com
             youtube.com → https://www.youtube.com
- If the instruction says "open X and search Y", produce TWO steps:
    open_url for X, then search for Y.
- Never produce page.goto() or any Python code.
- If you cannot parse the instruction, return:
    [{{"action": "error", "message": "Cannot parse: <reason>"}}]

User instruction: {instruction}
"""

def parse_node(state: AgentState) -> AgentState:

    user_input = state["input"]
    prompt     = PARSE_PROMPT.format(instruction=user_input)

    #model    = genai.GenerativeModel(MODEL_NAME)
    response = client.models.generate_content(model=MODEL_NAME , contents = prompt)
    raw      = response.text.strip()

    
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE).strip()
    raw = re.sub(r"```$",          "", raw, flags=re.MULTILINE).strip()

    try:
        steps = json.loads(raw)
        if not isinstance(steps, list):
            steps = [{"action": "error", "message": f"Expected list, got: {raw[:120]}"}]
    except json.JSONDecodeError as e:
        steps = [{"action": "error", "message": f"JSON parse failed: {e} | raw: {raw[:200]}"}]

    return {**state, "steps": steps}




def validate_node(state: AgentState) -> AgentState:
    """
    Validate and normalise each step:
      - open_url  → ensure URL is fully qualified
      - search    → ensure 'text' key exists and is non-empty
      - others    → pass through unchanged
    """
    steps      = state.get("steps", [])
    validated  = []

    for step in steps:
        action = step.get("action", "")

        if action == "open_url":
            raw_url = step.get("url", "")
            step["url"] = normalise_url(raw_url)
            validated.append(step)

        elif action == "search":
            text = step.get("text", "").strip()
            if not text:
                step["text"] = "unknown query"
            validated.append(step)

        elif action == "enter_text":
            if "field" not in step:
                step["field"] = "input"
            if "text" not in step:
                step["text"] = ""
            validated.append(step)

        elif action == "click":
            if "element" not in step:
                step["element"] = "button"
            validated.append(step)

        elif action == "error":
            validated.append(step)   

        else:
            
            validated.append(step)

    output_json = json.dumps(validated, indent=2, ensure_ascii=False)
    return {**state, "steps": validated, "output": output_json}




builder = StateGraph(AgentState)
builder.add_node("parse",    parse_node)
builder.add_node("validate", validate_node)
builder.set_entry_point("parse")
builder.add_edge("parse",    "validate")
builder.add_edge("validate", END)

graph = builder.compile()




def get_steps(instruction: str) -> list[dict]:
    """
    Convenience wrapper: run the graph and return the validated steps list.
    Falls back to an error step if anything goes wrong.
    """
    try:
        result = graph.invoke({"input": instruction, "steps": [], "output": ""})
        return result.get("steps", [])
    except Exception as exc:
        return [{"action": "error", "message": str(exc)}]




if __name__ == "__main__":
    tests = [
        "open google.com and search nptel courses",
        "open youtube.com and search lofi music",
        "go to github.com and search langchain",
        "search python tutorials on bing",
    ]
    for instruction in tests:
        print(f"\nInstruction : {instruction}")
        steps = get_steps(instruction)
        print(f"Steps       :\n{json.dumps(steps, indent=2)}")
        print("-" * 55)




'''from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    input: str
    output: str
'''
'''def agent_node(state: AgentState):
    user_input = state["input"]

    prompt = f"""Answer in fewer points.
    Keep the answer it concised and structured format.
    Question: {user_input}
    """

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)

    return {"output": response.text}
'''
'''
def agent_node(state: AgentState):
    user_input = state["input"]

    prompt = f"""
    You are a Playwright automation expert.

    Convert the user's instruction into valid Playwright Python code.

    IMPORTANT:
- Do NOT open any website.
- Do NOT use page.goto().
- Do NOT use page.wait_for_load_state().
- Assume the page is already open.

Rules:
- If the instruction includes "search", generate only the search-related steps.
- Use page.fill() for typing into input fields.
- Use page.click() for clicking buttons or elements.
- Use page.press() for pressing keys like Enter.
- Do NOT include browser launch code.
- Do NOT include explanations.
- Return only valid Python Playwright commands.
- Do NOT wrap the code in markdown (no ``` blocks).


Instruction:
{user_input}
    """

    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)

    return {"output": response.text}

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"input": "What is Machine Learning?"})
    print(result["output"])
'''