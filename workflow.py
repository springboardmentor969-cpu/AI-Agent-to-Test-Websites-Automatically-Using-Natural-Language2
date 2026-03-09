from langgraph.graph import StateGraph
from parser import parse_instruction

def parser_node(state):

    instruction = state["instruction"]

    parsed_actions = parse_instruction(instruction)

    return {"actions": parsed_actions}


builder = StateGraph(dict)

builder.add_node("parser", parser_node)

builder.set_entry_point("parser")

builder.set_finish_point("parser")

graph = builder.compile()