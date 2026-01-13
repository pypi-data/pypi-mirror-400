"""Debug module function return values."""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from maya_mcp_server.client import MayaClient
from maya_mcp_server.types import ResultType


async def test_module_returns():
    """Test that module functions return values correctly."""
    print("Testing module function returns...")

    client = MayaClient(host="127.0.0.1", port=7001, timeout=10.0)

    try:
        await client.connect()
        new_client = await client.bootstrap()
        await client.disconnect()

        # Write test module
        test_code = """
def hello(name="World"):
    return f"Hello, {name}!"

def add(a, b):
    return a + b
"""
        await new_client.write_module("test_module", test_code, overwrite=True)

        # Test 1: Call with statement (should be None)
        print("\nTest 1: Statement execution (no return expected)")
        result = await new_client.execute_code(
            "import test_module; test_module.hello('Maya')", result_type=ResultType.NONE
        )
        print(f"  Result: {result.result}")
        print(f"  Error: {result.error}")

        # Test 2: Expression evaluation (should return value)
        print("\nTest 2: Expression evaluation (RAW)")
        result = await new_client.execute_code(
            "test_module.hello('Maya')", result_type=ResultType.RAW
        )
        print(f"  Result: {result.result}")
        print(f"  Error: {result.error}")

        # Test 3: Expression evaluation (JSON)
        print("\nTest 3: Expression evaluation (JSON)")
        result = await new_client.execute_code(
            "test_module.add(10, 32)", result_type=ResultType.RAW
        )
        print(f"  Result: {result.result}")
        print(f"  Error: {result.error}")

        await new_client.disconnect()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_module_returns())
