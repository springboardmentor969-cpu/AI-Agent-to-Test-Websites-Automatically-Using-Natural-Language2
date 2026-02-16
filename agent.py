from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_openai import ChatOpenAI

# Create model
llm = ChatOpenAI(model="gpt-4o-mini")

class AgentState(TypedDict):
    input: str
    output: str

def agent_node(state: AgentState):
    user_input = state["input"]

    # Call OpenAI model
    response = llm.invoke(user_input)

    return {"output": response.content}

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)

graph = builder.compile()

