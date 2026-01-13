"""Batch testing API - main entry point."""

import asyncio
import logging
import threading
from typing import Any

import polars as pl
from tradepose_models.enums import PersistMode
from tradepose_models.strategy.config import StrategyConfig
from tradepose_models.strategy.indicator_spec import IndicatorSpec

from tradepose_client.batch.background import (
    BackgroundPoller,
    EnhancedOhlcvBackgroundPoller,
    OHLCVBackgroundPoller,
)
from tradepose_client.batch.cache import ResultCache
from tradepose_client.batch.models import BacktestRequest, Period
from tradepose_client.batch.results import (
    BatchResults,
    EnhancedOhlcvPeriodResult,
    EnhancedOhlcvResults,
    OHLCVPeriodResult,
    OHLCVResults,
)
from tradepose_client.utils import setup_jupyter_support

logger = logging.getLogger(__name__)


class BatchTester:
    """
    Batch backtest testing API.

    Simplifies multi-strategy, multi-period backtesting by handling:
    - Parallel task submission
    - Background status polling
    - Automatic result downloading
    - Memory caching

    Example:
        >>> from tradepose_client.batch import Period
        >>> tester = BatchTester(api_key="sk_xxx")
        >>> batch = tester.submit(
        ...     strategies=[strategy1, strategy2],
        ...     periods=[Period.Q1(2024), Period.Q2(2024)]
        ... )
        >>> batch.wait()  # Block until complete
        >>> print(batch.summary())
    """

    def __init__(
        self,
        api_key: str,
        server_url: str = "https://api.tradepose.com",
        poll_interval: float = 2.0,
        auto_download: bool = True,
    ):
        """
        Initialize batch tester.

        Args:
            api_key: API key for authentication
            server_url: Gateway server URL
            poll_interval: Status polling interval in seconds (default: 2.0)
            auto_download: Auto-download completed results (default: True)

        Note:
            Jupyter support is automatically enabled. No manual setup required.
        """
        self._api_key = api_key
        self._server_url = server_url
        self._poll_interval = poll_interval
        self._auto_download = auto_download

        # Auto-detect and setup Jupyter support (user-transparent)
        setup_jupyter_support()

    def submit(
        self,
        strategies: list[StrategyConfig],
        periods: list[Period],
        cache: bool = True,
        persist_mode: PersistMode = PersistMode.REDIS,
    ) -> BatchResults:
        """
        Submit batch backtest tasks.

        Creates one task per period, each task tests all strategies.
        Returns immediately (non-blocking), background polling starts automatically.

        Args:
            strategies: List of strategy configurations to test
            periods: List of Period objects defining test ranges
            cache: Enable result caching (default: True)
            persist_mode: Where to persist results (REDIS or PSQL for dual-write)

        Returns:
            BatchResults object (updates automatically in background)

        Example:
            >>> from tradepose_client.batch import Period
            >>> batch = tester.submit(
            ...     strategies=[strategy1, strategy2],
            ...     periods=[Period.Q1(2024), Period.Q2(2024)]
            ... )
            >>> print(batch.status)  # Check progress
            >>> batch.wait()  # Wait for completion

        Note:
            Period objects provide type-safe date validation and convenient constructors:
            - Period.Q1(2024), Period.Q2(2024), etc. for quarters
            - Period.from_year(2024) for full year
            - Period.from_month(2024, 3) for single month
            - Period(start="2024-01-01", end="2024-12-31") for custom ranges
        """
        # Validate input - periods must be Period objects
        request = BacktestRequest(strategies=strategies, periods=periods, cache=cache)

        # Submit tasks in background thread
        task_metadata = self._submit_all_tasks(request, persist_mode)

        # Create results container
        result_cache = ResultCache() if cache else None
        results = BatchResults(
            task_metadata=task_metadata,
            strategies=strategies,
            tester=self,
            cache=result_cache,
        )

        # Start background poller
        poller = BackgroundPoller(
            results=results,
            client_config={"api_key": self._api_key, "server_url": self._server_url},
            poll_interval=self._poll_interval,
            auto_download=self._auto_download,
        )
        poller.start()

        logger.info(
            f"Submitted {len(task_metadata)} batch tasks "
            f"({len(strategies)} strategies × {len(periods)} periods)"
        )

        return results

    def _submit_all_tasks(
        self, request: BacktestRequest, persist_mode: PersistMode
    ) -> list[dict[str, Any]]:
        """
        Submit all tasks in parallel.

        Runs in separate thread to avoid blocking main thread.

        Args:
            request: Validated backtest request
            persist_mode: Where to persist results

        Returns:
            List of task metadata dicts
        """
        result_container = []

        def _run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                metadata = loop.run_until_complete(self._async_submit_all(request, persist_mode))
                result_container.append(metadata)
            finally:
                loop.close()

        thread = threading.Thread(target=_run_in_thread)
        thread.start()
        thread.join()  # Wait for submission to complete

        return result_container[0] if result_container else []

    async def _async_submit_all(
        self, request: BacktestRequest, persist_mode: PersistMode
    ) -> list[dict[str, Any]]:
        """
        Submit all tasks concurrently using asyncio.gather.

        Args:
            request: Validated backtest request
            persist_mode: Where to persist results

        Returns:
            List of task metadata dicts with task_id, period, status
        """
        from tradepose_client import TradePoseClient

        async with TradePoseClient(api_key=self._api_key, server_url=self._server_url) as client:
            # Create submission tasks
            submission_tasks = []
            for period in request.periods:
                start, end = period.to_iso()
                submission_tasks.append(
                    client.export.export_backtest_results(
                        start_date=start,
                        end_date=end,
                        strategy_configs=request.strategies,
                        persist_mode=persist_mode,
                    )
                )

            # Submit all concurrently
            responses = await asyncio.gather(*submission_tasks, return_exceptions=True)

            # Process responses
            metadata = []
            for period, response in zip(request.periods, responses):
                if isinstance(response, Exception):
                    # Submission failed
                    logger.error(f"Failed to submit task for period {period}: {response}")
                    metadata.append(
                        {
                            "task_id": None,
                            "period": period,
                            "status": "failed",
                            "error": str(response),
                        }
                    )
                else:
                    # Submission succeeded
                    metadata.append(
                        {
                            "task_id": str(response.task_id),
                            "period": period,
                            "status": "pending",
                            "error": None,
                        }
                    )

            logger.info(
                f"Submitted {len(metadata)} tasks "
                f"(successful: {sum(1 for m in metadata if m['task_id'] is not None)})"
            )

            return metadata

    async def _async_download_results(
        self, task_id: str
    ) -> tuple[pl.DataFrame | None, pl.DataFrame | None]:
        """
        Download backtest results (trades + performance) for a task.

        Uses client.tasks.download_result_by_type() to download trades and
        performance separately as Parquet DataFrames.

        Args:
            task_id: Task identifier

        Returns:
            Tuple of (trades_df, performance_df) or (None, None) if failed
        """
        from tradepose_client import TradePoseClient

        try:
            async with TradePoseClient(
                api_key=self._api_key, server_url=self._server_url
            ) as client:
                # Download both results separately (gateway doesn't support ZIP yet)
                trades_df = await client.tasks.download_result_by_type(task_id, "trades")
                perf_df = await client.tasks.download_result_by_type(task_id, "performance")
                return (trades_df, perf_df)
        except Exception as e:
            logger.error(f"Failed to download results for task {task_id}: {e}")
            return (None, None)

    # =========================================================================
    # OHLCV Export Methods
    # =========================================================================

    def submit_ohlcv(
        self,
        strategy: StrategyConfig,
        period: Period,
        timeout: float | None = None,
    ) -> OHLCVPeriodResult:
        """
        Submit on-demand OHLCV export task (non-blocking).

        Extracts base_instrument, base_freq, and all indicators from the strategy,
        submits a single task, and returns immediately.
        Background polling and downloading happens automatically.

        Args:
            strategy: Strategy configuration to extract indicators from
            period: Time period to fetch OHLCV for
            timeout: Maximum polling time in seconds (None = no limit)

        Returns:
            OHLCVPeriodResult (updates automatically in background)

        Raises:
            ValueError: If strategy has no indicators
            RuntimeError: If task submission fails

        Example:
            >>> from tradepose_client.batch import BatchTester, Period
            >>> tester = BatchTester(api_key="sk_xxx")
            >>> result = tester.submit_ohlcv(
            ...     strategy=my_strategy,
            ...     period=Period.Q1(2024),
            ...     timeout=60,  # Stop polling after 60 seconds
            ... )
            >>>
            >>> # Returns immediately - check progress
            >>> print(result.status)
            >>>
            >>> # Access data when complete
            >>> print(result.df)
        """
        # 1. Extract indicators from strategy
        indicators = self._extract_indicators(strategy)

        logger.info(
            f"Submitting OHLCV export: {strategy.base_instrument} {strategy.base_freq} "
            f"({len(indicators)} indicators)"
        )

        # 2. Submit task (blocking, but fast)
        task_metadata = self._submit_ohlcv_tasks(strategy, [period], indicators)

        if not task_metadata or not task_metadata[0]["task_id"]:
            error_msg = task_metadata[0]["error"] if task_metadata else "Unknown error"
            raise RuntimeError(f"OHLCV task submission failed: {error_msg}")

        # 3. Create OHLCVResults container (internal use)
        results = OHLCVResults(task_metadata=task_metadata, periods=[period])

        # 4. Start background poller (non-blocking)
        poller = OHLCVBackgroundPoller(
            results=results,
            client_config={"api_key": self._api_key, "server_url": self._server_url},
            poll_interval=self._poll_interval,
            timeout=timeout,
        )
        poller.start()

        logger.info(f"Submitted OHLCV task: {task_metadata[0]['task_id']}")

        # 5. Return the single OHLCVPeriodResult
        return results._period_results[period.to_key()]

    def _extract_indicators(self, strategy: StrategyConfig) -> list[IndicatorSpec]:
        """
        Extract all indicators from strategy config.

        Args:
            strategy: Strategy configuration

        Returns:
            List of IndicatorSpec objects

        Raises:
            ValueError: If strategy has no indicators
        """
        indicators = list(strategy.indicators)  # Copy list

        # Note: volatility_indicator is Optional[pl.Expr] (column reference),
        # not an IndicatorSpec. The volatility column should be produced by
        # an indicator already in the indicators list.

        if not indicators:
            raise ValueError(
                f"Strategy '{strategy.name}' has no indicators. "
                "Add indicators to the strategy or use volatility_indicator."
            )

        return indicators

    def _submit_ohlcv_tasks(
        self,
        strategy: StrategyConfig,
        periods: list[Period],
        indicators: list[IndicatorSpec],
    ) -> list[dict[str, Any]]:
        """
        Submit all OHLCV export tasks in separate thread.

        Args:
            strategy: Strategy configuration
            periods: List of time periods
            indicators: List of indicators to export

        Returns:
            List of task metadata dicts
        """
        result_container: list[list[dict[str, Any]]] = []

        def _run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                metadata = loop.run_until_complete(
                    self._async_submit_ohlcv_tasks(strategy, periods, indicators)
                )
                result_container.append(metadata)
            finally:
                loop.close()

        thread = threading.Thread(target=_run_in_thread)
        thread.start()
        thread.join()

        return result_container[0] if result_container else []

    async def _async_submit_ohlcv_tasks(
        self,
        strategy: StrategyConfig,
        periods: list[Period],
        indicators: list[IndicatorSpec],
    ) -> list[dict[str, Any]]:
        """
        Submit all OHLCV export tasks concurrently.

        Args:
            strategy: Strategy configuration
            periods: List of time periods
            indicators: List of indicators to export

        Returns:
            List of task metadata dicts with task_id, period, status
        """
        from tradepose_client import TradePoseClient

        async with TradePoseClient(api_key=self._api_key, server_url=self._server_url) as client:
            # Create submission tasks for all periods
            submission_tasks = []
            for period in periods:
                start, end = period.to_iso()
                submission_tasks.append(
                    client.export.export_on_demand_ohlcv(
                        base_instrument=strategy.base_instrument,
                        base_freq=strategy.base_freq,
                        start_date=start,
                        end_date=end,
                        indicator_specs=indicators,
                    )
                )

            # Submit all concurrently
            responses = await asyncio.gather(*submission_tasks, return_exceptions=True)

            # Build metadata list
            metadata = []
            for period, response in zip(periods, responses):
                if isinstance(response, Exception):
                    logger.error(f"Failed to submit OHLCV task for {period}: {response}")
                    metadata.append(
                        {
                            "task_id": None,
                            "period": period,
                            "status": "failed",
                            "error": str(response),
                        }
                    )
                else:
                    metadata.append(
                        {
                            "task_id": str(response.task_id),
                            "period": period,
                            "status": "pending",
                            "error": None,
                        }
                    )

            logger.info(
                f"Submitted {len(metadata)} OHLCV tasks "
                f"(successful: {sum(1 for m in metadata if m['task_id'] is not None)})"
            )

            return metadata

    # =========================================================================
    # Enhanced OHLCV Export Methods (ENHANCED_OHLCV = 2)
    # =========================================================================

    def submit_enhanced_ohlcv(
        self,
        strategy: StrategyConfig,
        period: Period,
        strategy_name: str | None = None,
        blueprint_name: str | None = None,
        timeout: float | None = None,
    ) -> EnhancedOhlcvPeriodResult:
        """
        Submit enhanced OHLCV export task (non-blocking).

        Unlike submit_ohlcv() which uses ON_DEMAND_OHLCV (export_type=3),
        this uses ENHANCED_OHLCV (export_type=2) which requires a registered
        strategy and returns OHLCV data with complete strategy signals,
        indicators, and trading context.

        Args:
            strategy: StrategyConfig object (must contain strategy definition)
            period: Time period for the export
            strategy_name: Optional strategy name filter (default: strategy.name)
            blueprint_name: Optional blueprint name filter (default: base blueprint)
            timeout: Maximum polling time in seconds (None = no limit)

        Returns:
            EnhancedOhlcvPeriodResult (updates automatically in background)

        Raises:
            RuntimeError: If task submission fails

        Example:
            >>> from tradepose_client.batch import BatchTester, Period
            >>> tester = BatchTester(api_key="sk_xxx")
            >>> result = tester.submit_enhanced_ohlcv(
            ...     strategy=my_strategy,
            ...     period=Period.Q1(2024),
            ...     strategy_name="VA_Breakout",
            ...     blueprint_name="va_breakout_long",
            ...     timeout=60,
            ... )
            >>>
            >>> # Returns immediately - check progress
            >>> print(result.status)
            >>>
            >>> # Access data when complete (includes signals and trading context)
            >>> print(result.df)
        """
        # Use strategy.name as default strategy_name
        if strategy_name is None:
            strategy_name = strategy.name

        logger.info(f"Submitting Enhanced OHLCV export: {strategy.name} ({period.to_key()})")

        # Submit task (blocking, but fast)
        task_metadata = self._submit_enhanced_ohlcv_task(
            strategy=strategy,
            period=period,
            strategy_name=strategy_name,
            blueprint_name=blueprint_name,
        )

        if not task_metadata or not task_metadata[0]["task_id"]:
            error_msg = task_metadata[0]["error"] if task_metadata else "Unknown error"
            raise RuntimeError(f"Enhanced OHLCV task submission failed: {error_msg}")

        # Create EnhancedOhlcvResults container (internal use)
        results = EnhancedOhlcvResults(task_metadata=task_metadata, periods=[period])

        # Start background poller (non-blocking)
        poller = EnhancedOhlcvBackgroundPoller(
            results=results,
            client_config={"api_key": self._api_key, "server_url": self._server_url},
            poll_interval=self._poll_interval,
            timeout=timeout,
        )
        poller.start()

        logger.info(f"Submitted Enhanced OHLCV task: {task_metadata[0]['task_id']}")

        # Return the single EnhancedOhlcvPeriodResult
        return results._period_results[period.to_key()]

    def _submit_enhanced_ohlcv_task(
        self,
        strategy: StrategyConfig,
        period: Period,
        strategy_name: str,
        blueprint_name: str | None,
    ) -> list[dict[str, Any]]:
        """
        Submit enhanced OHLCV task in separate thread.

        Args:
            strategy: Strategy configuration
            period: Time period
            strategy_name: Strategy name to filter
            blueprint_name: Blueprint name to filter (optional)

        Returns:
            List of task metadata dicts
        """
        result_container: list[list[dict[str, Any]]] = []

        def _run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                metadata = loop.run_until_complete(
                    self._async_submit_enhanced_ohlcv_task(
                        strategy, period, strategy_name, blueprint_name
                    )
                )
                result_container.append(metadata)
            finally:
                loop.close()

        thread = threading.Thread(target=_run_in_thread)
        thread.start()
        thread.join()

        return result_container[0] if result_container else []

    async def _async_submit_enhanced_ohlcv_task(
        self,
        strategy: StrategyConfig,
        period: Period,
        strategy_name: str,
        blueprint_name: str | None,
    ) -> list[dict[str, Any]]:
        """
        Submit enhanced OHLCV export task.

        Args:
            strategy: Strategy configuration
            period: Time period
            strategy_name: Strategy name to filter
            blueprint_name: Blueprint name to filter (optional)

        Returns:
            List of task metadata dicts with task_id, period, status
        """
        from tradepose_client import TradePoseClient

        async with TradePoseClient(api_key=self._api_key, server_url=self._server_url) as client:
            start, end = period.to_iso()

            try:
                response = await client.export.export_enhanced_ohlcv(
                    start_date=start,
                    end_date=end,
                    strategy_configs=[strategy],
                    strategy_name=strategy_name,
                    blueprint_name=blueprint_name,
                )
                return [
                    {
                        "task_id": str(response.task_id),
                        "period": period,
                        "status": "pending",
                        "error": None,
                    }
                ]
            except Exception as e:
                logger.error(f"Failed to submit Enhanced OHLCV task: {e}")
                return [
                    {
                        "task_id": None,
                        "period": period,
                        "status": "failed",
                        "error": str(e),
                    }
                ]
