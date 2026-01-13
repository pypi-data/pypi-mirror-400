"""Configuration management for TradePose Client.

This module provides environment-based configuration using Pydantic Settings.
All configuration can be set via environment variables with TRADEPOSE_ prefix.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TradePoseConfig(BaseSettings):
    """TradePose client configuration.

    Configuration is loaded from environment variables with TRADEPOSE_ prefix.
    Supports .env file loading for local development.

    Environment Variables:
        TRADEPOSE_API_KEY: API key for authentication (required if jwt_token not provided)
        TRADEPOSE_SERVER_URL: Base URL for TradePose Gateway API
        TRADEPOSE_JWT_TOKEN: JWT token for authentication (optional, used for API key creation)
        TRADEPOSE_TIMEOUT: Request timeout in seconds
        TRADEPOSE_MAX_RETRIES: Maximum number of retry attempts
        TRADEPOSE_POLL_INTERVAL: Default task polling interval in seconds
        TRADEPOSE_POLL_TIMEOUT: Default task polling timeout in seconds
        TRADEPOSE_DEBUG: Enable debug mode with verbose logging
        TRADEPOSE_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> config = TradePoseConfig(api_key="tp_live_xxx", server_url="https://api.tradepose.com")
        >>> config = TradePoseConfig()  # Load from environment
    """

    model_config = SettingsConfigDict(
        env_prefix="TRADEPOSE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Authentication (at least one required)
    api_key: str | None = Field(
        default=None,
        description="API key for authentication (starts with tp_live_ or tp_test_)",
    )
    jwt_token: str | None = Field(
        default=None,
        description="JWT token for authentication (optional, used for API key creation)",
    )

    # Server configuration
    server_url: str = Field(
        default="https://api.tradepose.com",
        description="Base URL for TradePose Gateway API",
    )

    # Request configuration
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    # Task polling configuration
    poll_interval: float = Field(
        default=2.0,
        ge=0.5,
        le=60.0,
        description="Default task polling interval in seconds",
    )
    poll_timeout: float = Field(
        default=300.0,
        ge=10.0,
        le=3600.0,
        description="Default task polling timeout in seconds",
    )

    # Logging configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        """Validate and normalize server URL."""
        v = v.strip().rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("server_url must start with http:// or https://")
        return v

    # @field_validator("api_key")
    # @classmethod
    # def validate_api_key(cls, v: str | None) -> str | None:
    #     """Validate API key format."""
    #     if v is not None:
    #         v = v.strip()
    #         if not v.startswith(("tp_live_", "tp_test_")):
    #             raise ValueError(
    #                 "api_key must start with tp_live_ or tp_test_. "
    #                 "Get your API key from the TradePose dashboard."
    #             )
    #     return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        v = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v

    def model_post_init(self, __context) -> None:
        """Validate that at least one authentication method is provided."""
        if self.api_key is None and self.jwt_token is None:
            raise ValueError(
                "At least one authentication method is required: "
                "api_key or jwt_token. Set TRADEPOSE_API_KEY or TRADEPOSE_JWT_TOKEN."
            )

    @property
    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None

    @property
    def has_jwt_token(self) -> bool:
        """Check if JWT token is configured."""
        return self.jwt_token is not None

    @property
    def primary_auth_type(self) -> str:
        """Get primary authentication type (prefers API key over JWT)."""
        if self.has_api_key:
            return "api_key"
        elif self.has_jwt_token:
            return "jwt"
        return "none"
