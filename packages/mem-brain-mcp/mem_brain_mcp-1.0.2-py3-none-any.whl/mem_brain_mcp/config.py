"""Configuration management for Mem-Brain MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Configuration
    api_base_url: str = "http://membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com"
    membrain_api_key: Optional[str] = None
    # NOTE: default_user_id is deprecated and unused.
    # Per-user API keys are extracted from request headers for proper isolation.
    # Each MCP client should configure their own API key via headers.
    
    @property
    def api_key(self) -> Optional[str]:
        """Backward compatibility property for api_key."""
        return self.membrain_api_key

    # MCP Server Configuration
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8100

    # Logging
    log_level: str = "INFO"

    @property
    def api_url(self) -> str:
        """Get the full API base URL."""
        return self.api_base_url.rstrip("/")


# Global settings instance
settings = Settings()

