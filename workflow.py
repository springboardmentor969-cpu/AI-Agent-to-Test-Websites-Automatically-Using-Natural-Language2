from langgraph.graph import StateGraph
from typing import TypedDict
from instruction_parser import InstructionParser
from playwright_generator import PlaywrightGenerator
from assertion_generator import AssertionGenerator

class WorkflowState(TypedDict):
    input_text: str
    parsed_command: dict
    url: str
    playwright_code: str
    assertion_code: str


parser = InstructionParser()
generator = PlaywrightGenerator()
assertion_gen = AssertionGenerator()


def parse_node(state):
    cmd, url = parser.parse(state["input_text"])
    return {"parsed_command": cmd, "url": url}


def generate_node(state):
    code = generator.generate(state["parsed_command"], state["url"])
    return {"playwright_code": code}


def assertion_node(state):
    assertion = assertion_gen.generate_assertion(state["parsed_command"])
    return {"assertion_code": assertion}


graph = StateGraph(WorkflowState)

graph.add_node("parser", parse_node)
graph.add_node("generator", generate_node)
graph.add_node("assertion", assertion_node)

graph.set_entry_point("parser")

graph.add_edge("parser", "generator")
graph.add_edge("generator", "assertion")

workflow = graph.compile()