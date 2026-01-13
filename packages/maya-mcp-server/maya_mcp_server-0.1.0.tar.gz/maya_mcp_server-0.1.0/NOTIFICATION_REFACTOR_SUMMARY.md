# Notification System Refactor - Summary

## What Changed

Based on your feedback, I've removed the redundant notification system from the `list_sessions` tool and documented MCP's limitations around push notifications.

## The Problem You Identified

You correctly pointed out that having notifications in `list_sessions` was redundant because:
- Agents can infer new/removed sessions by comparing `list_sessions` results
- The notification approach doesn't provide any additional information
- It adds unnecessary complexity to the tool

## The Underlying Issue

After investigating, I found that **MCP fundamentally doesn't support push notifications from background tasks**:

- **Context is request-scoped** - All FastMCP notification methods require a `Context`, which only exists during request handling
- **No client registry** - Background tasks have no way to access connected clients
- **Pull-based design** - MCP is designed for clients to poll tools, not for servers to push updates

## Changes Made

### 1. Simplified `list_sessions` Tool (src/maya_mcp_server/server.py)

**Before:**
```python
@mcp.tool
async def list_sessions(ctx: Context) -> list[SessionInfo]:
    # Check for pending notifications
    notifications = await manager.get_pending_notifications()

    # Log new session discoveries to client
    for session in notifications["new_sessions"]:
        ctx.info(f"🆕 New Maya session discovered...")

    return await manager.list_sessions()
```

**After:**
```python
@mcp.tool
async def list_sessions() -> list[SessionInfo]:
    """
    Note: To detect new or removed sessions, clients should call this tool
    periodically (e.g., every 10-30 seconds) and compare results.
    """
    manager = get_session_manager()
    return await manager.list_sessions()
```

### 2. Enhanced Server-Side Logging (src/maya_mcp_server/session_manager.py)

Added rich logging for server operators:

```python
logger.info(
    f"🆕 Discovered Maya session at {client.key} "
    f"(PID {pid}, Maya {maya_version}, Scene: {scene_name})"
)

logger.info(f"🔴 Removed dead session: {session_key}")
```

These logs appear in the server's stdout/stderr, not to MCP clients.

### 3. Kept Notification Infrastructure

The notification queues (`_new_sessions`, `_removed_sessions`) and `get_pending_notifications()` method are **still present** for:
- Potential future custom extensions (webhooks, etc.)
- Debugging purposes
- Internal tracking

They're just not exposed to MCP clients anymore.

## Recommended Client Pattern

Clients (like AI agents) should poll periodically and compare results:

```python
previous_sessions = set()

async def monitor_sessions():
    """Call every 10-30 seconds."""
    current = await client.call_tool("list_sessions")
    current_keys = {s["session_key"] for s in current}

    # Detect changes
    new = current_keys - previous_sessions
    removed = previous_sessions - current_keys

    if new:
        print(f"🆕 New sessions: {new}")
    if removed:
        print(f"🔴 Removed sessions: {removed}")

    previous_sessions = current_keys
```

## Configuration

The SessionManager still scans in the background:

```python
SessionManager(
    scan_interval=10.0,  # Check for new sessions every 10 seconds
    client_type=ClientType.QT
)
```

Clients should poll `list_sessions` at a similar or slightly longer interval.

## What Server Operators See

When running the MCP server, operators see:

```
2026-01-05 10:15:23 - maya_mcp_server.session_manager - INFO - 🆕 Discovered Maya session at 127.0.0.1:56789 (PID 8453, Maya 2024, Scene: character_rig.ma)
2026-01-05 10:20:45 - maya_mcp_server.session_manager - INFO - 🔴 Removed dead session: 127.0.0.1:56789
```

These help with debugging but aren't sent to MCP clients.

## Benefits of This Approach

✅ **Simpler** - Removed redundant notification code from `list_sessions`
✅ **More honest** - Acknowledges MCP's limitations instead of working around them
✅ **Standard pattern** - Follows MCP's pull-based design
✅ **Still flexible** - Notification infrastructure remains for future extensions
✅ **Better logging** - Server operators get rich diagnostic information

## Files Changed

- `src/maya_mcp_server/server.py` - Simplified `list_sessions`, removed Context import
- `src/maya_mcp_server/session_manager.py` - Enhanced logging for discoveries/removals
- `MCP_NOTIFICATION_LIMITATIONS.md` - Documents why push notifications don't work
- `NOTIFICATION_REFACTOR_SUMMARY.md` - This file

## Files No Longer Relevant

- `SESSION_NOTIFICATIONS.md` - Described the old notification approach
- `FEATURE_SUMMARY.md` - Described the old implementation
- `test_session_notifications.py` - Tests for old notification system
- `test_notifications_integration.py` - Integration tests for old system

These can be deleted or kept for reference.

## Testing

The simplified implementation works correctly:

```bash
uv run python -c "
import asyncio
from maya_mcp_server.server import initialize_session_manager, list_sessions

async def test():
    await initialize_session_manager()
    sessions = await list_sessions.fn()
    print(f'Found {len(sessions)} sessions')

asyncio.run(test())
"
```

## Summary

Your instinct was correct - the notification system was solving a problem that didn't exist. MCP clients should simply poll `list_sessions` periodically and compare results to detect changes. This is simpler, more reliable, and aligns with MCP's design philosophy.

The notification infrastructure remains in place for potential future custom extensions (like webhooks), but it's no longer exposed through the MCP protocol.
