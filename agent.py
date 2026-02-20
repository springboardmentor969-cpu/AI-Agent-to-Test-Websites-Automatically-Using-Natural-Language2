import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

client = Groq(api_key=api_key)


def agent_node(state):
    instruction = state.get("instruction", "")

    if not instruction:
        return {"response": "No instruction provided."}

    prompt = f"""
You are an AI Website Testing Agent.
Convert the following instruction into clear step-by-step test actions.

Instruction:
{instruction}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ UPDATED MODEL
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {"response": f"Error occurred: {str(e)}"}


workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.set_finish_point("agent")

app_graph = workflow.compile()


def process_instruction(instruction):
    result = app_graph.invoke({"instruction": instruction})
    return result.get("response", "No response generated.")