"""Test MayaQtClient with live Maya session."""

import asyncio
import logging
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from maya_mcp_server.client import MayaClient, MayaQtClient
from maya_mcp_server.types import ResultType


# Enable logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


async def test_qt_client():
    """Test the Qt client with a live Maya session."""
    print("=" * 70)
    print("Testing MayaQtClient with Live Maya Session")
    print("=" * 70)

    # First connect via commandPort and bootstrap
    config_client = MayaClient(host="127.0.0.1", port=7001, timeout=10.0)

    try:
        print("\n1. Connecting to Maya commandPort...")
        await config_client.connect()
        print("   ✓ Connected to commandPort")

        print("\n2. Bootstrapping with Qt client...")
        qt_client = await config_client.bootstrap(client_type="qt")
        print(f"   ✓ Bootstrap returned: {qt_client.key}")
        print(f"   ✓ Client type: {type(qt_client).__name__}")

        # Verify it's a MayaQtClient
        assert isinstance(qt_client, MayaQtClient), f"Expected MayaQtClient, got {type(qt_client)}"

        print("\n3. Disconnecting from commandPort...")
        await config_client.disconnect()
        print("   ✓ Disconnected from commandPort")

        print("\n4. Testing ping on Qt client...")
        is_alive = await qt_client.ping()
        print(f"   ✓ Ping: {is_alive}")
        assert is_alive, "Ping failed!"

        print("\n5. Testing session_info...")
        info = await qt_client.session_info()
        print(f"   ✓ Maya version: {info.maya_version}")
        print(f"   ✓ PID: {info.pid}")
        print(f"   ✓ User: {info.user}")

        print("\n6. Testing execute_code with NONE result_type...")
        result = await qt_client.execute_code(
            "import maya.cmds as cmds", result_type=ResultType.NONE
        )
        print(f"   ✓ Result: {result.result}")
        print(f"   ✓ Error: {result.error}")

        print("\n7. Testing execute_code with RAW result_type...")
        result = await qt_client.execute_code("21 * 2", result_type=ResultType.RAW)
        print(f"   ✓ Result: {result.result}")
        assert result.result == 42, f"Expected 42, got {result.result}"

        print("\n8. Testing execute_code with JSON result_type...")
        result = await qt_client.execute_code("cmds.ls(cameras=True)", result_type=ResultType.JSON)
        print(f"   ✓ Result: {result.result}")
        assert isinstance(result.result, list), f"Expected list, got {type(result.result)}"

        print("\n9. Testing write_module...")
        module_result = await qt_client.write_module(
            name="qt_test_module",
            code='def greet(name):\n    return f"Hello from Qt, {name}!"',
            overwrite=True,
        )
        print(f"   ✓ Module created: {module_result}")

        print("\n10. Testing module usage...")
        result = await qt_client.execute_code(
            "import qt_test_module; qt_test_module.greet('Maya')",
            result_type=ResultType.RAW,
        )
        print(f"   ✓ Module function result: {result.result}")

        print("\n11. Testing stream capture...")
        await qt_client.install_stream_capture()
        await qt_client.execute_code("print('Hello from Qt!')", result_type=ResultType.NONE)
        output = await qt_client.get_buffered_output()
        print(f"   ✓ Captured stdout: {output.stdout!r}")
        await qt_client.uninstall_stream_capture()

        print("\n12. Cleaning up...")
        await qt_client.disconnect()
        print("   ✓ Disconnected from Qt server")

        print("\n" + "=" * 70)
        print("✓ All MayaQtClient tests passed!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        try:
            await config_client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    result = asyncio.run(test_qt_client())
    sys.exit(0 if result else 1)
