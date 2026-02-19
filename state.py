from typing import TypedDict, List

class AgentState(TypedDict):
    instruction: str
    parsed_steps: List[str]
