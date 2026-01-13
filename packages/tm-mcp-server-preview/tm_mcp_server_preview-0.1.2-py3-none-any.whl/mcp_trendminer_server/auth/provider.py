"""OAuth authentication provider for TrendMiner MCP server."""

import logging
import httpx
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.auth import RemoteAuthProvider
from pydantic import AnyHttpUrl
from starlette.routing import Route
from fastapi.responses import JSONResponse

from mcp_trendminer_server.auth.context import set_current_access_token

logger = logging.getLogger("mcp_trendminer_server.auth")


class CompleteRemoteAuthProvider(RemoteAuthProvider):
    """Custom RemoteAuthProvider that exposes OAuth metadata endpoints."""

    def __init__(self, token_verifier, authorization_server, resource_server_url):
        self.authorization_server = authorization_server
        self.resource_server_url = resource_server_url
        super().__init__(
            token_verifier,
            [AnyHttpUrl(authorization_server)],
            resource_server_url
        )

    def get_routes(self, mcp_path) -> list[Route]:
        """Return OAuth metadata routes for MCP clients."""

        async def oauth_authorization_server_metadata(request):
            """Proxy Keycloak's OpenID configuration."""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.authorization_server}/.well-known/openid-configuration"
                    )
                    response.raise_for_status()
                    metadata = response.json()
                    metadata["resource"] = str(self.resource_server_url)
                    metadata["scopes_supported"] = ["openid", "roles", "basic", "profile"]
                    logger.info(f"[OAuth] Served OAuth metadata from {self.authorization_server}")
                    return JSONResponse(metadata)
            except Exception as e:
                logger.error(f"[OAuth] Failed to fetch Keycloak metadata: {e}")
                return JSONResponse(
                    {
                        "error": "server_error",
                        "error_description": f"Failed to fetch KeyCloak metadata: {e}",
                    },
                    status_code=500,
                )

        async def oauth_protected_resource_metadata(request):
            """Return protected resource metadata for this MCP server."""
            response = {
                "resource": str(self.resource_server_url),
                "issuer": f"{self.authorization_server}",
                "authorization_endpoint": f"{self.authorization_server}/protocol/openid-connect/auth",
                "token_endpoint": f"{self.authorization_server}/protocol/openid-connect/token",
                "jwks_uri": f"{self.authorization_server}/protocol/openid-connect/certs",
                "scopes_supported": ["openid", "roles", "basic", "profile"],
                "bearer_methods_supported": ["header"],
                "mcp_endpoint": f"{self.resource_server_url}{mcp_path}"
            }
            logger.info(f"[OAuth] Served protected resource metadata")
            return JSONResponse(response)

        # Register routes at both root and MCP path for compatibility
        routes = [
            # Root-level routes (required by OAuth 2.0 spec and mcp-remote 0.1.37+)
            Route("/.well-known/oauth-protected-resource", endpoint=oauth_protected_resource_metadata,
                  methods=["GET", "OPTIONS"]),
            Route("/.well-known/oauth-authorization-server", endpoint=oauth_authorization_server_metadata,
                  methods=["GET", "OPTIONS"]),
            Route("/.well-known/openid-configuration", endpoint=oauth_authorization_server_metadata,
                  methods=["GET", "OPTIONS"]),
            # MCP path routes (for backwards compatibility)
            Route(f"{mcp_path}/.well-known/oauth-protected-resource", endpoint=oauth_protected_resource_metadata,
                  methods=["GET", "OPTIONS"]),
            Route(f"{mcp_path}/.well-known/oauth-authorization-server", endpoint=oauth_authorization_server_metadata,
                  methods=["GET", "OPTIONS"]),
            Route(f"{mcp_path}/.well-known/openid-configuration", endpoint=oauth_authorization_server_metadata,
                  methods=["GET", "OPTIONS"]),
        ]
        return routes


class LoggingJWTVerifier(JWTVerifier):
    """JWT Verifier that logs tokens and stores them in context for later use."""

    async def verify_token(self, token: str):
        """Verify the token, log it, and store it in context."""
        import time
        from datetime import datetime, timezone

        # Log token info
        logger.info(f"[OAuth] Access token received: {token[:20]}...{token[-20:]}")
        logger.info(f"[OAuth] Full token length: {len(token)} characters")

        # Check if dev mode is enabled to log full token
        from mcp_trendminer_server.settings import settings
        if settings.dev_mode:
            logger.debug(f"[OAuth] Full access token: {token}")

        # Call parent verification (it's async, so await it)
        result = await super().verify_token(token)

        # If verification succeeded, check expiration with buffer and store the token
        if result is not None:
            # Add extra validation: reject tokens expiring within 60 seconds
            exp = result.claims.get("exp")
            if exp:
                time_until_expiry = exp - time.time()
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                logger.info(f"[OAuth] Token expires at: {exp_datetime.isoformat()} (in {int(time_until_expiry)} seconds)")

                # Reject tokens expiring within 2 minutes (120 seconds)
                # This gives buffer for mcp-remote proxy latency and request processing
                if time_until_expiry < 120:
                    logger.warning(f"[OAuth] Token expires too soon ({int(time_until_expiry)}s), rejecting. Need at least 120s.")
                    return None

            set_current_access_token(token)

        return result


def create_auth(mcp_server: str, authorization_server: str):
    """
    Create and configure the OAuth authentication provider.

    Args:
        mcp_server: The MCP server URL (resource server)
        authorization_server: The Keycloak authorization server URL

    Returns:
        CompleteRemoteAuthProvider configured for TrendMiner OAuth
    """
    token_verifier = LoggingJWTVerifier(
        jwks_uri=f"{authorization_server}/auth/realms/trendminer/protocol/openid-connect/certs",
        issuer=f"{authorization_server}/auth/realms/trendminer",
    )

    auth = CompleteRemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_server=f"{authorization_server}/auth/realms/trendminer",
        resource_server_url=mcp_server,
    )

    return auth
