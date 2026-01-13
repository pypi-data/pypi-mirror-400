"""
Runtime patch for MCP SDK session manager to return 404 instead of 400 for invalid sessions.

This fixes non-compliance with the MCP specification:
https://modelcontextprotocol.io/specification/2025-06-18/basic/transports

According to spec:
- 400 Bad Request: Session ID header is MISSING
- 404 Not Found: Session ID is PROVIDED but invalid/expired

IMPORTANT: This patch is technically correct, but most MCP clients (VSCode, Cursor, mcp-remote)
have bugs and don't properly handle 404 responses. They should reinitialize on 404 but don't.
See: https://github.com/microsoft/vscode/issues/253854

RECOMMENDATION: Use stateless_http=True instead to avoid all session management issues.

This patch is kept for:
1. Documentation of the correct behavior per MCP spec
2. Future use if/when MCP clients fix their 404 handling
3. Testing with compliant MCP clients
"""

import logging
from http import HTTPStatus
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

logger = logging.getLogger("mcp_trendminer_server.patches")


def patch_session_manager():
    """
    Patch StreamableHTTPSessionManager to return 404 for invalid session IDs.

    This monkey-patches the _handle_stateful_request method to comply with MCP spec.

    WARNING: Most MCP clients don't handle 404 correctly and will get stuck.
    Only use this if you have a compliant MCP client or are testing the spec.
    """
    try:
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

        # Store original method
        original_handle_stateful = StreamableHTTPSessionManager._handle_stateful_request

        async def patched_handle_stateful(
            self, scope: Scope, receive: Receive, send: Send
        ) -> None:
            """Handle stateful HTTP requests with MCP-compliant status codes."""

            # Check for session ID in headers
            headers = dict(scope.get("headers", []))
            session_id_bytes = headers.get(b"mcp-session-id")

            if session_id_bytes:
                session_id = session_id_bytes.decode("utf-8")

                # Check if session exists
                if session_id not in self._server_instances:
                    # Invalid/expired session ID - return 404 per MCP spec
                    logger.info(
                        f"[Patch] Invalid session ID {session_id[:16]}... - returning 404 (MCP spec compliant)"
                    )
                    response = Response(
                        "Not Found: Session has expired or does not exist",
                        status_code=HTTPStatus.NOT_FOUND,  # 404 per MCP spec
                    )
                    await response(scope, receive, send)
                    return

            # Valid session or no session ID - use original implementation
            await original_handle_stateful(self, scope, receive, send)

        # Apply the patch
        StreamableHTTPSessionManager._handle_stateful_request = patched_handle_stateful

        logger.info("[Patch] Applied MCP session manager patch (400 → 404 for invalid sessions)")
        logger.warning("[Patch] WARNING: Most MCP clients don't handle 404 correctly. Use stateless_http=True instead.")

    except Exception as e:
        logger.error(f"[Patch] Failed to apply session manager patch: {e}")
        logger.warning("[Patch] Server will use default behavior (returns 400 for invalid sessions)")
