"""TrendMiner client caching for token-based performance optimization."""

import os
import logging
from zoneinfo import ZoneInfo

from trendminer_interface import TrendMinerClient
from mcp_trendminer_server.auth import get_current_access_token
from mcp_trendminer_server.settings import settings

logger = logging.getLogger("mcp_trendminer_server")

# Cache commonly used objects to avoid repeated parsing/lookups
_TM_TIMEZONE = ZoneInfo("Europe/Brussels")

# Token-based client cache for performance optimization
# Key: f"{token_hash}" -> TrendMinerClient
# This significantly improves performance by reusing clients across requests with the same token
# Works with both stateful and stateless HTTP transport modes
_client_cache: dict[str, TrendMinerClient] = {}


def _get_tm_server_url() -> str:
    """
    Get TM_SERVER_URL from environment, with validation.

    Raises:
        ValueError: If TM_SERVER_URL is not set
    """
    url = os.getenv("TM_SERVER_URL")
    if not url:
        raise ValueError("TM_SERVER_URL environment variable is required")
    return url


def get_tm_client() -> TrendMinerClient:
    """
    Get or create a TrendMinerClient instance based on authentication mode.

    In OAuth mode: Caches client per token for 5-10x performance improvement.
    In credentials mode: Uses a single cached client with fixed credentials.

    Returns
    -------
    TrendMinerClient
        A configured TrendMiner client instance.

    Raises
    ------
    RuntimeError
        If OAuth mode and no token is available, or if credentials are missing.
    """
    if settings.auth_mode == "credentials":
        # Credentials mode: Use fixed client_id, client_secret, username, password
        cache_key = "credentials_client"

        # Check if we have a cached client
        if cache_key in _client_cache:
            logger.debug(f"[Cache] Reusing cached TrendMinerClient (credentials mode)")
            return _client_cache[cache_key]

        # Create new client with credentials
        logger.info(f"[Cache] Creating TrendMinerClient with credentials (user: {settings.tm_username})")
        client = TrendMinerClient(
            url=_get_tm_server_url(),
            client_id=settings.tm_client_id,
            client_secret=settings.tm_client_secret,
            username=settings.tm_username,
            password=settings.tm_password,
            tz=_TM_TIMEZONE,
        )

        _client_cache[cache_key] = client
        logger.info(f"[Cache] Cached credentials-based TrendMinerClient")
        return client

    else:
        # OAuth mode: Use token from request context
        token = get_current_access_token()
        if not token:
            raise RuntimeError(
                "No OAuth token available. This tool requires authentication. "
                "Make sure requests include a valid Bearer token in the Authorization header."
            )

        # Create cache key from token hash only (works with stateless_http=True)
        # Using hash of token to avoid storing full token in cache key
        token_hash = hash(token) & 0xFFFFFFFF  # 32-bit hash
        cache_key = f"oauth_{token_hash}"

        # Check if we have a cached client for this token
        if cache_key in _client_cache:
            logger.debug(f"[Cache] Reusing cached TrendMinerClient (OAuth, token: ...{token[-8:]})")
            return _client_cache[cache_key]

        # Create new client and cache it
        client = TrendMinerClient(
            url=_get_tm_server_url(),
            access_token_getter=lambda: get_current_access_token(),
            tz=_TM_TIMEZONE,
        )

        _client_cache[cache_key] = client
        logger.info(f"[Cache] Created and cached new TrendMinerClient (OAuth, token: ...{token[-8:]}, cache size: {len(_client_cache)})")

        # Simple cache cleanup to prevent unbounded growth
        # Keep cache size under 200 entries (generous limit for token-based caching)
        if len(_client_cache) > 200:
            logger.warning(f"[Cache] Cache has {len(_client_cache)} entries, clearing to prevent memory issues")
            # Clear oldest half
            items = list(_client_cache.items())
            _client_cache.clear()
            _client_cache.update(dict(items[-100:]))  # Keep most recent 100

        return client
