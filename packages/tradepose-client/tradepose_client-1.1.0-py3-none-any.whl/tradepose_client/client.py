"""Main client class for TradePose Client.

This module provides the primary entry point for interacting with the TradePose Gateway API.
"""

import logging
from types import TracebackType
from typing import Self

import httpx

from .auth import APIKeyAuth, JWTAuth
from .config import TradePoseConfig
from .exceptions import TradePoseConfigError
from .resources import (
    AccountsResource,
    APIKeysResource,
    BillingResource,
    BindingsResource,
    ExportResource,
    PortfoliosResource,
    StrategiesResource,
    TasksResource,
    TradesResource,
    UsageResource,
)

__version__ = "0.1.0"

logger = logging.getLogger(__name__)


class TradePoseClient:
    """Main client for TradePose Gateway API.

    This class provides a high-level interface to interact with the TradePose Gateway API.
    It handles authentication, HTTP client lifecycle, and resource initialization.

    The client supports two authentication methods:
    - API Key authentication (recommended for production)
    - JWT authentication (for initial API key creation)

    Example (API Key):
        >>> from tradepose_client import TradePoseClient
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     subscription = await client.billing.get_subscription()
        ...     print(subscription)

    Example (JWT):
        >>> async with TradePoseClient(jwt_token="eyJ...") as client:
        ...     # Create API key for long-term usage
        ...     key = await client.api_keys.create(name="Production Key")
        ...     print(f"New API key: {key.plaintext_key}")

    Example (from environment):
        >>> # Set TRADEPOSE_API_KEY in environment
        >>> async with TradePoseClient() as client:
        ...     plans = await client.billing.list_plans()
        ...     print(plans)

    Attributes:
        config: Client configuration
        version: Client library version
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        jwt_token: str | None = None,
        server_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        debug: bool | None = None,
        config: TradePoseConfig | None = None,
    ) -> None:
        """Initialize TradePose client.

        Authentication is required via either api_key or jwt_token.
        If neither is provided, they will be loaded from environment variables.

        Args:
            api_key: API key for authentication (overrides TRADEPOSE_API_KEY)
            jwt_token: JWT token for authentication (overrides TRADEPOSE_JWT_TOKEN)
            server_url: Base URL for API (overrides TRADEPOSE_SERVER_URL)
            timeout: Request timeout in seconds (overrides TRADEPOSE_TIMEOUT)
            max_retries: Max retry attempts (overrides TRADEPOSE_MAX_RETRIES)
            debug: Enable debug mode (overrides TRADEPOSE_DEBUG)
            config: Pre-configured TradePoseConfig instance (overrides all other args)

        Raises:
            TradePoseConfigError: If configuration is invalid or authentication is missing

        Example:
            >>> client = TradePoseClient(api_key="tp_live_xxx")
            >>> async with client:
            ...     # Use client
            ...     pass
        """
        # Load configuration
        if config is not None:
            self.config = config
        else:
            # Build config from explicit args + environment
            config_kwargs = {}
            if api_key is not None:
                config_kwargs["api_key"] = api_key
            if jwt_token is not None:
                config_kwargs["jwt_token"] = jwt_token
            if server_url is not None:
                config_kwargs["server_url"] = server_url
            if timeout is not None:
                config_kwargs["timeout"] = timeout
            if max_retries is not None:
                config_kwargs["max_retries"] = max_retries
            if debug is not None:
                config_kwargs["debug"] = debug

            try:
                self.config = TradePoseConfig(**config_kwargs)
            except Exception as e:
                raise TradePoseConfigError(f"Configuration error: {e}")

        # Setup logging
        self._setup_logging()

        # Version info
        self.version = __version__

        # HTTP client (initialized in __aenter__)
        self._http_client: httpx.AsyncClient | None = None

        # Resource instances (initialized in __aenter__)
        self.accounts: AccountsResource | None = None
        self.api_keys: APIKeysResource | None = None
        self.billing: BillingResource | None = None
        self.tasks: TasksResource | None = None
        self.strategies: StrategiesResource | None = None
        self.portfolios: PortfoliosResource | None = None
        self.bindings: BindingsResource | None = None
        self.trades: TradesResource | None = None
        self.export: ExportResource | None = None
        self.usage: UsageResource | None = None

        logger.info(
            f"Initialized TradePoseClient v{self.version} "
            f"(auth={self.config.primary_auth_type}, server={self.config.server_url})"
        )

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        if self.config.debug:
            # Enable httpx debug logging
            logging.getLogger("httpx").setLevel(logging.DEBUG)

    def _get_auth(self) -> httpx.Auth:
        """Get authentication handler based on config.

        Returns:
            httpx.Auth instance (APIKeyAuth or JWTAuth)

        Raises:
            TradePoseConfigError: If no authentication method is configured
        """
        if self.config.has_api_key:
            return APIKeyAuth(api_key=self.config.api_key)  # type: ignore
        elif self.config.has_jwt_token:
            return JWTAuth(token=self.config.jwt_token)  # type: ignore
        else:
            raise TradePoseConfigError(
                "No authentication method configured. Provide api_key or jwt_token."
            )

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Returns:
            Self for use in async with statement
        """
        # Initialize HTTP client
        auth = self._get_auth()

        self._http_client = httpx.AsyncClient(
            auth=auth,
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
            http2=True,  # Enable HTTP/2
            follow_redirects=True,
        )

        # Initialize resources
        self.accounts = AccountsResource(self)
        self.api_keys = APIKeysResource(self)
        self.billing = BillingResource(self)
        self.tasks = TasksResource(self)
        self.strategies = StrategiesResource(self)
        self.portfolios = PortfoliosResource(self)
        self.bindings = BindingsResource(self)
        self.trades = TradesResource(self)
        self.export = ExportResource(self)
        self.usage = UsageResource(self)

        logger.debug("TradePoseClient context entered (11 resources initialized)")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        # Close HTTP client
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

        logger.debug("TradePoseClient context exited")

    async def close(self) -> None:
        """Manually close the client.

        This is called automatically when using the async context manager,
        but can be called manually if needed.

        Example:
            >>> client = TradePoseClient(api_key="tp_live_xxx")
            >>> await client.close()
        """
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    @property
    def is_closed(self) -> bool:
        """Check if client is closed.

        Returns:
            True if client is closed, False otherwise
        """
        return self._http_client is None or self._http_client.is_closed

    def __repr__(self) -> str:
        """String representation of client.

        Returns:
            String representation
        """
        return (
            f"TradePoseClient(server={self.config.server_url}, "
            f"auth={self.config.primary_auth_type}, "
            f"closed={self.is_closed})"
        )
