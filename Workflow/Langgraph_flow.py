"""
LangGraph Workflow — Parser → Generator → Executor
-----------------------------------------------------
Connects all three modules into a single executable graph:

  1. parser_node    — NL instruction → list of structured JSON actions
  2. generator_node — actions → Playwright Python script (for display/logging)
  3. executor_node  — actions → browser execution → PASS/FAIL result

Usage:
    from workflow.langgraph_flow import build_graph

    graph = build_graph()
    result = graph.invoke({"input": "Go to YouTube and search for lofi music"})
"""

from langgraph.graph import StateGraph
from typing import TypedDict, Any

from parser.instruction_parser import parse_instruction
from generator.code_generator import generate_playwright_code
from executor.playwright_runner import execute_actions


class AgentState(TypedDict, total=False):
    input: str
    actions: list
    generated_code: str
    requires_headed: bool
    execution_result: dict


# ─── Node 1: Parse NL → structured actions ───────────────────────────────────

def parser_node(state: AgentState) -> dict:
    """Convert the natural-language instruction into structured actions."""
    instruction = state["input"]
    print(f"\n[Workflow] Parsing: {instruction}")
    actions = parse_instruction(instruction)
    print(f"[Workflow] Parsed {len(actions)} actions")
    return {"actions": actions}


# ─── Node 2: Generate Playwright script (for display) ────────────────────────

def generator_node(state: AgentState) -> dict:
    """Generate Playwright Python code from the parsed actions."""
    actions = state.get("actions", [])
    if not actions:
        return {"generated_code": "# No actions to generate code for", "requires_headed": False}

    script, requires_headed = generate_playwright_code(actions)
    print(f"[Workflow] Generated script ({len(script)} chars), headed={requires_headed}")
    return {"generated_code": script, "requires_headed": requires_headed}


# ─── Node 3: Execute in browser ──────────────────────────────────────────────

def executor_node(state: AgentState) -> dict:
    """Execute the parsed actions in a Playwright browser."""
    actions = state.get("actions", [])
    if not actions:
        return {"execution_result": {"status": "FAIL", "steps_executed": 0, "error": "No actions to execute"}}

    requires_headed = state.get("requires_headed", False)
    headless = not requires_headed

    print(f"[Workflow] Executing {len(actions)} actions (headless={headless})")
    result = execute_actions(actions, headless=headless)
    
    summary = result.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    overall_status = "PASS" if failed == 0 and passed > 0 else "FAIL"
    
    print(f"[Workflow] Result: {overall_status} ({passed} passed, {failed} failed)")
    return {"execution_result": result}


# ─── Graph Assembly ──────────────────────────────────────────────────────────

def build_graph():
    """Build and compile the full LangGraph workflow."""
    graph = StateGraph(AgentState)

    graph.add_node("parser", parser_node)
    graph.add_node("generator", generator_node)
    graph.add_node("executor", executor_node)

    graph.set_entry_point("parser")
    graph.add_edge("parser", "generator")
    graph.add_edge("generator", "executor")
    graph.set_finish_point("executor")

    return graph.compile()