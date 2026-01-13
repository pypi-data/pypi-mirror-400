"""Test refactored MayaClient with new _send_receive signature."""

import asyncio
import logging
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from maya_mcp_server.client import MayaClient
from maya_mcp_server.types import ResultType


# Enable logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


async def test_refactored_client():
    """Test the refactored client."""
    print("=" * 70)
    print("Testing Refactored MayaClient")
    print("=" * 70)

    client = MayaClient(host="127.0.0.1", port=7001, timeout=10.0)

    try:
        print("\n1. Connecting to Maya...")
        await client.connect()
        print("   ✓ Connected")

        print("\n2. Testing ping...")
        is_alive = await client.ping()
        print(f"   ✓ Ping: {is_alive}")

        print("\n3. Bootstrapping...")
        new_client = await client.bootstrap()
        print(f"   ✓ Bootstrap returned: {new_client.key}")

        print("\n4. Disconnecting from config port...")
        await client.disconnect()
        print("   ✓ Disconnected from config port")

        print("\n5. Testing new client session_info...")
        info = await new_client.session_info()
        print(f"   ✓ Maya version: {info.maya_version}")
        print(f"   ✓ PID: {info.pid}")

        print("\n6. Testing execute_code with NONE result_type...")
        result = await new_client.execute_code(
            "import maya.cmds as cmds", result_type=ResultType.NONE
        )
        print(f"   ✓ Result: {result.result}")
        print(f"   ✓ Error: {result.error}")

        print("\n7. Testing execute_code with RAW result_type...")
        result = await new_client.execute_code("21 * 2", result_type=ResultType.RAW)
        print(f"   ✓ Result: {result.result}")

        print("\n8. Testing execute_code with JSON result_type...")
        result = await new_client.execute_code("cmds.ls(cameras=True)", result_type=ResultType.JSON)
        print(f"   ✓ Result: {result.result}")

        print("\n9. Cleaning up...")
        await new_client.disconnect()
        print("   ✓ Done")

        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

    return True


if __name__ == "__main__":
    result = asyncio.run(test_refactored_client())
    sys.exit(0 if result else 1)
