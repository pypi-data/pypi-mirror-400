"""
Auto-recovery patch for MCP session management.

This patch makes the server automatically recover from invalid session IDs by:
1. Detecting when a client sends an invalid/expired session ID
2. Stripping the invalid session ID from the request
3. Allowing the request to proceed as a "new session" request

This works around MCP client bugs where clients don't properly reinitialize on 404.

IMPORTANT: This only helps if the client sends an initialize request after restart.
If the client tries to call tools with an invalid session, it will still fail
(correctly) because you can't call tools without initializing first.
"""

import logging
from starlette.types import Receive, Scope, Send

logger = logging.getLogger("mcp_trendminer_server.patches")


def patch_session_manager_auto_recovery():
    """
    Patch StreamableHTTPSessionManager to automatically handle invalid session IDs.

    When a client sends an invalid session ID:
    1. Log the invalid session for debugging
    2. Strip the session ID from the request headers
    3. Process as a fresh request (will create new session for initialize requests)

    This approach:
    - Works around clients that don't handle 404 correctly
    - Still requires client to eventually send initialize request
    - Prevents clients from getting "stuck" with invalid session IDs
    """
    try:
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

        # Store original method
        original_handle_stateful = StreamableHTTPSessionManager._handle_stateful_request

        async def patched_handle_stateful_with_recovery(
            self, scope: Scope, receive: Receive, send: Send
        ) -> None:
            """Handle stateful requests with automatic session recovery."""

            # Get headers
            headers = dict(scope.get("headers", []))
            session_id_bytes = headers.get(b"mcp-session-id")

            if session_id_bytes:
                session_id = session_id_bytes.decode("utf-8")

                # Check if session is invalid
                if session_id not in self._server_instances:
                    logger.warning(
                        f"[Recovery] Client sent invalid session ID {session_id[:16]}... "
                        f"(server was probably restarted)"
                    )
                    logger.info(
                        f"[Recovery] Stripping invalid session ID to allow re-initialization"
                    )

                    # Strip the invalid session ID from headers
                    # This makes the request look like a "no session" request
                    new_headers = [
                        (name, value)
                        for name, value in scope.get("headers", [])
                        if name != b"mcp-session-id"
                    ]
                    scope["headers"] = new_headers

                    logger.info(
                        f"[Recovery] Request will be processed without session ID. "
                        f"Client should send 'initialize' to create a new session."
                    )

            # Process with original handler
            # If headers have no session ID, this will:
            # - Allow 'initialize' requests → creates new session
            # - Reject other requests with 400 (correct - can't call tools without session)
            await original_handle_stateful(self, scope, receive, send)

        # Apply the patch
        StreamableHTTPSessionManager._handle_stateful_request = patched_handle_stateful_with_recovery

        logger.info("[Patch] Applied auto-recovery session manager patch")
        logger.info("[Patch] Server will automatically strip invalid session IDs")
        logger.info("[Patch] Clients must send 'initialize' request after server restarts")

    except Exception as e:
        logger.error(f"[Patch] Failed to apply auto-recovery patch: {e}")
        logger.warning("[Patch] Server will use default behavior")
