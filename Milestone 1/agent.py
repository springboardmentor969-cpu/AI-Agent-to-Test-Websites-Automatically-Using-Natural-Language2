from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from instruct_parser import InstructionParser

# Initialize parser
parser = InstructionParser()

# Agent State - Enhanced for Milestone 2
class AgentState(TypedDict):
    input: str                          # User's natural language instruction
    parsed_actions: List[Dict]          # Parsed structured actions
    playwright_commands: List[Dict]     # Mapped Playwright commands
    generated_code: str                 # Final generated code
    output: str                         # Final output to return


# Node 1: Parse User Instruction
def parse_instruction_node(state: AgentState):
    """
    Convert natural language instruction to structured actions
    This is the Instruction Parser Module
    """
    user_input = state["input"]
    
    print(f"📝 Parsing instruction: {user_input}")
    
    # Parse the test case into structured actions
    parsed_actions = parser.parse_test_case(user_input)
    
    print(f"✅ Parsed {len(parsed_actions)} actions")
    
    return {
        "parsed_actions": parsed_actions
    }


# Node 2: Map Actions to Playwright Commands
def map_to_playwright_node(state: AgentState):
    """
    Map parsed actions to Playwright-specific commands
    """
    parsed_actions = state.get("parsed_actions", [])
    
    print(f"🔧 Mapping {len(parsed_actions)} actions to Playwright commands")
    
    # Map to Playwright commands
    playwright_commands = parser.map_to_playwright_actions(parsed_actions)
    
    print(f"✅ Generated {len(playwright_commands)} Playwright commands")
    
    return {
        "playwright_commands": playwright_commands
    }


# Node 3: Generate Executable Code
def generate_code_node(state: AgentState):
    """
    Generate final executable Playwright Python code
    """
    playwright_commands = state.get("playwright_commands", [])
    
    print(f"🎯 Generating executable code from {len(playwright_commands)} commands")
    
    
    code_lines = []
    
    for cmd in playwright_commands:
        pw_command = cmd.get("playwright_command")
        if pw_command:
            # Add comment for clarity
            original_desc = cmd.get("original_action", {}).get("description", "")
            if original_desc:
                code_lines.append(f"# {original_desc}")
            code_lines.append(pw_command)
            code_lines.append("")  # Add blank line for readability
    
    generated_code = "\n".join(code_lines)
    
    print(f"✅ Generated {len(code_lines)} lines of code")
    
    return {
        "generated_code": generated_code,
        "output": generated_code
    }


# Node 4: Validate Generated Code (Optional but recommended)
def validate_code_node(state: AgentState):
    """
    Basic validation of generated code
    """
    generated_code = state.get("generated_code", "")
    
    print(f"🔍 Validating generated code")
    
    # Basic validation checks
    issues = []
    
    if not generated_code or generated_code.strip() == "":
        issues.append("Generated code is empty")
    
    if "page." not in generated_code:
        issues.append("No Playwright page commands found")
    
    # Check for common syntax issues
    if generated_code.count('(') != generated_code.count(')'):
        issues.append("Mismatched parentheses")
    
    if generated_code.count('"') % 2 != 0:
        issues.append("Mismatched quotes")
    
    if issues:
        print(f"⚠️ Validation issues found: {', '.join(issues)}")
    else:
        print(f"✅ Code validation passed")
    
    return {}


# LangGraph Workflow Setup - Milestone 2 Complete
builder = StateGraph(AgentState)

# Add nodes in workflow order
builder.add_node("parse_instruction", parse_instruction_node)
builder.add_node("map_to_playwright", map_to_playwright_node)
builder.add_node("generate_code", generate_code_node)
builder.add_node("validate_code", validate_code_node)

# Define the workflow
builder.set_entry_point("parse_instruction")
builder.add_edge("parse_instruction", "map_to_playwright")
builder.add_edge("map_to_playwright", "generate_code")
builder.add_edge("generate_code", "validate_code")
builder.add_edge("validate_code", END)

# Compile the graph
graph = builder.compile()


# Standalone Test
if __name__ == "__main__":
    print("=== Testing Milestone 2 Workflow ===\n")
    
    # Test case 1: Simple navigation and interaction
    test_input = """
    Go to https://demo.playwright.dev/todomvc
    Click on the input field with class 'new-todo'
    Type 'Learn LangGraph' in the todo input
    Press Enter
    Verify the text 'Learn LangGraph' appears on the page
    """
    
    print(f"Test Input:\n{test_input}\n")
    print("=" * 50)
    
    result = graph.invoke({"input": test_input})
    
    print("\n" + "=" * 50)
    print("\n🎉 GENERATED CODE:\n")
    print(result["output"])
    
    print("\n" + "=" * 50)
    print("\n📊 DETAILED STATE:")
    print(f"\nParsed Actions: {len(result.get('parsed_actions', []))}")
    for i, action in enumerate(result.get('parsed_actions', []), 1):
        print(f"  {i}. {action.get('action_type')}: {action.get('description')}")
    
    print(f"\nPlaywright Commands: {len(result.get('playwright_commands', []))}")
    for i, cmd in enumerate(result.get('playwright_commands', []), 1):
        print(f"  {i}. {cmd.get('playwright_command')}")




