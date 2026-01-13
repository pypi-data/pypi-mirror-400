"""Test the MCP server with a live Maya session."""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from maya_mcp_server import server


async def test_mcp_server():
    """Test the MCP server tools with a live Maya session."""
    print("=" * 70)
    print("Testing MCP Server with Live Maya Session")
    print("=" * 70)

    # Initialize session manager
    print("\n1. Initializing session manager...")
    manager = await server.initialize_session_manager(scan_interval=100.0)
    print("   ✓ Session manager initialized")

    try:
        # List sessions
        print("\n2. Listing sessions...")
        sessions = await server.list_sessions.fn()
        print(f"   ✓ Found {len(sessions)} session(s)")
        for session in sessions:
            print(f"     - {session.host}:{session.port} (PID: {session.pid})")

        if not sessions:
            print("\n✗ No Maya sessions found!")
            print("   Make sure Maya is running with a command port open.")
            print("   In Maya's Script Editor (Python), run:")
            print("   import maya.cmds as cmds")
            print("   cmds.commandPort(name=':7001', sourceType='python')")
            return False

        # Use the first session
        session = sessions[0]
        host = session.host
        port = session.port

        print(f"\n3. Using session {host}:{port}...")
        info = await server.use_session.fn(host, port)
        print("   ✓ Session activated")
        print(f"     - Maya version: {info.maya_version}")
        print(f"     - PID: {info.pid}")
        print(f"     - Scene: {info.scene_name or 'untitled'}")

        # Get session info
        print("\n4. Getting session info...")
        info = await server.get_session_info.fn()
        print("   ✓ Session info retrieved")
        print(f"     - User: {info.user}")
        print(f"     - Scene path: {info.scene_path or 'N/A'}")

        # Execute code with NONE result type
        print("\n5. Testing execute_code (NONE result_type)...")
        result = await server.execute_code.fn("import maya.cmds as cmds", result_type="NONE")
        print("   ✓ Code executed")
        print(f"     - Result: {result}")

        # Execute code with RAW result type
        print("\n6. Testing execute_code (RAW result_type)...")
        result = await server.execute_code.fn("21 * 2", result_type="RAW")
        print(f"   ✓ Result: {result}")

        # Execute code with JSON result type
        print("\n7. Testing execute_code (JSON result_type)...")
        result = await server.execute_code.fn("cmds.ls(cameras=True)", result_type="JSON")
        print(f"   ✓ Result: {result}")

        # Test write_module
        print("\n8. Testing write_module...")
        test_code = """
def hello(name="World"):
    return f"Hello, {name}!"

def add(a, b):
    return a + b
"""
        module_result = await server.write_module.fn(
            name="test_module", code=test_code, overwrite=True
        )
        print(f"   ✓ Module created: {module_result}")

        # Use the module (first ensure it's imported)
        print("\n9. Testing module usage...")
        await server.execute_code.fn("import test_module", result_type="NONE")

        result = await server.execute_code.fn("test_module.hello('Maya')", result_type="RAW")
        print(f"   ✓ Module function result: {result}")

        result = await server.execute_code.fn("test_module.add(10, 32)", result_type="RAW")
        print(f"   ✓ Module add function result: {result}")

        # Test get_output
        print("\n10. Testing get_output...")
        await server.execute_code.fn("print('Testing stdout capture')", result_type="NONE")
        output = await server.get_output.fn(clear=True)
        print("   ✓ Output captured:")
        if output.stdout:
            print(f"     - stdout: {output.stdout!r}")
        if output.stderr:
            print(f"     - stderr: {output.stderr!r}")

        # Test unuse_session
        print("\n11. Testing unuse_session...")
        result = await server.unuse_session.fn()
        print(f"   ✓ {result}")

        # Verify no active session
        print("\n12. Verifying no active session after unuse...")
        assert manager.active_session is None
        print("   ✓ No active session")

        print("\n" + "=" * 70)
        print("✓ All MCP server tests passed!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print("\nCleaning up...")
        await server.shutdown_session_manager()
        print("   ✓ Session manager shutdown")


if __name__ == "__main__":
    result = asyncio.run(test_mcp_server())
    sys.exit(0 if result else 1)
