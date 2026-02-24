from langgraph.graph import StateGraph

class AgentState(dict):
    pass

def handle_input(state: AgentState):
    user_input = state.get("input")
    return {"output": f"Processed: {user_input}"}

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("handler", handle_input)
    graph.set_entry_point("handler")

    return graph.compile()

agent = build_agent()
