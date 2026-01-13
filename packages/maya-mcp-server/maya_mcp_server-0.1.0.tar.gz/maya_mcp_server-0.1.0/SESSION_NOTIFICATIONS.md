# Session Discovery Notifications

## Overview

The Maya MCP Server now includes a notification system that alerts MCP clients when new Maya sessions are discovered or when existing sessions disconnect. This allows clients to stay informed about changes to the Maya environment without constantly polling.

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SessionManager                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Background Scanner (every scan_interval seconds)      │ │
│  │  - Scans for new Maya ports                            │ │
│  │  - Discovers new sessions → adds to _new_sessions      │ │
│  │  - Detects dead sessions → adds to _removed_sessions   │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Notification Queues (asyncio.Queue)                   │ │
│  │  - _new_sessions: Queue[SessionInfo]                   │ │
│  │  - _removed_sessions: Queue[str]                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  MCP Server (server.py)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  list_sessions() tool                                  │ │
│  │  1. Calls get_pending_notifications()                  │ │
│  │  2. For each new session:                              │ │
│  │     ctx.info("🆕 New Maya session discovered...")      │ │
│  │  3. For each removed session:                          │ │
│  │     ctx.info("🔴 Maya session disconnected...")        │ │
│  │  4. Returns current session list                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                     MCP Client                              │
│  - Receives log messages via MCP protocol                   │
│  - Sees notifications in real-time                          │
│  - Can react to session changes                             │
└─────────────────────────────────────────────────────────────┘
```

### Notification Flow

1. **Discovery**: SessionManager's background scanner discovers a new Maya session
2. **Queue**: Session info is added to `_new_sessions` queue
3. **Client Call**: MCP client calls `list_sessions()` tool
4. **Check Notifications**: Server calls `get_pending_notifications()` which drains the queues
5. **Log to Client**: Server uses `Context.info()` to send log messages to the client
6. **Client Receives**: Client sees notifications as MCP log messages

## Implementation Details

### SessionManager Changes

Added to `session_manager.py`:

```python
# New fields in __init__
self._new_sessions: asyncio.Queue[SessionInfo] = asyncio.Queue()
self._removed_sessions: asyncio.Queue[str] = asyncio.Queue()

# New method
async def get_pending_notifications(self) -> dict[str, list]:
    """Get and clear pending session change notifications."""
    # Drains both queues and returns their contents
```

**When sessions are discovered:**
```python
# In _scan_for_sessions() and add_session()
session_info = await client.session_info()
await self._new_sessions.put(session_info)
```

**When sessions are removed:**
```python
# In _prune_dead_sessions()
await self._removed_sessions.put(session_key)
```

### Server Changes

Modified `server.py`:

```python
from fastmcp import Context, FastMCP

@mcp.tool
async def list_sessions(ctx: Context) -> list[SessionInfo]:
    """List all active Maya sessions with notifications."""
    manager = get_session_manager()

    # Check for pending notifications
    notifications = await manager.get_pending_notifications()

    # Log new session discoveries
    for session in notifications["new_sessions"]:
        ctx.info(
            f"🆕 New Maya session discovered: {session.host}:{session.port} "
            f"(Maya {session.maya_version}, Scene: {session.scene_name})"
        )

    # Log removed sessions
    for session_key in notifications["removed_sessions"]:
        ctx.info(f"🔴 Maya session disconnected: {session_key}")

    return await manager.list_sessions()
```

## Usage

### For MCP Clients

MCP clients automatically receive notifications when they call the `list_sessions` tool:

```python
# Client calls list_sessions
result = await client.call_tool("list_sessions")

# Client receives log messages in MCP protocol:
# {
#   "method": "notifications/message",
#   "params": {
#     "level": "info",
#     "logger": "maya_mcp_server.sessions",
#     "data": "🆕 New Maya session discovered: 127.0.0.1:56789 (Maya 2024, Scene: myrig.ma)"
#   }
# }
```

### For Claude Code

When using Claude Code with the Maya MCP Server, Claude will see these notifications in the conversation:

```
Claude: Let me check for Maya sessions...
[calls list_sessions tool]

System: 🆕 New Maya session discovered: 127.0.0.1:56789 (Maya 2024, Scene: myrig.ma)

Claude: I see a new Maya session has been discovered!
Maya 2024 is running with the scene "myrig.ma" on port 56789.
Would you like me to connect to it?
```

## Testing

Run the test script to verify notifications work:

```bash
uv run python test_session_notifications.py
```

Expected output:
- Shows initial session discovery with notification
- Waits for background scan
- Reports any new sessions discovered during the scan
- Demonstrates the notification flow

## Key Features

✅ **Automatic Discovery**: Sessions are automatically discovered during background scans

✅ **Real-time Notifications**: Clients are notified immediately when calling `list_sessions`

✅ **Non-blocking**: Uses asyncio queues to avoid blocking the background scanner

✅ **One-time Delivery**: Each notification is delivered once and then cleared

✅ **Session Removal Tracking**: Clients are notified when sessions disconnect

✅ **Rich Information**: New session notifications include Maya version, scene name, host, and port

## Configuration

The notification system works with the existing SessionManager configuration:

```python
# Shorter scan interval = faster discovery of new sessions
manager = SessionManager(
    scan_interval=5.0,  # Check for new sessions every 5 seconds
    client_type=ClientType.QT
)
```

## Notes

- Notifications are **queued** until the next `list_sessions` call
- If no client calls `list_sessions`, notifications accumulate in the queue
- Each notification is delivered **once** - after a client retrieves notifications, they are cleared
- The notification queue is **in-memory** and not persisted across server restarts
- Notifications use MCP's standard logging mechanism (`notifications/message`)

## Future Enhancements

Possible improvements:

1. **Resource-based notifications**: Use MCP's `notifications/resources/list_changed` for more semantic notifications
2. **Persistent notification log**: Store notifications in a file for debugging
3. **Notification filtering**: Allow clients to subscribe only to specific types of notifications
4. **Session metadata changes**: Notify when scene name or other metadata changes
5. **Heartbeat notifications**: Periodic "still alive" notifications for long-running sessions

## Example Scenarios

### Scenario 1: New Maya Instance Started

```
1. User starts Maya with command port on :7002
2. SessionManager background scan detects port 7002
3. SessionManager probes port and establishes session
4. SessionInfo queued in _new_sessions
5. Claude calls list_sessions
6. Claude receives: "🆕 New Maya session discovered: 127.0.0.1:52341 (Maya 2024, Scene: untitled)"
7. Claude: "I see you've started a new Maya session! Would you like me to interact with it?"
```

### Scenario 2: Maya Crashes

```
1. Maya process terminates unexpectedly
2. Background scanner's next cycle tries to ping session
3. Ping fails, session marked as dead
4. Session key queued in _removed_sessions
5. Claude calls list_sessions
6. Claude receives: "🔴 Maya session disconnected: 127.0.0.1:52341"
7. Claude: "It looks like the Maya session crashed. Would you like me to wait for it to restart?"
```

### Scenario 3: Multiple Sessions

```
1. Artist has Maya 2023 and Maya 2024 both open
2. Both sessions are discovered and notifications queued
3. Claude calls list_sessions
4. Claude receives two notifications:
   - "🆕 New Maya session discovered: 127.0.0.1:51234 (Maya 2023, Scene: oldrig.ma)"
   - "🆕 New Maya session discovered: 127.0.0.1:52345 (Maya 2024, Scene: newrig.ma)"
5. Claude: "I found two Maya sessions! Would you like to work with Maya 2023 (oldrig.ma) or Maya 2024 (newrig.ma)?"
```

## Troubleshooting

**Q: I'm not seeing notifications for new sessions**

A: Ensure that:
- `list_sessions` is being called after sessions are discovered
- Background scanner is running (`SessionManager.start()` was called)
- New Maya instances have command ports open

**Q: Notifications are appearing multiple times**

A: This shouldn't happen as queues are drained. If it does, check that:
- Only one SessionManager instance is running
- `get_pending_notifications()` is properly draining the queues

**Q: Notifications are delayed**

A: Notifications only appear when `list_sessions` is called. To get faster notifications:
- Reduce `scan_interval` for faster discovery
- Call `list_sessions` more frequently
