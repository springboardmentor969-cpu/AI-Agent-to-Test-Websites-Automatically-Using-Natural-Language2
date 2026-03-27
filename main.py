from parser import parse_instruction
from code_generator import generate_code
from executor import run_test

if __name__ == "__main__":

    instruction = input("Enter instruction: ")

    actions = parse_instruction(instruction)

    code = generate_code(actions)

    print("\nGenerated Code:\n")
    print(code)

    print("\nRunning...\n")

    result, error = run_test(code)

    print("Result:", result)
    print("Error:", error)