"""Test script for session discovery notifications.

This script demonstrates how the MCP server notifies clients when new Maya sessions
are discovered or when existing sessions disconnect.

Prerequisites:
- Maya running with command port on :7001
- Run: uv run python test_session_notifications.py
"""

import asyncio
import logging

from maya_mcp_server.session_manager import SessionManager
from maya_mcp_server.types import ClientType

# Setup logging to see notifications
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_notifications():
    """Test session discovery notifications."""

    print("=" * 70)
    print("Session Discovery Notification Test")
    print("=" * 70)

    # Initialize session manager with short scan interval for testing
    print("\n1. Initializing session manager (scan interval: 5s)...")
    manager = SessionManager(scan_interval=5.0, client_type=ClientType.QT)
    await manager.start()

    print(f"   Sessions found: {manager.session_count}")

    # Check initial sessions
    print("\n2. Listing initial sessions...")
    sessions = await manager.list_sessions()
    for session in sessions:
        print(f"   - {session.host}:{session.port} - Maya {session.maya_version}")

    # Check for any pending notifications from initial scan
    print("\n3. Checking for initial notifications...")
    notifications = await manager.get_pending_notifications()
    if notifications["new_sessions"]:
        print("   New sessions detected during initial scan:")
        for session in notifications["new_sessions"]:
            print(f"   🆕 {session.host}:{session.port} - Maya {session.maya_version}")
    else:
        print("   No pending notifications")

    # Wait for background scan
    print("\n4. Waiting for background scan cycle (5 seconds)...")
    print("   TIP: Start a new Maya instance with command port during this time")
    print("        to see a new session notification!")
    await asyncio.sleep(6)

    # Check for notifications after scan
    print("\n5. Checking for notifications after scan...")
    notifications = await manager.get_pending_notifications()

    if notifications["new_sessions"]:
        print("   🎉 New sessions discovered:")
        for session in notifications["new_sessions"]:
            print(f"   🆕 {session.host}:{session.port} - Maya {session.maya_version}")
    else:
        print("   No new sessions found")

    if notifications["removed_sessions"]:
        print("   Sessions removed:")
        for session_key in notifications["removed_sessions"]:
            print(f"   🔴 {session_key}")
    else:
        print("   No sessions removed")

    # List all current sessions
    print("\n6. Current active sessions:")
    sessions = await manager.list_sessions()
    if sessions:
        for session in sessions:
            print(f"   - {session.host}:{session.port} - Maya {session.maya_version}")
    else:
        print("   No active sessions")

    # Test manual session addition
    print("\n7. Testing manual session addition notification...")
    print("   (This would trigger a notification if a new session was added)")

    # Cleanup
    print("\n8. Shutting down session manager...")
    await manager.stop()

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
    print("\nNotification Flow:")
    print("1. SessionManager scans for new Maya ports")
    print("2. New sessions are queued in _new_sessions")
    print("3. MCP clients call list_sessions() tool")
    print("4. Server checks pending notifications and logs them via Context.info()")
    print("5. MCP clients see these log messages in real-time")


async def test_with_simulated_context():
    """Test notifications with simulated MCP Context."""

    print("\n" + "=" * 70)
    print("Testing with Simulated MCP Context")
    print("=" * 70)

    # Mock Context for testing
    class MockContext:
        def info(self, message: str, logger_name: str = None):
            print(f"   [MCP LOG] {message}")

    manager = SessionManager(scan_interval=30.0, client_type=ClientType.QT)
    await manager.start()

    # Simulate what happens when list_sessions tool is called
    print("\n1. Simulating list_sessions() tool call...")

    ctx = MockContext()
    notifications = await manager.get_pending_notifications()

    # This is what happens in server.py list_sessions tool
    for session in notifications["new_sessions"]:
        ctx.info(
            f"🆕 New Maya session discovered: {session.host}:{session.port} "
            f"(Maya {session.maya_version}, Scene: {session.scene_name})"
        )

    for session_key in notifications["removed_sessions"]:
        ctx.info(f"🔴 Maya session disconnected: {session_key}")

    sessions = await manager.list_sessions()
    print(f"\n2. Total sessions: {len(sessions)}")

    await manager.stop()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Maya MCP Server - Session Notification Testing")
    print("=" * 70)

    try:
        # Run basic test
        asyncio.run(test_notifications())

        # Run simulated context test
        asyncio.run(test_with_simulated_context())

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
