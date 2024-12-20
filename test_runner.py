# -*- coding: utf-8 -*-
import os
import subprocess

TESTS_DIR = "tests"
TEST_CASES = [
    {"input": "test_input1.xml", "expected": "test_output1.txt"},
    {"input": "test_input2.xml", "expected": "test_output2.txt"},
]
TRANSFORMER_SCRIPT = os.path.abspath("transformer.py")

def run_test(test_case):
    input_file = os.path.join(TESTS_DIR, test_case["input"])
    expected_file = os.path.join(TESTS_DIR, test_case["expected"])
    output_file = "test_output.txt"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return False

    if not os.path.exists(expected_file):
        print(f"Error: Expected file '{expected_file}' does not exist.")
        return False

    try:
        subprocess.run(
            ["python", TRANSFORMER_SCRIPT, input_file, output_file],
            check=True,
            cwd=os.path.dirname(TRANSFORMER_SCRIPT)
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Transformer script failed with error: {e}")
        return False

    with open(output_file, "r", encoding="utf-8", errors="ignore") as output:
        result = output.read().strip()

    with open(expected_file, "r", encoding="utf-8", errors="ignore") as expected:
        expected_result = expected.read().strip()

    if result == expected_result:
        print(f"Test '{test_case['input']}' passed.")
        print("Expected:")
        print(expected_result)
        print("Got:")
        print(result)
        return True
    else:
        print(f"Test '{test_case['input']}' failed.")
        print("Expected:")
        print(expected_result)
        print("Got:")
        print(result)
        return False

def main():
    print("Running tests...\n")
    passed = 0

    for test_case in TEST_CASES:
        if run_test(test_case):
            passed += 1

    total = len(TEST_CASES)
    print(f"\nTests passed: {passed}/{total}")
    if passed == total:
        print("All tests passed successfully!")
    else:
        print("Some tests failed.")

if __name__ == "__main__":
    main()