from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from typing import TypedDict
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel("gemini-2.5-flash")

class AgentState(TypedDict):
    input: str
    output: str

def agent_node(state: AgentState):
    user_input = state["input"]f

    # Call Gemini model
    response = llm.generate_content(user_input)

    return {"output": response.text}

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)

graph = builder.compile()

