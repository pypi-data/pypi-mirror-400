"""
Test module for TasksResource

Test Categories:
1. get_status() - Get task status
2. download_result() - Download result with as_dataframe option
3. download_result_by_type() - Download specific result type
4. Parquet parsing - Convert bytes to DataFrame
"""

import pytest

# TODO: Import from tradepose_client.resources.tasks
# from tradepose_client.resources.tasks import TasksResource


class TestTasksResource:
    """Test suite for TasksResource."""

    @pytest.mark.asyncio
    async def test_get_status_success(self, mock_httpx_client, mock_task_response):
        """Test get_status returns ExportTaskResponse."""
        # TODO: Arrange - Mock GET /api/v1/tasks/{task_id}
        # TODO: Act - status = await tasks.get_status("task_123")
        # TODO: Assert - Returns task metadata
        pass

    @pytest.mark.asyncio
    async def test_download_result_as_dataframe(self, mock_httpx_client, mock_parquet_data):
        """Test download_result with as_dataframe=True."""
        # TODO: Arrange - Mock GET returns Parquet bytes
        # TODO: Act - df = await tasks.download_result("task_123", as_dataframe=True)
        # TODO: Assert - Returns DataFrame (polars or pandas)
        pass

    @pytest.mark.asyncio
    async def test_download_result_as_bytes(self, mock_httpx_client, mock_parquet_data):
        """Test download_result with as_dataframe=False."""
        # TODO: Arrange - Mock response
        # TODO: Act - data = await tasks.download_result("task_123", as_dataframe=False)
        # TODO: Assert - Returns bytes
        pass

    @pytest.mark.asyncio
    async def test_download_result_by_type_trades(self, mock_httpx_client):
        """Test downloading specific result type (trades)."""
        # TODO: Act - trades = await tasks.download_result_by_type("task_123", "trades")
        # TODO: Assert - Correct endpoint called
        pass

    @pytest.mark.asyncio
    async def test_download_result_parquet_error_handling(self, mock_httpx_client):
        """Test Parquet parsing error handling."""
        # TODO: Arrange - Invalid Parquet data
        # TODO: Act & Assert - Raises SerializationError
        pass
