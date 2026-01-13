"""API Keys resource for TradePose Client.

This module provides methods for managing API keys (create, list, revoke).
"""

import logging

from tradepose_models.auth import (
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyListResponse,
)

from .base import BaseResource

logger = logging.getLogger(__name__)


class APIKeysResource(BaseResource):
    """API Keys management resource.

    This resource provides methods to manage API keys for authentication.
    API keys can be created, listed, and revoked.

    Note: API key creation requires JWT authentication. Once created, the
    API key can be used for all subsequent requests.

    Example:
        >>> async with TradePoseClient(jwt_token="eyJ...") as client:
        ...     # Create a new API key
        ...     key = await client.api_keys.create(name="Production Key")
        ...     print(f"New API key: {key.api_key}")  # Save this!
        ...
        ...     # List all keys
        ...     keys = await client.api_keys.list()
        ...     for k in keys.keys:
        ...         print(f"{k.name}: {k.created_at}")
        ...
        ...     # Revoke a key
        ...     await client.api_keys.revoke(key_id=key.id)
    """

    async def create(self, name: str) -> APIKeyCreateResponse:
        """Create a new API key.

        This endpoint requires JWT authentication (not API key auth).
        The plaintext API key is returned ONCE in the response.
        Save it securely - it cannot be retrieved later.

        Args:
            name: Human-readable name for the API key (1-100 characters)

        Returns:
            APIKeyCreateResponse with plaintext key (one-time only)

        Raises:
            AuthenticationError: If JWT token is invalid
            ValidationError: If name is invalid
            TradePoseAPIError: For other API errors

        Example:
            >>> key = await client.api_keys.create(name="Production Key")
            >>> print(f"API Key: {key.api_key}")  # Save this!
            >>> print(f"Key ID: {key.id}")
        """
        logger.info(f"Creating API key: {name}")

        request = APIKeyCreate(name=name)
        response = await self._post(
            "/api/v1/keys",
            json=request,
        )

        result = APIKeyCreateResponse(**response)
        logger.info(f"API key created: {result.id}")
        return result

    async def list(self) -> APIKeyListResponse:
        """List all API keys for the authenticated user.

        Returns all API keys (both active and revoked) without plaintext keys.
        The plaintext key is only shown once during creation.

        Returns:
            APIKeyListResponse with list of keys and total count

        Raises:
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> keys = await client.api_keys.list()
            >>> print(f"Total keys: {keys.total}")
            >>> for key in keys.keys:
            ...     status = "revoked" if key.revoked else "active"
            ...     print(f"{key.name}: {status} (created: {key.created_at})")
        """
        logger.debug("Listing API keys")

        response = await self._get("/api/v1/keys")

        result = APIKeyListResponse(**response)
        logger.info(f"Listed {result.total} API keys")
        return result

    async def revoke(self, key_id: str) -> None:
        """Revoke an API key.

        Once revoked, the API key can no longer be used for authentication.
        This action cannot be undone.

        Args:
            key_id: UUID of the API key to revoke

        Raises:
            ResourceNotFoundError: If key_id not found
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> await client.api_keys.revoke(key_id="123e4567-e89b-12d3-a456-426614174000")
            >>> print("API key revoked successfully")
        """
        logger.info(f"Revoking API key: {key_id}")

        await self._delete(f"/api/v1/keys/{key_id}")

        logger.info(f"API key revoked: {key_id}")
