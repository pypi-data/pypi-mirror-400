"""Runtime patches for third-party libraries."""

from mcp_trendminer_server.patches.mcp_session_manager import patch_session_manager
from mcp_trendminer_server.patches.auto_recovery import patch_session_manager_auto_recovery

__all__ = ["patch_session_manager", "patch_session_manager_auto_recovery"]
