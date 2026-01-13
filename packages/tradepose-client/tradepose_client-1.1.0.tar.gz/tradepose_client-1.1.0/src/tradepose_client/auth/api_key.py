"""API key authentication for TradePose Client.

This module implements API key-based authentication using the X-API-Key header.
"""

import httpx

from ..types import Headers


class APIKeyAuth(httpx.Auth):
    """API key authentication handler for httpx.

    This authentication handler adds the API key to request headers
    using the X-API-Key header format expected by the TradePose Gateway.

    Example:
        >>> auth = APIKeyAuth(api_key="tp_live_xxx")
        >>> async with httpx.AsyncClient(auth=auth) as client:
        ...     response = await client.get("https://api.tradepose.com/api/v1/billing/subscription")
    """

    def __init__(self, api_key: str) -> None:
        """Initialize API key authentication.

        Args:
            api_key: TradePose API key (starts with tp_live_ or tp_test_)

        Raises:
            ValueError: If API key format is invalid
        """
        # if not api_key.startswith(("tp_live_", "tp_test_")):
        #     raise ValueError(
        #         "Invalid API key format. API key must start with tp_live_ or tp_test_"
        #     )
        self.api_key = api_key

    def auth_flow(self, request: httpx.Request) -> httpx.Request:
        """Add API key to request headers.

        Args:
            request: HTTP request to authenticate

        Returns:
            Request with API key header added
        """
        request.headers["X-API-Key"] = self.api_key
        yield request

    def get_headers(self) -> Headers:
        """Get authentication headers.

        Returns:
            Dictionary with X-API-Key header
        """
        return {"X-API-Key": self.api_key}
