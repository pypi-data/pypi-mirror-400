"""
Test module for ExportResource

Test Categories:
1. create_export() - Generic export task creation
2. export_backtest_results() - Export backtest results
3. export_enhanced_ohlcv() - Export enhanced OHLCV
4. export_latest_trades() - Export latest trades
5. export_on_demand_ohlcv() - Export on-demand OHLCV
6. IndicatorSpec conversion - Dict or Pydantic model
"""

import pytest

# TODO: Import from tradepose_client.resources.export


class TestExportResource:
    """Test suite for ExportResource."""

    @pytest.mark.asyncio
    async def test_create_export_generic(self, mock_httpx_client, mock_export_response):
        """Test generic create_export."""
        # TODO: Arrange - ExportRequest
        # TODO: Act - response = await export.create_export(export_request)
        # TODO: Assert - Returns task_id
        pass

    @pytest.mark.asyncio
    async def test_export_backtest_results(self, mock_httpx_client):
        """Test exporting backtest results."""
        # TODO: Arrange - Strategy configs
        # TODO: Act - response = await export.export_backtest_results(strategy_configs, start_date, end_date)
        # TODO: Assert - export_type="backtest-results"
        pass

    @pytest.mark.asyncio
    async def test_export_enhanced_ohlcv(self, mock_httpx_client):
        """Test exporting enhanced OHLCV."""
        # TODO: Act - response = await export.export_enhanced_ohlcv(strategy_name="test")
        # TODO: Assert - export_type="enhanced-ohlcv"
        # TODO: Assert - strategy_name required
        pass

    @pytest.mark.asyncio
    async def test_export_latest_trades(self, mock_httpx_client):
        """Test exporting latest trades."""
        # TODO: Act - response = await export.export_latest_trades(limit=100)
        # TODO: Assert - export_type="latest-trades"
        # TODO: Assert - Auto-calculates start_date
        pass

    @pytest.mark.asyncio
    async def test_export_on_demand_ohlcv(self, mock_httpx_client):
        """Test exporting on-demand OHLCV."""
        # TODO: Arrange - indicator_specs list
        # TODO: Act - response = await export.export_on_demand_ohlcv(indicator_specs)
        # TODO: Assert - export_type="on-demand-ohlcv"
        pass

    @pytest.mark.asyncio
    async def test_indicator_spec_conversion(self, mock_httpx_client):
        """Test IndicatorSpec dict → Pydantic conversion."""
        # TODO: Arrange - indicator_specs as dicts
        # TODO: Act - Call export method
        # TODO: Assert - Converted to IndicatorSpec models
        pass
