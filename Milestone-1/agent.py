from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# State structure
class AgentState(TypedDict):
    user_input: str
    output: str


# Function to generate Playwright automation code
def generate_code(state: AgentState) -> AgentState:

    query = state["user_input"]

    code = f"""
# Playwright Automation Script
# Task: Search "{query}" on Google

from playwright.sync_api import sync_playwright


def run_test():

    with sync_playwright() as p:

        # Step 1: Launch the browser
        browser = p.chromium.launch(headless=False)

        # Step 2: Open a new page
        page = browser.new_page()

        # Step 3: Navigate to Google
        page.goto("https://www.google.com")

        # Step 4: Locate the search box
        search_box = page.locator('input[name="q"]')

        # Step 5: Enter the search text
        search_box.fill("{query}")

        # Step 6: Press Enter
        search_box.press("Enter")

        # Step 7: Wait for results
        page.wait_for_timeout(5000)

        # Step 8: Close the browser
        browser.close()


# Run the automation
run_test()
"""

    return {
        "user_input": query,
        "output": code
    }


# Build LangGraph workflow
def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("generate_code", generate_code)

    builder.add_edge(START, "generate_code")
    builder.add_edge("generate_code", END)

    return builder.compile()


# Function called from app.py
def run_agent(user_input: str):

    graph = build_graph()

    result = graph.invoke({
        "user_input": user_input,
        "output": ""
    })

    return result["output"]