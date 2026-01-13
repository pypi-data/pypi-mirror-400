"""Authentication module for MCP TrendMiner Server."""

import logging
from typing import Optional
from mcp_trendminer_server.auth.provider import create_auth, CompleteRemoteAuthProvider
from mcp_trendminer_server.auth.context import get_current_access_token
from mcp_trendminer_server.settings import settings

logger = logging.getLogger("mcp_trendminer_server.auth")

__all__ = ["create_auth", "get_current_access_token", "create_auth_provider"]


def create_auth_provider() -> Optional[CompleteRemoteAuthProvider]:
    """
    Create authentication provider based on environment settings.

    Returns:
        - CompleteRemoteAuthProvider for OAuth mode
        - None for credentials mode (no OAuth needed)
    """
    if settings.auth_mode == "credentials":
        logger.info("[Auth] Using credentials mode (TM_CLIENT_ID, TM_CLIENT_SECRET, TM_USERNAME, TM_PASSWORD)")
        logger.info(f"[Auth] Client ID: {settings.tm_client_id}")
        logger.info(f"[Auth] Username: {settings.tm_username}")
        return None  # No OAuth provider needed
    else:
        logger.info("[Auth] Using OAuth mode")
        logger.info(f"[Auth] Resource Server: {settings.resource_server}")
        logger.info(f"[Auth] Authorization Server: {settings.authorization_server}")
        return create_auth(
            mcp_server=settings.resource_server,
            authorization_server=settings.authorization_server
        )
