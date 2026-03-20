from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ParsedAction:
    action: str
    target: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedInstruction:
    raw_input: str
    target_name: str
    target_url: str
    target_type: str
    username: str | None = None
    password: str | None = None
    expected_result: str | None = None
    headless: bool = True
    actions: list[ParsedAction] = field(default_factory=list)

    def actions_as_dicts(self) -> list[dict[str, Any]]:
        return [action.to_dict() for action in self.actions]


@dataclass
class ExecutionResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0

    @property
    def summary(self) -> str:
        if self.stdout.strip():
            return self.stdout.strip()
        if self.stderr.strip():
            return self.stderr.strip()
        return "Completed" if self.success else "No output"
