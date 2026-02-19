from langgraph.graph import StateGraph
from agent.state import AgentState
from agent.parser import parse_instruction

def instruction_node(state: AgentState):
    state["parsed_steps"] = parse_instruction(state["instruction"])
    return state

workflow = StateGraph(AgentState)
workflow.add_node("instruction_parser", instruction_node)
workflow.set_entry_point("instruction_parser")

agent_graph = workflow.compile()
