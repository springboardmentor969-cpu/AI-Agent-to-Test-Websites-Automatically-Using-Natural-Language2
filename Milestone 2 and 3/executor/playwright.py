def run_test(code):

    print("\nGenerated Playwright Script:")
    print(code)

    print("\nRunning Test...\n")

    exec(code)

    print("\nTest Finished")