"""Export resource for TradePose Client.

This module provides methods for exporting backtest results, OHLCV data, and trade information.
"""

import logging

from tradepose_models.enums import PersistMode
from tradepose_models.export import ExportRequest, ExportResponse
from tradepose_models.strategy import IndicatorSpec

from .base import BaseResource

logger = logging.getLogger(__name__)


class ExportResource(BaseResource):
    """Export and backtest resource.

    This resource provides methods to export various types of trading data including
    backtest results, enhanced OHLCV, latest trades, and on-demand OHLCV with custom indicators.

    All export operations are asynchronous and return task IDs for polling.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Export backtest results
        ...     response = await client.export.export_backtest_results(
        ...         symbol="BTCUSDT",
        ...         timeframe="1h",
        ...         start_date="2024-01-01",
        ...         end_date="2024-12-31",
        ...         strategy_names=["my_strategy"]
        ...     )
        ...     task_id = response.task_id
        ...
        ...     # Poll for completion
        ...     status = await client.tasks.get_status(task_id)
        ...     while status.status == "RUNNING":
        ...         await asyncio.sleep(5)
        ...         status = await client.tasks.get_status(task_id)
        ...
        ...     # Download results
        ...     trades = await client.tasks.download_result_by_type(
        ...         task_id,
        ...         result_type="trades"
        ...     )
    """

    async def create_export(
        self,
        request: ExportRequest,
    ) -> ExportResponse:
        """Create a generic export task.

        This is a low-level method that accepts a complete ExportRequest.
        For most use cases, use the specific export methods instead.

        Args:
            request: Complete export request with all required fields

        Returns:
            ExportResponse with task_id for polling

        Raises:
            ValidationError: If request is invalid
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> request = ExportRequest(
            ...     symbol="BTCUSDT",
            ...     timeframe="1h",
            ...     export_type="backtest-results",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ...     strategy_names=["strategy1", "strategy2"]
            ... )
            >>> response = await client.export.create_export(request)
            >>> print(f"Task ID: {response.task_id}")
        """
        logger.info(f"Creating export task: {request.export_type}")

        response_data = await self._post(
            "/api/v1/export",
            json=request,
        )

        result = ExportResponse(**response_data)
        logger.info(f"Export task created: {result.task_id} ({result.operation_type})")
        return result

    async def export_backtest_results(
        self,
        start_date: str,
        end_date: str,
        strategy_configs: list[dict] | list,
        strategy_ids: list[str] | None = None,
        persist_mode: PersistMode = PersistMode.REDIS,
    ) -> ExportResponse:
        """Export backtest results (trades + performance).

        Returns trades DataFrame and performance metrics for the specified strategies.
        This is the primary method for running backtests.

        Args:
            start_date: Start date in ISO 8601 format (YYYY-MM-DD)
            end_date: End date in ISO 8601 format (YYYY-MM-DD)
            strategy_configs: List of StrategyConfig objects (can be StrategyConfig instances or dicts)
            strategy_ids: Optional list of strategy IDs to execute (None = execute all)
            persist_mode: Where to persist results (REDIS or PSQL for dual-write)

        Returns:
            ExportResponse with task_id for polling

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> from tradepose_client import StrategyBuilder
            >>> from tradepose_models.enums import Freq, IndicatorType
            >>>
            >>> # Build strategy using StrategyBuilder
            >>> builder = StrategyBuilder(
            ...     name="my_strategy",
            ...     base_instrument="BTCUSDT",
            ...     base_freq=Freq.HOUR_1
            ... )
            >>> atr = builder.add_indicator(IndicatorType.ATR, period=14, freq=Freq.DAY_1, shift=1)
            >>> # ... add blueprints ...
            >>> strategy = builder.build(volatility_indicator=atr)
            >>>
            >>> # Run backtest with strategy config
            >>> response = await client.export.export_backtest_results(
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ...     strategy_configs=[strategy]  # Pass StrategyConfig directly
            ... )
            >>>
            >>> # Poll for completion
            >>> status = await client.tasks.get_status(response.task_id)
            >>> while status.status in ["PENDING", "RUNNING"]:
            ...     await asyncio.sleep(5)
            ...     status = await client.tasks.get_status(response.task_id)
            >>>
            >>> # Download results (single call returns both DataFrames)
            >>> trades_df, perf_df = await client.tasks.download_backtest_results(response.task_id)
            >>>
            >>> # Analyze results
            >>> total_pnl = trades_df["pnl"].sum()
            >>> win_rate = (trades_df["pnl"] > 0).mean() * 100
            >>> print(f"Total PnL: ${total_pnl:.2f}")
            >>> print(f"Win Rate: {win_rate:.1f}%")
            >>> print(f"Performance metrics: {perf_df.columns}")
        """
        # Convert StrategyConfig objects to dicts
        strategy_config_dicts = []
        for config in strategy_configs:
            if isinstance(config, dict):
                strategy_config_dicts.append(config)
            else:
                # Assume it's a StrategyConfig (Pydantic model)
                strategy_config_dicts.append(config.model_dump(mode="json", exclude_none=True))

        logger.info(
            f"Exporting backtest results: {start_date} to {end_date} "
            f"({len(strategy_config_dicts)} strategies)"
        )

        from tradepose_models.enums import ExportType

        request = ExportRequest(
            strategy_configs=strategy_config_dicts,
            export_type=ExportType.BACKTEST_RESULTS,
            start_date=start_date,
            end_date=end_date,
            strategy_ids=strategy_ids,
            persist_mode=persist_mode,
        )

        return await self.create_export(request)

    async def export_enhanced_ohlcv(
        self,
        start_date: str,
        end_date: str,
        strategy_configs: list[dict] | list,
        strategy_name: str | None = None,
        blueprint_name: str | None = None,
        persist_mode: PersistMode = PersistMode.REDIS,
    ) -> ExportResponse:
        """Export enhanced OHLCV with strategy indicators and signals.

        Returns OHLCV data with all strategy indicators, signals, and trading context.
        Useful for analyzing strategy behavior and visualizing signals.

        Args:
            start_date: Start date in ISO 8601 format (YYYY-MM-DD)
            end_date: End date in ISO 8601 format (YYYY-MM-DD)
            strategy_configs: List of StrategyConfig objects (can be StrategyConfig instances or dicts)
            strategy_name: Optional strategy name to filter (default: first strategy in list)
            blueprint_name: Optional blueprint name to filter (default: base blueprint)
            persist_mode: Where to persist results (REDIS or PSQL for dual-write)

        Returns:
            ExportResponse with task_id for polling

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Export enhanced OHLCV for strategy analysis
            >>> response = await client.export.export_enhanced_ohlcv(
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ...     strategy_configs=[my_strategy],
            ...     strategy_name="my_strategy",
            ...     blueprint_name="base"
            ... )
            >>>
            >>> # Poll for completion
            >>> status = await client.tasks.get_status(response.task_id)
            >>> while status.status in ["PENDING", "RUNNING"]:
            ...     await asyncio.sleep(5)
            ...     status = await client.tasks.get_status(response.task_id)
            >>>
            >>> # Download enhanced OHLCV
            >>> ohlcv = await client.tasks.download_enhanced_ohlcv(response.task_id)
            >>>
            >>> # Analyze indicators and signals
            >>> print(f"Columns: {ohlcv.columns}")
            >>> print(f"Shape: {ohlcv.shape}")
        """
        # Convert StrategyConfig objects to dicts
        strategy_config_dicts = []
        for config in strategy_configs:
            if isinstance(config, dict):
                strategy_config_dicts.append(config)
            else:
                strategy_config_dicts.append(config.model_dump(mode="json", exclude_none=True))

        logger.info(
            f"Exporting enhanced OHLCV: {start_date} to {end_date} "
            f"(strategy={strategy_name}, blueprint={blueprint_name})"
        )

        from tradepose_models.enums import ExportType

        request = ExportRequest(
            strategy_configs=strategy_config_dicts,
            export_type=ExportType.ENHANCED_OHLCV,
            start_date=start_date,
            end_date=end_date,
            strategy_name=strategy_name,
            blueprint_name=blueprint_name,
            persist_mode=persist_mode,
        )

        return await self.create_export(request)

    async def export_latest_trades(
        self,
        strategy_configs: list[dict] | list,
        start_date: str | None = None,
        strategy_ids: list[str] | None = None,
        persist_mode: PersistMode = PersistMode.REDIS,
    ) -> ExportResponse:
        """Export latest trade states for strategies.

        Returns the most recent trade information for specified strategies.
        Useful for monitoring current positions and recent trade activity.

        Args:
            strategy_configs: List of StrategyConfig objects (can be StrategyConfig instances or dicts)
            start_date: Optional start date (defaults to current date)
            strategy_ids: Optional list of strategy IDs to filter
            persist_mode: Where to persist results (REDIS or PSQL for dual-write)

        Returns:
            ExportResponse with task_id for polling

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Get latest trades for monitoring
            >>> response = await client.export.export_latest_trades(
            ...     strategy_configs=[strategy1, strategy2],
            ...     strategy_ids=["strategy1_id"]
            ... )
            >>>
            >>> # Poll for completion
            >>> status = await client.tasks.get_status(response.task_id)
            >>> while status.status in ["PENDING", "RUNNING"]:
            ...     await asyncio.sleep(2)
            ...     status = await client.tasks.get_status(response.task_id)
            >>>
            >>> # Download latest trades (JSON format)
            >>> trades = await client.tasks.download_latest_trades(response.task_id)
            >>>
            >>> # Check current positions
            >>> for trade in trades["trades"]:
            ...     print(f"{trade['strategy']}: {trade['status']}")
        """
        # Convert StrategyConfig objects to dicts
        strategy_config_dicts = []
        for config in strategy_configs:
            if isinstance(config, dict):
                strategy_config_dicts.append(config)
            else:
                strategy_config_dicts.append(config.model_dump(mode="json", exclude_none=True))

        # Use current date if not specified
        if start_date is None:
            from datetime import datetime

            start_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(
            f"Exporting latest trades: {start_date} ({len(strategy_config_dicts)} strategies)"
        )

        from tradepose_models.enums import ExportType

        request = ExportRequest(
            strategy_configs=strategy_config_dicts,
            export_type=ExportType.LATEST_TRADES,
            start_date=start_date,
            strategy_ids=strategy_ids,
            persist_mode=persist_mode,
        )

        return await self.create_export(request)

    async def export_on_demand_ohlcv(
        self,
        base_instrument: str,
        base_freq: str,
        start_date: str,
        end_date: str,
        indicator_specs: list[IndicatorSpec] | list[dict],
        persist_mode: PersistMode = PersistMode.REDIS,
    ) -> ExportResponse:
        """Export OHLCV with custom indicators.

        Returns OHLCV data with user-specified indicators without requiring a strategy.
        Useful for exploratory analysis and custom indicator combinations.

        Args:
            base_instrument: Instrument ID (e.g., "BTCUSDT")
            base_freq: Base frequency (e.g., "1h", "4h", "1d")
            start_date: Start date in ISO 8601 format (YYYY-MM-DD)
            end_date: End date in ISO 8601 format (YYYY-MM-DD)
            indicator_specs: List of indicator specifications (IndicatorSpec or dict)
            persist_mode: Where to persist results (REDIS or PSQL for dual-write)

        Returns:
            ExportResponse with task_id for polling

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> from tradepose_models.indicators import Indicator
            >>>
            >>> # Define custom indicators
            >>> indicators = [
            ...     Indicator.sma(period=20),
            ...     Indicator.ema(period=50),
            ...     Indicator.rsi(period=14),
            ...     Indicator.atr(period=14, quantile=0.618),
            ...     Indicator.supertrend(atr_period=10, atr_multiplier=3.0),
            ... ]
            >>>
            >>> # Export with custom indicators
            >>> response = await client.export.export_on_demand_ohlcv(
            ...     base_instrument="BTCUSDT",
            ...     base_freq="1h",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ...     indicator_specs=indicators
            ... )
            >>>
            >>> # Poll for completion
            >>> status = await client.tasks.get_status(response.task_id)
            >>> while status.status in ["PENDING", "RUNNING"]:
            ...     await asyncio.sleep(5)
            ...     status = await client.tasks.get_status(response.task_id)
            >>>
            >>> # Download OHLCV with indicators
            >>> ohlcv = await client.tasks.download_on_demand_ohlcv(response.task_id)
            >>>
            >>> # Analyze custom indicators
            >>> print(f"Columns: {ohlcv.columns}")
            >>> print(f"SMA_20: {ohlcv['sma_20'].tail()}")
        """
        logger.info(
            f"Exporting on-demand OHLCV: {base_instrument} {base_freq} "
            f"({len(indicator_specs)} indicators)"
        )

        # Convert IndicatorSpec objects to dicts
        indicator_dicts = []
        for spec in indicator_specs:
            if isinstance(spec, dict):
                indicator_dicts.append(spec)
            else:
                # Assume it's an IndicatorSpec (Pydantic model)
                indicator_dicts.append(spec.model_dump(mode="json", exclude_none=True))

        from tradepose_models.enums import ExportType

        # For on-demand OHLCV, we create a minimal strategy config with only indicators
        # This allows the worker to process the request without a full strategy definition
        # Note: Worker requires a valid base_blueprint, so we provide a dummy one
        # Use PascalCase enum values to match Rust worker expectations
        dummy_blueprint = {
            "name": "_ohlcv_export_dummy",
            "direction": "Long",
            "trend_type": "Trend",
            "entry_first": True,
            "note": "Dummy blueprint for OHLCV export (not used)",
            "entry_triggers": [],
            "exit_triggers": [],
        }

        minimal_strategy = {
            "name": f"on_demand_{base_instrument}_{base_freq}",
            "base_instrument": base_instrument,
            "base_freq": base_freq,
            "note": "On-demand OHLCV export (auto-generated)",
            "indicators": indicator_dicts,
            "base_blueprint": dummy_blueprint,
            "advanced_blueprints": [],
            "volatility_indicator": None,
        }

        request = ExportRequest(
            strategy_configs=[minimal_strategy],
            export_type=ExportType.ON_DEMAND_OHLCV,
            start_date=start_date,
            end_date=end_date,
            base_instrument=base_instrument,
            base_freq=base_freq,
            indicator_specs=indicator_dicts,
            persist_mode=persist_mode,
        )

        return await self.create_export(request)
