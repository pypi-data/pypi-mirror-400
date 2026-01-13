# MCP Protocol Limitations: Push Notifications

## The Problem

We want the MCP server to **proactively notify clients** when new Maya sessions are discovered or when existing sessions disconnect. However, the MCP protocol and FastMCP have fundamental limitations that prevent true push notifications from background tasks.

## Why Push Notifications Don't Work

### 1. Context is Request-Scoped

FastMCP's `Context` object (which provides notification methods like `ctx.info()`, `ctx.send_resource_list_changed()`) **only exists during request handling**:

```python
@mcp.tool
async def some_tool(ctx: Context):  # ✅ ctx exists here
    ctx.info("This works - we're in a request")

# Background task - NO ctx available
async def background_scanner():
    # ❌ No way to call ctx.info() from here
    # ❌ No way to send notifications to connected clients
    pass
```

### 2. No Persistent Client Connections

FastMCP doesn't expose:
- Connected client sessions
- Client connection registry
- Any way for background tasks to send data to clients

The MCP protocol is fundamentally **request/response**, not **publish/subscribe**.

### 3. What MCP Does Support

MCP supports these notification mechanisms:

| Mechanism | When It Works | Limitation |
|-----------|---------------|------------|
| `ctx.info()` logging | During request handling | Requires active request |
| `ctx.send_resource_list_changed()` | During request handling | Requires active request |
| Resource subscriptions | Client reads resources | Still pull-based, client must poll |
| Server logs (stdout/stderr) | Always | Not part of MCP protocol, client-dependent |

**All MCP notification methods require an active request Context.**

## The MCP Way: Pull-Based Pattern

MCP is designed around clients **polling for changes**, not servers pushing notifications:

```
Client                              Server
  |                                   |
  |  1. list_sessions()              |
  |--------------------------------->|
  |  [session1, session2]            |
  |<---------------------------------|
  |                                   |
  | (wait 10 seconds)                |
  |                                   | (background scanner finds session3)
  |                                   |
  |  2. list_sessions()              |
  |--------------------------------->|
  |  [session1, session2, session3]  |  ← Client compares and detects new session
  |<---------------------------------|
```

## Recommended Implementation

### For Clients (AI Agents)

**Poll `list_sessions` periodically and compare results:**

```python
previous_sessions = set()

async def check_for_session_changes():
    """Call this every 10-30 seconds."""
    current = await client.call_tool("list_sessions")
    current_sessions = {s["session_key"] for s in current}

    # Detect new sessions
    new_sessions = current_sessions - previous_sessions
    for key in new_sessions:
        print(f"🆕 New session detected: {key}")

    # Detect removed sessions
    removed_sessions = previous_sessions - current_sessions
    for key in removed_sessions:
        print(f"🔴 Session removed: {key}")

    previous_sessions = current_sessions
```

### For Server Operators

The SessionManager logs discoveries/removals for debugging:

```
2026-01-05 10:15:23 - maya_mcp_server.session_manager - INFO - 🆕 Discovered Maya session at 127.0.0.1:56789 (PID 8453, Maya 2024, Scene: character_rig.ma)
2026-01-05 10:20:45 - maya_mcp_server.session_manager - INFO - 🔴 Removed dead session: 127.0.0.1:56789
```

These logs appear in the server's stdout/stderr for monitoring.

## Alternative Approaches (Outside MCP)

If you absolutely need push notifications, you'd have to implement a **custom notification channel outside of MCP**:

### 1. WebHook URL
```python
# Client provides a webhook URL
# Server POSTs to it when sessions change
session_manager.set_webhook("https://client.example.com/notifications")
```

### 2. Separate WebSocket
```python
# Run a separate WebSocket server for notifications
# Clients connect to both MCP (for tools) and WS (for notifications)
```

### 3. SSE (Server-Sent Events)
```python
# If using SSE transport, could potentially use it for notifications
# But FastMCP doesn't expose this easily
```

**However, all of these are non-standard and add complexity.**

## Current Implementation

### What We Keep

1. **Notification queues in SessionManager** - Kept for potential future use (webhooks, custom extensions)
2. **Server-side logging** - Operators can see discoveries/removals in logs
3. **`get_pending_notifications()`** - Available if someone builds a custom notification system

### What We Removed

1. **Notifications in `list_sessions` tool** - Redundant, clients can infer changes
2. **Context-based logging to clients** - Doesn't work from background tasks

## Conclusion

**MCP doesn't support true push notifications from background tasks.** This is a protocol limitation, not a bug.

The recommended approach is:
- ✅ **Clients poll `list_sessions` periodically** (every 10-30 seconds)
- ✅ **Clients compare results to detect changes**
- ✅ **SessionManager logs to stdout/stderr for server operators**
- ❌ **Don't try to push notifications from background tasks** (won't work)

This aligns with MCP's request/response design and works reliably across all MCP clients.

## Future Possibilities

If MCP adds support for:
- Server-to-client notification channels
- Persistent connection tracking
- Background task notification APIs

Then we could revisit push notifications. But as of now (MCP 1.0, FastMCP 2.x), it's not possible within the standard protocol.
