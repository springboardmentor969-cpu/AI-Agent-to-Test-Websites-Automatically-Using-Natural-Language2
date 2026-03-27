from langgraph.graph import StateGraph
from parser import parse_instruction
from code_generator import generate_code
from executor import run_test


def parser_node(state):
    actions = parse_instruction(state["instruction"])
    return {"actions": actions}


def generator_node(state):
    code = generate_code(state["actions"])
    return {"code": code}


def executor_node(state):
    result, error = run_test(state["code"])
    return {"result": result, "error": error}


builder = StateGraph(dict)

builder.add_node("parser", parser_node)
builder.add_node("generator", generator_node)
builder.add_node("executor", executor_node)

builder.set_entry_point("parser")

builder.add_edge("parser", "generator")
builder.add_edge("generator", "executor")

builder.set_finish_point("executor")

graph = builder.compile()