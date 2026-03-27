def run_test(code):
    try:
        with open("test_script.py", "w") as f:
            f.write(code)

        import subprocess
        result = subprocess.run(
            ["python", "test_script.py"],
            capture_output=True,
            text=True
        )

        return result.stdout, result.stderr

    except Exception as e:
        return "", str(e)