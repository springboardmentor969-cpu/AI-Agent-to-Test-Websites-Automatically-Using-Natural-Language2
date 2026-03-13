# workflow.py
from langgraph.graph import StateGraph
from typing import TypedDict
from parser import InstructionParser
from code_generator import CodeGenerator
from schemas import TestCommand

class WorkflowState(TypedDict):
    input_text: str
    parsed_command: TestCommand
    generated_code: str


parser = InstructionParser()
generator = CodeGenerator()


def parse_node(state: WorkflowState):
    command = parser.parse(state["input_text"])
    return {"parsed_command": command}


def generate_node(state: WorkflowState):
    code = generator.generate(state["parsed_command"])
    return {"generated_code": code}


graph = StateGraph(WorkflowState)
graph.add_node("parser", parse_node)
graph.add_node("generator", generate_node)

graph.set_entry_point("parser")
graph.add_edge("parser", "generator")

workflow = graph.compile()