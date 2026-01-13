"""JWT authentication for TradePose Client.

This module implements JWT-based authentication using the Authorization header.
JWT tokens are typically used for initial API key creation via the Clerk integration.
"""

import httpx

from ..types import Headers


class JWTAuth(httpx.Auth):
    """JWT authentication handler for httpx.

    This authentication handler adds the JWT token to request headers
    using the Bearer token format expected by the TradePose Gateway.

    JWT authentication is primarily used for:
    - Initial API key creation
    - Administrative operations
    - Testing with Clerk-issued tokens

    Example:
        >>> auth = JWTAuth(token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
        >>> async with httpx.AsyncClient(auth=auth) as client:
        ...     response = await client.post("https://api.tradepose.com/api/v1/keys", json={"name": "My Key"})
    """

    def __init__(self, token: str) -> None:
        """Initialize JWT authentication.

        Args:
            token: JWT token (typically from Clerk)

        Raises:
            ValueError: If token is empty or invalid format
        """
        if not token or not token.strip():
            raise ValueError("JWT token cannot be empty")
        self.token = token.strip()

    def auth_flow(self, request: httpx.Request) -> httpx.Request:
        """Add JWT token to request headers.

        Args:
            request: HTTP request to authenticate

        Returns:
            Request with Authorization header added
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

    def get_headers(self) -> Headers:
        """Get authentication headers.

        Returns:
            Dictionary with Authorization header
        """
        return {"Authorization": f"Bearer {self.token}"}
