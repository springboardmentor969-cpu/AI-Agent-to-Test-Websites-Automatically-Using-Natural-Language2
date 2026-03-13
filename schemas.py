from pydantic import BaseModel
from typing import Optional

class TestCommand(BaseModel):
    action: str
    target: str
    value: Optional[str] = None
    expected_result: Optional[str] = None