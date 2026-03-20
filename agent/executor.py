import subprocess
import sys
from pathlib import Path

from agent.models import ExecutionResult


def write_generated_test(code: str, output_path: str = "generated_test.py") -> Path:
    path = Path(output_path)
    path.write_text(code, encoding="utf-8")
    return path


def run_generated_test(output_path: str = "generated_test.py", python_executable: str | None = None) -> ExecutionResult:
    completed = subprocess.run(
        [python_executable or sys.executable, output_path],
        capture_output=True,
        text=True,
    )
    return ExecutionResult(
        success=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )
