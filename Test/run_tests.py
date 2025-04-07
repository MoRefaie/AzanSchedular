import asyncio
import sys
from test_scan_for_devices import test_scan_for_devices
from api import simulate_scan_devices_call

# Dictionary mapping test names to their corresponding functions
TESTS = {
    "scan_for_devices": test_scan_for_devices,
    "simulate_api_call": simulate_scan_devices_call,
}

def list_tests():
    """
    Lists all available tests.
    """
    print("Available tests:")
    for test_name in TESTS.keys():
        print(f"- {test_name}")

async def run_test(test_name):
    """
    Runs the specified test by name.
    """
    if test_name not in TESTS:
        print(f"Error: Test '{test_name}' not found.")
        list_tests()
        return

    print(f"Running test: {test_name}")
    test_function = TESTS[test_name]
    if asyncio.iscoroutinefunction(test_function):
        await test_function()
    else:
        test_function()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <test_name>")
        list_tests()
        sys.exit(1)

    test_name = sys.argv[1]
    asyncio.run(run_test(test_name))