# -------------------------------
# Import LangGraph
# -------------------------------
from langgraph.graph import StateGraph
from typing import TypedDict

# -------------------------------
# Define Agent State (IMPORTANT FIX)
# -------------------------------


class AgentState(TypedDict):
    input: str


# -------------------------------
# Node Function
# -------------------------------

def handle_input(state: AgentState):
    user_input = state["input"]

    print("User Instruction:", user_input)

    return state


# -------------------------------
# Create Workflow
# -------------------------------

workflow = StateGraph(AgentState)

workflow.add_node("input_handler", handle_input)

workflow.set_entry_point("input_handler")

app = workflow.compile()


# -------------------------------
# Test Run
# -------------------------------

if __name__ == "__main__":
    app.invoke({"input": "Click login button"})
