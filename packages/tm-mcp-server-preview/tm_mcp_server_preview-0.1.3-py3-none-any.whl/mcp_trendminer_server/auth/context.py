"""OAuth token context management."""

import logging
from contextvars import ContextVar
from typing import Optional

logger = logging.getLogger("mcp_trendminer_server.auth")

# Context variable to store the current access token for the request
current_access_token: ContextVar[Optional[str]] = ContextVar('current_access_token', default=None)


def get_current_access_token() -> Optional[str]:
    """
    Get the current OAuth access token from the request context.

    Returns the token if available in the current request context, or None otherwise.
    This should only be called during an authenticated request.
    """
    token = current_access_token.get()
    if token:
        logger.debug(f"[OAuth] Providing OAuth access token: {token[:20]}...")
    return token


def set_current_access_token(token: str) -> None:
    """
    Set the current OAuth access token in the request context.

    This is called by the LoggingJWTVerifier after successful token verification.
    """
    current_access_token.set(token)
    logger.info("[OAuth] Token verified and stored in context for TrendMinerClient")
