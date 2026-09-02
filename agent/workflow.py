from typing import Any

from agent.assertions import infer_expected_result
from agent.codegen import generate_playwright_code
from agent.executor import run_generated_test, write_generated_test
from agent.parser import parse_instruction_details

try:
    from langgraph.graph import END, StateGraph
except Exception:
    END = "__end__"
    StateGraph = None


WorkflowState = dict[str, Any]


# 🔹 STEP 1: PARSE INPUT
def parse_node(state: WorkflowState) -> WorkflowState:
    parsed = parse_instruction_details(state["input"])

    return {
        **state,
        "parsed": parsed,
        "actions": parsed.actions_as_dicts(),
    }


# 🔹 STEP 2: INFER EXPECTED RESULT
def assertion_node(state: WorkflowState) -> WorkflowState:
    parsed = state["parsed"]
    expected = infer_expected_result(parsed)

    return {
        **state,
        "expected_result": expected,
    }


# 🔹 STEP 3: GENERATE PLAYWRIGHT CODE
def codegen_node(state: WorkflowState) -> WorkflowState:
    code = generate_playwright_code(
        parsed=state["parsed"],
        expected_result=state.get("expected_result"),
    )

    return {
        **state,
        "generated_code": code,
    }


# 🔹 STEP 4: EXECUTE TEST
def execution_node(state: WorkflowState) -> WorkflowState:
    write_generated_test(state["generated_code"])

    execution = run_generated_test()

    # 🧠 REPORT GENERATION
    if execution.success:
        status = "PASS"
    else:
        status = "FAIL"

    report = {
        "status": status,
        "output": execution.summary,
        "returncode": execution.returncode,
    }

    return {
        **state,
        "execution_output": execution.summary,
        "execution_success": execution.success,
        "execution_returncode": execution.returncode,
        "report": report,
    }


# 🔹 FALLBACK (no LangGraph)
class FallbackWorkflow:
    def invoke(self, state: WorkflowState) -> WorkflowState:
        state = parse_node(state)
        state = assertion_node(state)
        state = codegen_node(state)

        if state.get("execute"):
            state = execution_node(state)

        return state


# 🔹 BUILD LANGGRAPH WORKFLOW
def build_workflow():
    if StateGraph is None:
        return FallbackWorkflow()

    graph = StateGraph(dict)

    graph.add_node("parse", parse_node)
    graph.add_node("assert", assertion_node)
    graph.add_node("codegen", codegen_node)
    graph.add_node("execute", execution_node)

    graph.set_entry_point("parse")

    graph.add_edge("parse", "assert")
    graph.add_edge("assert", "codegen")

    def route_after_codegen(state: WorkflowState) -> str:
        return "execute" if state.get("execute") else END

    graph.add_conditional_edges(
        "codegen",
        route_after_codegen,
        {"execute": "execute", END: END},
    )

    graph.add_edge("execute", END)

    return graph.compile()


_workflow = build_workflow()


# 🔹 MAIN ENTRY FUNCTION
def run_workflow(user_input: str, execute: bool = False) -> WorkflowState:
    return _workflow.invoke(
        {
            "input": user_input,
            "execute": execute,
        }
    )


# 🔹 TEST
if __name__ == "__main__":
    result = run_workflow(
        "Open login page and enter username test and password 1234 then click login",
        execute=True,
    )

    print("ACTIONS:", result.get("actions"))
    print("REPORT:", result.get("report"))