from datetime import datetime

def generate_report(step_results):
    total_steps = len(step_results)
    passed = sum(1 for step in step_results if step["status"] == "success")
    failed = sum(1 for step in step_results if step["status"] == "failed")

    report = {
        "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_steps": total_steps,
        "passed": passed,
        "failed": failed,
        "details": step_results
    }

    return report