"""
Reporting Module
-----------------
Constructs structured JSON reports from test execution data.

Output format:
{
    "test_name": "...",
    "steps": [
        {"action": "...", "status": "pass/fail", "details": "...", "execution_time": 0.5}
    ],
    "summary": {
        "total": 5,
        "passed": 4,
        "failed": 1,
        "execution_time": "12.5s"
    }
}
"""

class TestReport:
    def __init__(self, test_name: str = "Automated Browser Test"):
        self.test_name = test_name
        self.steps = []
        self._start_time = None
        self._total_time = 0.0
    
    def add_step(self, action: dict, status: str, details: str = "", execution_time: float = 0.0):
        """
        Add a completed or failed step to the report.
        """
        # Convert the action dict to a readable string format
        action_type = action.get("type", "unknown").upper()
        target = action.get("selector") or action.get("url") or action.get("key") or ""
        value = action.get("value") or ""
        
        action_desc = f"{action_type}"
        if target:
            action_desc += f" {target}"
        if value:
            action_desc += f" with value '{value}'"
            
        # Optional wait duration
        if action_type == "WAIT" and action.get("duration"):
            action_desc += f" {action['duration']}ms"
            
        self.steps.append({
            "action": action_desc,
            "raw_action": action,
            "status": status.lower(),
            "details": details,
            "execution_time": round(execution_time, 2)
        })
        self._total_time += execution_time
        
    def to_dict(self) -> dict:
        """
        Generate the final structured JSON payload.
        """
        total = len(self.steps)
        passed = sum(1 for s in self.steps if s["status"] == "pass")
        failed = sum(1 for s in self.steps if s["status"] == "fail")
        
        # Round the total time nicely
        time_str = f"{round(self._total_time, 2)}s"
        
        return {
            "test_name": self.test_name,
            "steps": self.steps,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "execution_time": time_str
            }
        }
