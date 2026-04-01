from agent.planner import plan_actions
from agent.code_generator import generate_code
from agent.execution_module import execute_test_case


def create_workflow():

    def run_agent(user_input):

        state = {}

        state["instruction"] = user_input

        actions = plan_actions(user_input)

        if not isinstance(actions, list):
            actions = []

        clean_actions = []
        for a in actions:
            if isinstance(a, dict):
                clean_actions.append(a)

        state["parsed_actions"] = clean_actions

        code = generate_code(clean_actions)
        state["generated_code"] = code

        result = execute_test_case(state)

        state["execution_status"] = result["status"]
        state["report"] = result

        return state

    return run_agent
