"""
Test module for StrategiesResource

Test Categories:
1. register() - Register strategy (async task)
2. list() - List strategies (async task)
3. get() - Get strategy detail (async task)
4. delete() - Delete strategy (async task)
"""

import pytest

# TODO: Import from tradepose_client.resources.strategies


class TestStrategiesResource:
    """Test suite for StrategiesResource."""

    @pytest.mark.asyncio
    async def test_register_strategy(self, mock_httpx_client):
        """Test registering strategy."""
        # TODO: Arrange - Mock POST /api/v1/strategies
        # TODO: Act - response = await strategies.register(strategy_code="...", overwrite=False)
        # TODO: Assert - Returns task_id
        pass

    @pytest.mark.asyncio
    async def test_list_strategies(self, mock_httpx_client):
        """Test listing strategies."""
        # TODO: Arrange - Mock GET /api/v1/strategies
        # TODO: Act - response = await strategies.list(full=True)
        # TODO: Assert - Returns task_id for async listing
        pass

    @pytest.mark.asyncio
    async def test_get_strategy(self, mock_httpx_client):
        """Test getting strategy detail."""
        # TODO: Act - response = await strategies.get("strategy_name")
        # TODO: Assert - Returns task_id
        pass

    @pytest.mark.asyncio
    async def test_delete_strategy(self, mock_httpx_client):
        """Test deleting strategy."""
        # TODO: Act - response = await strategies.delete("strategy_name")
        # TODO: Assert - Returns task_id
        pass
