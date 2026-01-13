"""Connectivity checks for TrendMiner server."""

import logging
import os
import sys

import requests

logger = logging.getLogger("mcp_trendminer_server")


def check_server_connectivity():
    """Check if TrendMiner server is reachable before starting."""
    tm_server_url = os.getenv("TM_SERVER_URL")

    if not tm_server_url:
        logger.error("[Connectivity] TM_SERVER_URL not set in environment")
        sys.exit(1)

    logger.info(f"[Connectivity] Checking connection to TrendMiner server: {tm_server_url}")

    try:
        # Try to reach the server with a short timeout
        response = requests.get(tm_server_url, timeout=5, verify=True)
        logger.info(f"[Connectivity] ✓ Successfully connected to TrendMiner server (status: {response.status_code})")
        return True
    except requests.exceptions.SSLError as e:
        logger.error(f"[Connectivity] ✗ SSL certificate error connecting to {tm_server_url}")
        # logger.error(f"[Connectivity] Error: {e}")
        logger.warning("[Connectivity] 💡 Suggestion: Check if you need to turn on your VPN")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[Connectivity] ✗ Cannot connect to TrendMiner server at {tm_server_url}")
        # logger.error(f"[Connectivity] Error: {e}")
        logger.warning("[Connectivity] 💡 Suggestion: Check if you need to turn on your VPN")
        sys.exit(1)
    except requests.exceptions.Timeout:
        logger.error(f"[Connectivity] ✗ Connection timeout to {tm_server_url}")
        logger.warning("[Connectivity] 💡 Suggestion: Check if you need to turn on your VPN")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[Connectivity] ✗ Unexpected error connecting to {tm_server_url}")
        # logger.error(f"[Connectivity] Error: {e}")
        logger.warning("[Connectivity] 💡 Suggestion: Check if you need to turn on your VPN")
        sys.exit(1)
