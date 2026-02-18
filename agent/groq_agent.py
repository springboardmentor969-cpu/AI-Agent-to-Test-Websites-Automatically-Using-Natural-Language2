from agent.parser import parse_instruction
from dataclasses import dataclass
from agent.client import get_client

# Initialize client used by this module
client = get_client()


@dataclass
class State:
    input: str
    output: str = ""


def agent_node(state: State):
    user_input = state.input

    try:
        parsed_actions = parse_instruction(user_input)

        try:
            client_instance = client
        except NameError:
            return State(
                input=user_input,
                output="Error: 'client' is not configured. Set up an API client and assign it to the name 'client'."
            )

        response = client_instance.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are an AI testing agent.

User Instruction:
{user_input}

Parsed Actions:
{parsed_actions}

Generate a Playwright Python script that performs these actions.
Return ONLY valid Python code. No explanations.
"""
                }
            ]
        )

        return State(
            input=user_input,
            output=response.choices[0].message.content
        )

    except Exception as e:
        return State(
            input=user_input,
            output=f"Error: {str(e)}"
        )


# Lightweight adapter expected by `app.py`:
class AgentApp:
    def invoke(self, state: State):
        result = agent_node(state)
        if isinstance(result, State):
            return {"input": result.input, "output": result.output}
        if isinstance(result, dict):
            return result
        return {"input": getattr(state, "input", None), "output": str(result)}


# Module-level `app` for `from agent.groq_agent import app` usage
app = AgentApp()

__all__ = ["State", "agent_node", "AgentApp", "app"]
