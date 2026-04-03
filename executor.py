import subprocess

def run_test(code):
    try:
        with open("test_script.py", "w") as f:
            f.write(code)

        # run in background
        subprocess.Popen(["python", "test_script.py"])

        return {
            "status": "Started"
        }

    except Exception as e:
        return {
            "status": "Failed",
            "error": str(e)
        }