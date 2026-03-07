from langgraph.graph import StateGraph
from parser.instruction_parser import parse_instruction
from generator.code_generator import generate_playwright_code


class AgentState(dict):
    pass


def parser_node(state):

    instruction = state["input"]

    parsed = parse_instruction(instruction)

    state["parsed"] = parsed

    return state


def generator_node(state):

    command = state["parsed"]

    code = generate_playwright_code(command)

    state["generated_code"] = code

    return state


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("parser", parser_node)
    graph.add_node("generator", generator_node)

    graph.set_entry_point("parser")

    graph.add_edge("parser","generator")

    graph.set_finish_point("generator")

    return graph.compile()