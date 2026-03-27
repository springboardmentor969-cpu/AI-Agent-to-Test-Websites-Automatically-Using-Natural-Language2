from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from parser import parse_instruction
from generator import generate_code
from validator import validate_output


class AgentState(TypedDict):
    user_input: str
    parsed: list
    generated_code: str


def parser_node(state: AgentState):

    parsed = parse_instruction(state["user_input"])

    return {
        "parsed": parsed
    }


def generator_node(state: AgentState):

    code = generate_code(state["parsed"])

    return {
        "generated_code": code
    }


def validator_node(state: AgentState):

    validate_output(state)

    return state


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("parser", parser_node)
    builder.add_node("generator", generator_node)
    builder.add_node("validator", validator_node)

    builder.add_edge(START, "parser")
    builder.add_edge("parser", "generator")
    builder.add_edge("generator", "validator")
    builder.add_edge("validator", END)

    return builder.compile()


def run_agent(user_input: str):

    graph = build_graph()

    result = graph.invoke({
        "user_input": user_input
    })

    return result