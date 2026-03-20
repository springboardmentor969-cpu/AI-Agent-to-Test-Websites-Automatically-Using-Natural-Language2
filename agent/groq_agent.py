from dataclasses import dataclass

from agent.workflow import run_workflow


@dataclass
class State:
    input: str
    output: str = ""


def agent_node(state: State):
    try:
        result = run_workflow(state.input, execute=False)
        return State(
            input=state.input,
            output=result["generated_code"],
        )
    except Exception as exc:
        return State(
            input=state.input,
            output=f"Error: {exc}",
        )


class AgentApp:
    def invoke(self, state: State):
        result = agent_node(state)
        return {"input": result.input, "output": result.output}


app = AgentApp()

__all__ = ["State", "agent_node", "AgentApp", "app"]
