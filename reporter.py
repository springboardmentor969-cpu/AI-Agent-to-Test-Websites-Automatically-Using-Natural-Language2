from datetime import datetime

def generate_report(instruction, code, execution_result):
    status = execution_result.get("status", "unknown")
    error  = execution_result.get("error", "")
    output = execution_result.get("output", "")

    report = {
        "timestamp"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instruction": instruction,
        "status"     : status,
        "code"       : code,
        "output"     : output,
        "error"      : error,
    }
    return report