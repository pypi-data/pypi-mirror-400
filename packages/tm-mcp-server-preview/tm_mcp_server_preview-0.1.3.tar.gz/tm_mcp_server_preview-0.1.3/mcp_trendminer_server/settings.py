import os
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

# Load .env file BEFORE Settings class is created
# Check current directory first, then fall back to relative path
_cwd = Path.cwd()
_env_paths = [_cwd / ".env", Path(".env")]

for _env_path in _env_paths:
    if _env_path.exists():
        load_dotenv(_env_path, override=True)
        break

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TM_MCP_",
        case_sensitive=False,
        extra="ignore",  # Allow extra environment variables (like TM_SERVER_URL, etc.)
    )

    # Server configuration
    protocol: str = Field(default="http", description="Server protocol")
    bind_host: str = Field(default="0.0.0.0", description="Host address to bind the server to")
    bind_port: int = Field(default=8765, description="Server port")

    resource_server: str = Field(default="http://localhost:8765", description="External server host/URL for OAuth redirects")
    authorization_server: str = Field(default="https://tm-test-arch01.trendminer.net", description="Authorization server URL")

    dev_mode: bool = Field(default=False, description="Enable development mode")

    # TrendMiner authentication mode detection
    @property
    def auth_mode(self) -> Literal["oauth", "credentials"]:
        """
        Determine authentication mode based on environment variables.

        Returns "credentials" if all of TM_CLIENT_ID, TM_CLIENT_SECRET,
        TM_USERNAME, and TM_PASSWORD are set.
        Otherwise returns "oauth".
        """
        if self.tm_client_id and self.tm_client_secret and self.tm_username and self.tm_password:
            return "credentials"
        return "oauth"

    @property
    def tm_client_id(self) -> Optional[str]:
        """TrendMiner OAuth client ID (for credentials mode)."""
        return os.getenv("TM_CLIENT_ID")

    @property
    def tm_client_secret(self) -> Optional[str]:
        """TrendMiner OAuth client secret (for credentials mode)."""
        return os.getenv("TM_CLIENT_SECRET")

    @property
    def tm_username(self) -> Optional[str]:
        """TrendMiner username (for credentials mode)."""
        return os.getenv("TM_USERNAME")

    @property
    def tm_password(self) -> Optional[str]:
        """TrendMiner password (for credentials mode)."""
        return os.getenv("TM_PASSWORD")

    @property
    def server_url(self) -> str:
        """TrendMiner server URL."""
        return os.getenv("TM_SERVER_URL", "")

settings = Settings()