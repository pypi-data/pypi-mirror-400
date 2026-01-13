"""
Test module for APIKeysResource

Test Categories:
1. create() - Create new API key (returns plaintext once)
2. list() - List all API keys for user
3. revoke() - Revoke API key
4. JWT requirement - create() requires JWT, not API key
"""

import pytest

# TODO: Import from tradepose_client.resources.api_keys


class TestAPIKeysResource:
    """Test suite for APIKeysResource."""

    @pytest.mark.asyncio
    async def test_create_api_key(self, mock_httpx_client, mock_api_key_response):
        """Test creating API key."""
        # TODO: Arrange - Mock POST /api/v1/keys
        # TODO: Act - key_response = await api_keys.create(name="Test Key")
        # TODO: Assert - Returns plaintext key
        # TODO: Assert - Returns key_preview
        pass

    @pytest.mark.asyncio
    async def test_list_api_keys(self, mock_httpx_client):
        """Test listing API keys."""
        # TODO: Arrange - Mock GET /api/v1/keys
        # TODO: Act - keys = await api_keys.list()
        # TODO: Assert - Returns list of keys (no hashes)
        pass

    @pytest.mark.asyncio
    async def test_revoke_api_key(self, mock_httpx_client):
        """Test revoking API key."""
        # TODO: Arrange - Mock DELETE /api/v1/keys/{key_id}
        # TODO: Act - await api_keys.revoke("key_123")
        # TODO: Assert - Returns None (204)
        pass

    @pytest.mark.asyncio
    async def test_create_requires_jwt(self, mock_httpx_client):
        """Test create() validates JWT authentication."""
        # TODO: If using API key auth, should raise error or warn
        pass
