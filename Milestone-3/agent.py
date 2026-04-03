from parser import parse_instruction
from generator import generate_code
import subprocess
import tempfile
import sys

def run_agent(instruction):
    parsed = parse_instruction(instruction)
    code = generate_code(parsed)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        temp_file = f.name

    subprocess.run([sys.executable, temp_file])

    return {
        "parsed": parsed,
        "code": code
    }