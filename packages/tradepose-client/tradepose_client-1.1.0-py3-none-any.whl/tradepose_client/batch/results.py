"""Result objects for batch testing API."""

import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING

import polars as pl
from tradepose_models.enums import TaskStatus
from tradepose_models.export import TaskMetadataResponse
from tradepose_models.strategy.blueprint import Blueprint
from tradepose_models.strategy.config import StrategyConfig

from tradepose_client.batch.cache import ResultCache
from tradepose_client.batch.models import Period
from tradepose_client.utils import run_async_safe

if TYPE_CHECKING:
    from tradepose_client.batch.tester import BatchTester


class BlueprintResult:
    """
    Blueprint-level view for filtering trades/performance.

    This is a lightweight view that filters the parent PeriodResult's
    DataFrame by strategy and blueprint name. No data duplication.
    """

    def __init__(
        self,
        period: "PeriodResult",
        strategy_name: str,
        blueprint: Blueprint,
    ):
        """
        Initialize blueprint result view.

        Args:
            period: Parent PeriodResult containing all data
            strategy_name: Name of the parent strategy
            blueprint: Blueprint configuration
        """
        self._period = period
        self._strategy_name = strategy_name
        self._blueprint = blueprint

    @property
    def name(self) -> str:
        """Blueprint name."""
        return self._blueprint.name

    @property
    def blueprint(self) -> Blueprint:
        """Blueprint configuration."""
        return self._blueprint

    @property
    def trades(self) -> pl.DataFrame:
        """
        Trades for this specific blueprint.

        Returns filtered DataFrame from parent PeriodResult.
        """
        all_trades = self._period.trades
        if all_trades is None or len(all_trades) == 0:
            return pl.DataFrame()

        # Filter by strategy and blueprint
        return all_trades.filter(
            (pl.col("strategy") == self._strategy_name)
            & (pl.col("blueprint") == self._blueprint.name)
        )

    @property
    def performance(self) -> pl.DataFrame:
        """
        Performance metrics for this specific blueprint.

        Returns filtered DataFrame from parent PeriodResult.
        """
        all_perf = self._period.performance
        if all_perf is None or len(all_perf) == 0:
            return pl.DataFrame()

        # Filter by strategy and blueprint
        return all_perf.filter(
            (pl.col("strategy") == self._strategy_name)
            & (pl.col("blueprint") == self._blueprint.name)
        )

    def __repr__(self) -> str:
        return f"BlueprintResult(name={self.name!r}, strategy={self._strategy_name!r})"


class StrategyResult:
    """
    Strategy-level view for filtering trades/performance.

    This is a lightweight view that filters the parent PeriodResult's
    DataFrame by strategy name. Provides access to individual blueprints.
    """

    def __init__(self, period: "PeriodResult", strategy: StrategyConfig):
        """
        Initialize strategy result view.

        Args:
            period: Parent PeriodResult containing all data
            strategy: Strategy configuration
        """
        self._period = period
        self._strategy = strategy

    @property
    def name(self) -> str:
        """Strategy name."""
        return self._strategy.name

    @property
    def strategy(self) -> StrategyConfig:
        """Strategy configuration."""
        return self._strategy

    @property
    def blueprints(self) -> list[BlueprintResult]:
        """
        All blueprints in this strategy.

        Returns list of BlueprintResult views for base_blueprint
        and all advanced_blueprints.
        """
        bps = [self._strategy.base_blueprint] + list(self._strategy.advanced_blueprints)
        return [BlueprintResult(self._period, self._strategy.name, bp) for bp in bps]

    @property
    def trades(self) -> pl.DataFrame:
        """
        Trades for all blueprints in this strategy.

        Returns filtered DataFrame from parent PeriodResult.
        """
        all_trades = self._period.trades
        if all_trades is None or len(all_trades) == 0:
            return pl.DataFrame()

        return all_trades.filter(pl.col("strategy") == self._strategy.name)

    @property
    def performance(self) -> pl.DataFrame:
        """
        Performance metrics for all blueprints in this strategy.

        Returns filtered DataFrame from parent PeriodResult.
        """
        all_perf = self._period.performance
        if all_perf is None or len(all_perf) == 0:
            return pl.DataFrame()

        return all_perf.filter(pl.col("strategy") == self._strategy.name)

    def __getitem__(self, blueprint_name: str) -> BlueprintResult:
        """
        Get blueprint by name.

        Args:
            blueprint_name: Name of the blueprint

        Returns:
            BlueprintResult view

        Raises:
            KeyError: If blueprint not found

        Example:
            >>> bp = strategy["va_breakout_long"]
            >>> print(bp.trades)
        """
        # Check base blueprint
        if self._strategy.base_blueprint.name == blueprint_name:
            return BlueprintResult(self._period, self._strategy.name, self._strategy.base_blueprint)

        # Check advanced blueprints
        for bp in self._strategy.advanced_blueprints:
            if bp.name == blueprint_name:
                return BlueprintResult(self._period, self._strategy.name, bp)

        raise KeyError(f"Blueprint not found: {blueprint_name!r}")

    def __contains__(self, blueprint_name: str) -> bool:
        """Check if blueprint exists."""
        if self._strategy.base_blueprint.name == blueprint_name:
            return True
        return any(bp.name == blueprint_name for bp in self._strategy.advanced_blueprints)

    def __iter__(self):
        """Iterate over blueprints."""
        return iter(self.blueprints)

    def __len__(self) -> int:
        """Number of blueprints."""
        return 1 + len(self._strategy.advanced_blueprints)

    def __repr__(self) -> str:
        return f"StrategyResult(name={self.name!r}, blueprints={len(self)})"


class PeriodResult:
    """
    Single period backtest result.

    Represents results for all strategies tested in a specific time period.
    Data is lazy-loaded and cached on first access.
    """

    def __init__(
        self,
        task_id: str,
        period: Period,
        strategies: list[StrategyConfig],
        cache: ResultCache | None,
        tester: "BatchTester",
    ):
        """
        Initialize period result.

        Args:
            task_id: Server task identifier
            period: Time period for this result
            strategies: List of strategies tested
            cache: Result cache (optional)
            tester: BatchTester instance for downloading results
        """
        self._task_id = task_id
        self._period = period
        self._strategies = strategies
        self._cache = cache
        self._tester = tester
        self._status = TaskStatus.PENDING
        self._error: str | None = None
        self._metadata: TaskMetadataResponse | None = None

    @property
    def task_id(self) -> str:
        """Server task identifier."""
        return self._task_id

    @property
    def period(self) -> tuple[datetime, datetime]:
        """Time period as (start, end) datetime tuple."""
        start = (
            self._period.start if isinstance(self._period.start, datetime) else self._period.start
        )
        end = self._period.end if isinstance(self._period.end, datetime) else self._period.end
        return (start, end)

    @property
    def period_str(self) -> str:
        """Formatted period string: '2021-01-01_2021-12-31'."""
        return self._period.to_key()

    @property
    def status(self) -> TaskStatus:
        """Current task status."""
        return self._status

    @property
    def strategy_names(self) -> list[str]:
        """Names of strategies tested in this period."""
        return [s.name for s in self._strategies]

    @property
    def error(self) -> str | None:
        """Error message if task failed."""
        return self._error

    @property
    def metadata(self) -> TaskMetadataResponse | None:
        """
        Full task metadata from server.

        Available after the first status poll. Contains complete information
        including timestamps, worker_id, and error details.
        """
        return self._metadata

    @property
    def strategies(self) -> list[StrategyResult]:
        """
        All strategies in this period as StrategyResult views.

        Example:
            >>> for strategy in period.strategies:
            ...     print(f"{strategy.name}: {len(strategy.blueprints)} blueprints")
        """
        return [StrategyResult(self, s) for s in self._strategies]

    def __getitem__(self, strategy_name: str) -> StrategyResult:
        """
        Get strategy by name.

        Args:
            strategy_name: Name of the strategy

        Returns:
            StrategyResult view

        Raises:
            KeyError: If strategy not found

        Example:
            >>> strategy = period["VA_Breakout"]
            >>> print(strategy.trades)
        """
        for s in self._strategies:
            if s.name == strategy_name:
                return StrategyResult(self, s)
        raise KeyError(f"Strategy not found: {strategy_name!r}")

    def __contains__(self, strategy_name: str) -> bool:
        """Check if strategy exists."""
        return any(s.name == strategy_name for s in self._strategies)

    def _update_status(
        self,
        status: TaskStatus,
        error: str | None = None,
        metadata: TaskMetadataResponse | None = None,
    ) -> None:
        """
        Update status (called by BackgroundPoller).

        Args:
            status: New task status
            error: Error message if failed
            metadata: Full TaskMetadataResponse from server
        """
        self._status = status
        if error:
            self._error = error
        if metadata:
            self._metadata = metadata

    @property
    def trades(self) -> pl.DataFrame | None:
        """
        Trade details for all strategies.

        Returns None if task not yet completed.
        Auto-downloads and caches on first access.
        """
        if self._status != TaskStatus.COMPLETED:
            return None

        # Check cache first
        if self._cache and self._cache.has(self._task_id, "trades"):
            return self._cache.get(self._task_id, "trades")

        # Download both trades and performance together
        self._download_results()

        # Return from cache
        if self._cache:
            return self._cache.get(self._task_id, "trades")
        return None

    @property
    def performance(self) -> pl.DataFrame | None:
        """
        Performance metrics for all strategies (as DataFrame).

        Returns None if task not yet completed.
        Auto-downloads and caches on first access.
        """
        if self._status != TaskStatus.COMPLETED:
            return None

        # Check cache first
        if self._cache and self._cache.has(self._task_id, "performance"):
            return self._cache.get(self._task_id, "performance")

        # Download both trades and performance together
        self._download_results()

        # Return from cache
        if self._cache:
            return self._cache.get(self._task_id, "performance")
        return None

    def _download_results(self) -> None:
        """Download both trades and performance using client.tasks API."""
        # Skip if already cached
        if self._cache and self._cache.has(self._task_id, "trades"):
            return

        # Use smart async runner (automatically handles Jupyter)
        trades_df, perf_df = run_async_safe(self._tester._async_download_results(self._task_id))

        # Cache both results
        if self._cache:
            if trades_df is not None:
                self._cache.set(self._task_id, "trades", trades_df)
            if perf_df is not None:
                self._cache.set(self._task_id, "performance", perf_df)

    def get_strategy_trades(self, strategy_name: str) -> pl.DataFrame:
        """
        Get trades for specific strategy.

        Args:
            strategy_name: Name of strategy to filter

        Returns:
            Filtered DataFrame with only this strategy's trades
        """
        trades = self.trades
        if trades is None:
            return pl.DataFrame()
        return trades.filter(pl.col("strategy_name") == strategy_name)

    def get_strategy_performance(self, strategy_name: str) -> dict | None:
        """
        Get performance metrics for specific strategy.

        Args:
            strategy_name: Name of strategy

        Returns:
            Dictionary of performance metrics or None if not found
        """
        perf_df = self.performance
        if perf_df is None or len(perf_df) == 0:
            return None

        # Filter by strategy name if column exists
        if "strategy" in perf_df.columns:
            strategy_row = perf_df.filter(pl.col("strategy") == strategy_name)
            if len(strategy_row) > 0:
                return strategy_row.to_dicts()[0]
            return None

        # If no strategy column, return first row (single strategy case)
        return perf_df.to_dicts()[0]

    def summary(self) -> pl.DataFrame | None:
        """
        Performance summary for this period.

        Automatically waits for task completion.

        Returns:
            Performance DataFrame with added period column, or None if failed/no data
        """
        self.wait()

        if self._status == TaskStatus.FAILED:
            return None

        perf_df = self.performance
        if perf_df is None or len(perf_df) == 0:
            return None

        # Add period column to performance DataFrame
        return perf_df.with_columns(pl.lit(self.period_str).alias("period"))

    def wait(self, timeout: float | None = None) -> None:
        """
        Block until this task completes.

        Args:
            timeout: Maximum wait time in seconds (None = infinite)

        Raises:
            TimeoutError: If timeout exceeded
        """
        start_time = time.time()

        while self._status not in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self._task_id} did not complete within {timeout}s")
            time.sleep(0.5)

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.PROCESSING: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
        }

        status_color = {
            TaskStatus.PENDING: "#FFA500",
            TaskStatus.PROCESSING: "#1E90FF",
            TaskStatus.COMPLETED: "#32CD32",
            TaskStatus.FAILED: "#DC143C",
        }

        emoji = status_emoji.get(self._status, "❓")
        color = status_color.get(self._status, "#808080")

        html = f"""
        <div style="border: 1px solid {color}; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <h4>{emoji} {self.period_str}</h4>
            <p><b>Status:</b> {self._status.name}</p>
            <p><b>Strategies:</b> {len(self._strategies)}</p>
            <p><b>Task ID:</b> <code>{self._task_id}</code></p>
        """

        if self._status == TaskStatus.FAILED and self._error:
            html += f'<p style="color: red;"><b>Error:</b> {self._error}</p>'

        if self._status == TaskStatus.COMPLETED:
            trades = self.trades
            if trades is not None:
                total_trades = len(trades)
                html += f"<p><b>Total Trades:</b> {total_trades}</p>"

        html += "</div>"
        return html

    def __repr__(self) -> str:
        """String representation."""
        return f"PeriodResult(period={self.period_str}, status={self._status.name}, strategies={len(self._strategies)})"


class BatchResults:
    """
    Batch backtest results container.

    Manages multiple PeriodResult objects and provides aggregated views.
    Updates automatically in background as tasks complete.
    """

    def __init__(
        self,
        task_metadata: list[dict],
        strategies: list[StrategyConfig],
        tester: "BatchTester",
        cache: ResultCache | None,
    ):
        """
        Initialize batch results.

        Args:
            task_metadata: List of task metadata dicts
            strategies: List of strategies being tested
            tester: BatchTester instance
            cache: Result cache (optional)
        """
        self._strategies = strategies
        self._tester = tester
        self._cache = cache
        self._lock = threading.RLock()

        # Initialize PeriodResult objects and task index
        self._period_results: dict[str, PeriodResult] = {}
        self._task_index: dict[str, PeriodResult] = {}  # O(1) task_id lookup

        for meta in task_metadata:
            period = meta["period"]
            period_key = period.to_key()
            task_id = meta.get("task_id")

            result = PeriodResult(
                task_id=task_id,
                period=period,
                strategies=strategies,
                cache=cache,
                tester=tester,
            )

            # Set initial status if failed during submission
            if meta.get("status") == "failed":
                result._update_status(TaskStatus.FAILED, meta.get("error"))

            self._period_results[period_key] = result

            # Build task_id index (skip failed submissions with task_id=None)
            if task_id:
                self._task_index[task_id] = result

    @property
    def task_count(self) -> int:
        """Total number of tasks."""
        return len(self._period_results)

    @property
    def strategy_count(self) -> int:
        """Number of strategies per task."""
        return len(self._strategies)

    @property
    def status(self) -> dict[str, int]:
        """
        Real-time task status counts.

        Returns:
            Dict with counts: {"pending": 1, "processing": 0, "completed": 2, "failed": 0}
        """
        with self._lock:
            counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}

            for result in self._period_results.values():
                status_name = result.status.name.lower()
                counts[status_name] = counts.get(status_name, 0) + 1

            return counts

    @property
    def progress(self) -> float:
        """Overall progress (0.0 - 1.0)."""
        status_counts = self.status
        total = self.task_count
        if total == 0:
            return 1.0

        done = status_counts["completed"] + status_counts["failed"]
        return done / total

    @property
    def is_complete(self) -> bool:
        """Whether all tasks are complete (success or failure)."""
        return self.progress == 1.0

    @property
    def completed_tasks(self) -> list[str]:
        """List of completed task IDs."""
        with self._lock:
            return [
                result.task_id
                for result in self._period_results.values()
                if result.status == TaskStatus.COMPLETED
            ]

    @property
    def periods(self) -> list[PeriodResult]:
        """
        All period results as a list.

        Example:
            >>> for period in batch.periods:
            ...     print(f"{period.period_str}: {period.status}")
        """
        with self._lock:
            return list(self._period_results.values())

    @property
    def failed_tasks(self) -> list[PeriodResult]:
        """
        List of failed period results.

        Returns PeriodResult objects (not dicts) so you can access
        full metadata including TaskMetadataResponse.

        Example:
            >>> for failed in batch.failed_tasks:
            ...     print(f"Task {failed.task_id} failed: {failed.error}")
            ...     if failed.metadata:
            ...         print(f"  Started: {failed.metadata.started_at}")
        """
        with self._lock:
            return [
                result
                for result in self._period_results.values()
                if result.status == TaskStatus.FAILED
            ]

    @property
    def results(self) -> dict[str, PeriodResult]:
        """All period results by period key."""
        with self._lock:
            return self._period_results.copy()

    def get_task(self, task_id: str) -> PeriodResult | None:
        """
        Get period result by task ID in O(1) time.

        Args:
            task_id: Server task identifier (UUID)

        Returns:
            PeriodResult or None if not found

        Example:
            >>> result = batch.get_task("f23bbb5a-03e9-4ad8-9cd1-0d87f9be8dad")
            >>> if result:
            ...     print(f"Status: {result.status}")
            ...     print(f"Error: {result.error}")
        """
        with self._lock:
            return self._task_index.get(task_id)

    def __getitem__(self, key: str) -> PeriodResult:
        """
        Get period result by period key or task ID.

        Supports two access patterns:
        1. By period key: batch["2024-01-01_2024-12-31"]
        2. By task ID: batch["f23bbb5a-03e9-4ad8-9cd1-0d87f9be8dad"]

        The method first tries period lookup, then falls back to task_id lookup.

        Args:
            key: Period key string or task_id

        Returns:
            PeriodResult

        Raises:
            KeyError: If neither period nor task_id matches

        Example:
            >>> result = batch["2024-01-01_2024-03-31"]
            >>> result = batch["f23bbb5a-03e9-4ad8-9cd1-0d87f9be8dad"]
        """
        with self._lock:
            # Try period first (common case)
            if key in self._period_results:
                return self._period_results[key]

            # Try task_id
            if key in self._task_index:
                return self._task_index[key]

            raise KeyError(f"No result found for key: {key!r}")

    def __contains__(self, key: str) -> bool:
        """Check if period key or task_id exists."""
        with self._lock:
            return key in self._period_results or key in self._task_index

    def __iter__(self):
        """Iterate over period results."""
        with self._lock:
            return iter(list(self._period_results.values()))

    def __len__(self) -> int:
        """Number of periods."""
        return len(self._period_results)

    def get_period(self, period: str | tuple[str, str]) -> PeriodResult | None:
        """
        Get result for specific period.

        Args:
            period: Period as string key or (start, end) tuple

        Returns:
            PeriodResult or None if not found

        Example:
            >>> result = batch.get_period("2021-01-01_2021-12-31")
            >>> result = batch.get_period(("2021-01-01", "2021-12-31"))
        """
        if isinstance(period, tuple):
            period_obj = Period(start=period[0], end=period[1])
            period_key = period_obj.to_key()
        else:
            period_key = period

        return self._period_results.get(period_key)

    def wait(self, timeout: float | None = None) -> None:
        """
        Block until all tasks complete.

        Args:
            timeout: Maximum wait time in seconds (None = infinite)

        Raises:
            TimeoutError: If timeout exceeded
        """
        start_time = time.time()

        while not self.is_complete:
            if timeout and (time.time() - start_time) > timeout:
                incomplete = self.task_count - (self.status["completed"] + self.status["failed"])
                raise TimeoutError(
                    f"Batch backtest did not complete within {timeout}s. "
                    f"{incomplete} tasks still pending."
                )
            time.sleep(0.5)

    def refresh(self) -> None:
        """Manually trigger status refresh (background poller updates automatically)."""
        # Status is updated automatically by BackgroundPoller
        # This is a no-op but kept for API compatibility
        pass

    def summary(self) -> pl.DataFrame:
        """
        Summary statistics for all completed periods.

        Returns:
            Combined performance DataFrame from all periods with period column

        Example:
            >>> batch = tester.submit(strategies=[s1, s2], periods=[...])
            >>> batch.wait()
            >>> summary_df = batch.summary()
            >>> print(summary_df.columns)  # includes 'period' column
        """
        summaries = []
        for result in self._period_results.values():
            if result.status == TaskStatus.COMPLETED:
                perf_df = result.summary()
                if perf_df is not None:
                    summaries.append(perf_df)

        if not summaries:
            return pl.DataFrame()

        # Concatenate all period performances
        return pl.concat(summaries)

    def all_trades(self) -> pl.DataFrame:
        """
        Combined trades from all completed periods.

        Adds 'period' column to distinguish sources.

        Returns:
            Combined DataFrame with all trades
        """
        all_trades_list = []

        for period_key, result in self._period_results.items():
            if result.status == TaskStatus.COMPLETED and result.trades is not None:
                trades = result.trades.clone()
                # Add period column
                trades = trades.with_columns(pl.lit(period_key).alias("period"))
                all_trades_list.append(trades)

        if not all_trades_list:
            return pl.DataFrame()

        return pl.concat(all_trades_list)

    def save(self, path: str) -> None:
        """
        Save all results to local directory.

        Creates directory structure:
            path/
                summary.parquet
                trades.parquet
                2021-01-01_2021-12-31/
                    trades.parquet
                    performance.parquet
                2022-01-01_2022-12-31/
                    ...

        Args:
            path: Directory path to save results
        """
        import os

        os.makedirs(path, exist_ok=True)

        # Save summary
        summary_df = self.summary()
        if len(summary_df) > 0:
            summary_df.write_parquet(os.path.join(path, "summary.parquet"))

        # Save combined trades
        all_trades_df = self.all_trades()
        if len(all_trades_df) > 0:
            all_trades_df.write_parquet(os.path.join(path, "trades.parquet"))

        # Save individual period results
        for period_key, result in self._period_results.items():
            if result.status == TaskStatus.COMPLETED:
                period_dir = os.path.join(path, period_key)
                os.makedirs(period_dir, exist_ok=True)

                if result.trades is not None:
                    result.trades.write_parquet(os.path.join(period_dir, "trades.parquet"))

                if result.performance is not None:
                    result.performance.write_parquet(
                        os.path.join(period_dir, "performance.parquet")
                    )

    def _update_period_status(
        self,
        task_id: str,
        status: TaskStatus,
        error: str | None = None,
        metadata: TaskMetadataResponse | None = None,
    ) -> None:
        """
        Update status of a period result (called by BackgroundPoller).

        Now O(1) using _task_index instead of O(n) iteration.

        Args:
            task_id: Task identifier
            status: New status
            error: Error message if failed
            metadata: Full TaskMetadataResponse from server
        """
        with self._lock:
            # O(1) lookup via task_index
            result = self._task_index.get(task_id)
            if result:
                result._update_status(status, error, metadata)

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status = self.status
        progress_pct = int(self.progress * 100)
        progress_bar = "█" * (progress_pct // 5) + "░" * (20 - progress_pct // 5)

        html = f"""
        <div style="border: 2px solid #1E90FF; padding: 15px; border-radius: 8px; background-color: #F0F8FF;">
            <h3>🚀 Batch Backtest Progress</h3>
            <p><b>Tasks:</b> {self.task_count} ({self.strategy_count} strategies × {self.task_count} periods)</p>
            <p><b>Progress:</b> <code>{progress_bar}</code> {progress_pct}% ({status["completed"] + status["failed"]}/{self.task_count})</p>
            <p>
                <span style="color: #32CD32;">✅ Completed: {status["completed"]}</span> |
                <span style="color: #1E90FF;">🔄 Processing: {status["processing"]}</span> |
                <span style="color: #FFA500;">⏳ Pending: {status["pending"]}</span> |
                <span style="color: #DC143C;">❌ Failed: {status["failed"]}</span>
            </p>
        </div>
        """

        return html

    def __repr__(self) -> str:
        """String representation."""
        status = self.status
        return (
            f"BatchResults("
            f"tasks={self.task_count}, "
            f"completed={status['completed']}, "
            f"processing={status['processing']}, "
            f"pending={status['pending']}, "
            f"failed={status['failed']}"
            f")"
        )


# =============================================================================
# OHLCV Export Results
# =============================================================================


class OHLCVPeriodResult:
    """
    Single period OHLCV result.

    Represents OHLCV data with indicators for a specific time period.
    Data is stored directly (not lazy-loaded like PeriodResult).
    """

    def __init__(
        self,
        task_id: str,
        period: Period,
        status: str = "pending",
        error: str | None = None,
        data: pl.DataFrame | None = None,
    ):
        """
        Initialize OHLCV period result.

        Args:
            task_id: Server task identifier
            period: Time period for this result
            status: Task status ('pending', 'completed', 'failed')
            error: Error message if failed
            data: OHLCV DataFrame (set after download)
        """
        self._task_id = task_id
        self._period = period
        self._status = status
        self._error = error
        self._data = data

    @property
    def task_id(self) -> str:
        """Server task identifier."""
        return self._task_id

    @property
    def period(self) -> Period:
        """Time period object."""
        return self._period

    @property
    def period_str(self) -> str:
        """Formatted period string: '2024-01-01_2024-12-31'."""
        return self._period.to_key()

    @property
    def status(self) -> str:
        """Current task status ('pending', 'completed', 'failed')."""
        return self._status

    @property
    def error(self) -> str | None:
        """Error message if task failed."""
        return self._error

    @property
    def data(self) -> pl.DataFrame | None:
        """
        OHLCV DataFrame with indicators.

        Returns None if task not completed or failed.
        """
        return self._data

    @property
    def df(self) -> pl.DataFrame | None:
        """Alias for data property."""
        return self._data

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status_emoji = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌",
        }
        status_color = {
            "pending": "#FFA500",
            "processing": "#1E90FF",
            "completed": "#32CD32",
            "failed": "#DC143C",
        }

        emoji = status_emoji.get(self._status, "❓")
        color = status_color.get(self._status, "#808080")

        html = f"""
        <div style="border: 1px solid {color}; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <h4>{emoji} {self.period_str}</h4>
            <p><b>Status:</b> {self._status}</p>
            <p><b>Task ID:</b> <code>{self._task_id}</code></p>
        """

        if self._status == "failed" and self._error:
            html += f'<p style="color: red;"><b>Error:</b> {self._error}</p>'

        if self._status == "completed" and self._data is not None:
            html += (
                f"<p><b>Shape:</b> {self._data.shape[0]} rows × {self._data.shape[1]} columns</p>"
            )

        html += "</div>"
        return html

    def __repr__(self) -> str:
        """String representation."""
        shape = f", shape={self._data.shape}" if self._data is not None else ""
        return f"OHLCVPeriodResult(period={self.period_str!r}, status={self._status!r}{shape})"


class OHLCVResults:
    """
    OHLCV export results container (for ON_DEMAND_OHLCV).

    Manages multiple OHLCVPeriodResult objects and provides aggregated views.
    Similar to BatchResults but for OHLCV data.

    Example:
        >>> results = tester.submit_ohlcv(strategy, periods)
        >>> results.wait()
        >>>
        >>> # Access by period
        >>> q1 = results["2024-01-01_2024-03-31"]
        >>> print(q1.df)
        >>>
        >>> # Iterate over periods
        >>> for period in results:
        ...     print(f"{period.period_str}: {period.df.shape}")
        >>>
        >>> # Get combined DataFrame
        >>> all_data = results.to_df()
    """

    def __init__(self, task_metadata: list[dict], periods: list[Period]):
        """
        Initialize OHLCV results.

        Args:
            task_metadata: List of task metadata dicts with task_id, period, status
            periods: List of Period objects
        """
        self._period_results: dict[str, OHLCVPeriodResult] = {}
        self._task_index: dict[str, OHLCVPeriodResult] = {}

        for meta in task_metadata:
            period = meta["period"]
            period_key = period.to_key()
            task_id = meta.get("task_id")

            result = OHLCVPeriodResult(
                task_id=task_id or "",
                period=period,
                status=meta.get("status", "pending"),
                error=meta.get("error"),
            )

            self._period_results[period_key] = result

            if task_id:
                self._task_index[task_id] = result

    @property
    def task_count(self) -> int:
        """Total number of tasks."""
        return len(self._period_results)

    @property
    def status(self) -> dict[str, int]:
        """
        Task status counts.

        Returns:
            Dict with counts: {"pending": 1, "completed": 2, "failed": 0}
        """
        counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
        for result in self._period_results.values():
            status = result.status
            counts[status] = counts.get(status, 0) + 1
        return counts

    @property
    def progress(self) -> float:
        """Overall progress (0.0 - 1.0)."""
        status_counts = self.status
        total = self.task_count
        if total == 0:
            return 1.0
        done = status_counts["completed"] + status_counts["failed"]
        return done / total

    @property
    def is_complete(self) -> bool:
        """Whether all tasks are complete (success or failure)."""
        return self.progress == 1.0

    def wait(self, timeout: float | None = None) -> None:
        """
        Block until all tasks complete.

        Args:
            timeout: Maximum wait time in seconds (None = infinite)

        Raises:
            TimeoutError: If timeout exceeded

        Example:
            >>> results = tester.submit_ohlcv(strategy, periods)
            >>> results.wait()  # Block until all complete
            >>> print(results.to_df())
        """
        start_time = time.time()

        while not self.is_complete:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"OHLCV tasks did not complete within {timeout}s. Progress: {self.progress:.0%}"
                )
            time.sleep(0.1)  # Short sleep to avoid busy-waiting

    @property
    def periods(self) -> list[OHLCVPeriodResult]:
        """All period results as a list."""
        return list(self._period_results.values())

    @property
    def failed_periods(self) -> list[OHLCVPeriodResult]:
        """List of failed period results."""
        return [r for r in self._period_results.values() if r.status == "failed"]

    @property
    def completed_periods(self) -> list[OHLCVPeriodResult]:
        """List of completed period results."""
        return [r for r in self._period_results.values() if r.status == "completed"]

    def __getitem__(self, key: str) -> OHLCVPeriodResult:
        """
        Get period result by period key or task ID.

        Args:
            key: Period key string (e.g., "2024-01-01_2024-03-31") or task_id

        Returns:
            OHLCVPeriodResult

        Raises:
            KeyError: If not found

        Example:
            >>> result = results["2024-01-01_2024-03-31"]
            >>> print(result.df)
        """
        if key in self._period_results:
            return self._period_results[key]
        if key in self._task_index:
            return self._task_index[key]
        raise KeyError(f"No result found for key: {key!r}")

    def __contains__(self, key: str) -> bool:
        """Check if period key or task_id exists."""
        return key in self._period_results or key in self._task_index

    def __iter__(self):
        """Iterate over period results."""
        return iter(self._period_results.values())

    def __len__(self) -> int:
        """Number of periods."""
        return len(self._period_results)

    def get_period(self, period: str | Period) -> OHLCVPeriodResult | None:
        """
        Get result for specific period.

        Args:
            period: Period key string or Period object

        Returns:
            OHLCVPeriodResult or None if not found
        """
        if isinstance(period, Period):
            period_key = period.to_key()
        else:
            period_key = period
        return self._period_results.get(period_key)

    def to_df(self) -> pl.DataFrame:
        """
        Combine all completed period DataFrames.

        Adds 'period' column to distinguish sources.

        Returns:
            Combined DataFrame with all OHLCV data

        Example:
            >>> df = results.to_df()
            >>> print(df.columns)  # [..., 'period']
        """
        dfs = []
        for period_key, result in self._period_results.items():
            if result.status == "completed" and result.data is not None:
                df = result.data.clone()
                df = df.with_columns(pl.lit(period_key).alias("period"))
                dfs.append(df)

        if not dfs:
            return pl.DataFrame()

        return pl.concat(dfs)

    def _update_result(
        self,
        task_id: str,
        status: str,
        error: str | None = None,
        data: pl.DataFrame | None = None,
    ) -> None:
        """
        Update a period result (internal method).

        Args:
            task_id: Task identifier
            status: New status
            error: Error message if failed
            data: OHLCV DataFrame if completed
        """
        result = self._task_index.get(task_id)
        if result:
            result._status = status
            if error:
                result._error = error
            if data is not None:
                result._data = data

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status = self.status
        progress_pct = int(self.progress * 100)
        progress_bar = "█" * (progress_pct // 5) + "░" * (20 - progress_pct // 5)

        html = f"""
        <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 8px; background-color: #F1F8E9;">
            <h3>📊 OHLCV Export Progress</h3>
            <p><b>Tasks:</b> {self.task_count} periods</p>
            <p><b>Progress:</b> <code>{progress_bar}</code> {progress_pct}% ({status["completed"] + status["failed"]}/{self.task_count})</p>
            <p>
                <span style="color: #32CD32;">✅ Completed: {status["completed"]}</span> |
                <span style="color: #1E90FF;">🔄 Processing: {status["processing"]}</span> |
                <span style="color: #FFA500;">⏳ Pending: {status["pending"]}</span> |
                <span style="color: #DC143C;">❌ Failed: {status["failed"]}</span>
            </p>
        </div>
        """

        return html

    def __repr__(self) -> str:
        """String representation."""
        status = self.status
        return (
            f"OHLCVResults("
            f"tasks={self.task_count}, "
            f"completed={status['completed']}, "
            f"failed={status['failed']}"
            f")"
        )


# =============================================================================
# Enhanced OHLCV Export Results (ENHANCED_OHLCV = 2)
# =============================================================================


class EnhancedOhlcvPeriodResult:
    """
    Single period Enhanced OHLCV result.

    Represents OHLCV data with strategy indicators, signals, and trading context.
    Unlike OHLCVPeriodResult, this requires a registered strategy and includes
    complete signal information (entry/exit signals, trading context).

    Example:
        >>> result = tester.submit_enhanced_ohlcv(
        ...     strategy=my_strategy,
        ...     period=Period.Q1(2024),
        ... )
        >>> print(result.status)  # 'pending', 'completed', 'failed'
        >>> print(result.df)      # DataFrame with signals and context
    """

    def __init__(
        self,
        task_id: str,
        period: Period,
        status: str = "pending",
        error: str | None = None,
        data: pl.DataFrame | None = None,
    ):
        """
        Initialize Enhanced OHLCV period result.

        Args:
            task_id: Server task identifier
            period: Time period for this result
            status: Task status ('pending', 'processing', 'completed', 'failed')
            error: Error message if failed
            data: Enhanced OHLCV DataFrame (set after download)
        """
        self._task_id = task_id
        self._period = period
        self._status = status
        self._error = error
        self._data = data
        self._lock = threading.RLock()

    @property
    def task_id(self) -> str:
        """Server task identifier."""
        return self._task_id

    @property
    def period(self) -> Period:
        """Time period object."""
        return self._period

    @property
    def period_str(self) -> str:
        """Formatted period string: '2024-01-01_2024-12-31'."""
        return self._period.to_key()

    @property
    def status(self) -> str:
        """Current task status ('pending', 'processing', 'completed', 'failed')."""
        with self._lock:
            return self._status

    @property
    def error(self) -> str | None:
        """Error message if task failed."""
        with self._lock:
            return self._error

    @property
    def data(self) -> pl.DataFrame | None:
        """
        Enhanced OHLCV DataFrame with indicators, signals, and trading context.

        Returns None if task not completed or failed.
        """
        with self._lock:
            return self._data

    @property
    def df(self) -> pl.DataFrame | None:
        """Alias for data property."""
        return self.data

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status_emoji = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌",
        }
        status_color = {
            "pending": "#FFA500",
            "processing": "#1E90FF",
            "completed": "#32CD32",
            "failed": "#DC143C",
        }

        emoji = status_emoji.get(self._status, "❓")
        color = status_color.get(self._status, "#808080")

        html = f"""
        <div style="border: 1px solid {color}; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <h4>{emoji} Enhanced OHLCV: {self.period_str}</h4>
            <p><b>Status:</b> {self._status}</p>
            <p><b>Task ID:</b> <code>{self._task_id}</code></p>
        """

        if self._status == "failed" and self._error:
            html += f'<p style="color: red;"><b>Error:</b> {self._error}</p>'

        if self._status == "completed" and self._data is not None:
            html += (
                f"<p><b>Shape:</b> {self._data.shape[0]} rows × {self._data.shape[1]} columns</p>"
            )

        html += "</div>"
        return html

    def __repr__(self) -> str:
        """String representation."""
        shape = f", shape={self._data.shape}" if self._data is not None else ""
        return (
            f"EnhancedOhlcvPeriodResult(period={self.period_str!r}, status={self._status!r}{shape})"
        )


class EnhancedOhlcvResults:
    """
    Enhanced OHLCV export results container (internal use).

    Manages EnhancedOhlcvPeriodResult objects. Similar to OHLCVResults but
    for ENHANCED_OHLCV (export_type=2) which requires registered strategies.
    """

    def __init__(self, task_metadata: list[dict], periods: list[Period]):
        """
        Initialize Enhanced OHLCV results.

        Args:
            task_metadata: List of task metadata dicts with task_id, period, status
            periods: List of Period objects
        """
        self._period_results: dict[str, EnhancedOhlcvPeriodResult] = {}
        self._task_index: dict[str, EnhancedOhlcvPeriodResult] = {}
        self._lock = threading.RLock()

        for meta in task_metadata:
            period = meta["period"]
            period_key = period.to_key()
            task_id = meta.get("task_id")

            result = EnhancedOhlcvPeriodResult(
                task_id=task_id or "",
                period=period,
                status=meta.get("status", "pending"),
                error=meta.get("error"),
            )

            self._period_results[period_key] = result

            if task_id:
                self._task_index[task_id] = result

    @property
    def task_count(self) -> int:
        """Total number of tasks."""
        return len(self._period_results)

    @property
    def status(self) -> dict[str, int]:
        """
        Task status counts.

        Returns:
            Dict with counts: {"pending": 1, "completed": 2, "failed": 0}
        """
        with self._lock:
            counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
            for result in self._period_results.values():
                status = result.status
                counts[status] = counts.get(status, 0) + 1
            return counts

    @property
    def progress(self) -> float:
        """Overall progress (0.0 - 1.0)."""
        status_counts = self.status
        total = self.task_count
        if total == 0:
            return 1.0
        done = status_counts["completed"] + status_counts["failed"]
        return done / total

    @property
    def is_complete(self) -> bool:
        """Whether all tasks are complete (success or failure)."""
        return self.progress == 1.0

    def wait(self, timeout: float | None = None) -> None:
        """
        Block until all tasks complete.

        Args:
            timeout: Maximum wait time in seconds (None = infinite)

        Raises:
            TimeoutError: If timeout exceeded
        """
        start_time = time.time()

        while not self.is_complete:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Enhanced OHLCV tasks did not complete within {timeout}s. "
                    f"Progress: {self.progress:.0%}"
                )
            time.sleep(0.1)

    @property
    def periods(self) -> list[EnhancedOhlcvPeriodResult]:
        """All period results as a list."""
        with self._lock:
            return list(self._period_results.values())

    @property
    def failed_periods(self) -> list[EnhancedOhlcvPeriodResult]:
        """List of failed period results."""
        with self._lock:
            return [r for r in self._period_results.values() if r.status == "failed"]

    @property
    def completed_periods(self) -> list[EnhancedOhlcvPeriodResult]:
        """List of completed period results."""
        with self._lock:
            return [r for r in self._period_results.values() if r.status == "completed"]

    def __getitem__(self, key: str) -> EnhancedOhlcvPeriodResult:
        """
        Get period result by period key or task ID.

        Args:
            key: Period key string (e.g., "2024-01-01_2024-03-31") or task_id

        Returns:
            EnhancedOhlcvPeriodResult

        Raises:
            KeyError: If not found
        """
        with self._lock:
            if key in self._period_results:
                return self._period_results[key]
            if key in self._task_index:
                return self._task_index[key]
            raise KeyError(f"No result found for key: {key!r}")

    def __contains__(self, key: str) -> bool:
        """Check if period key or task_id exists."""
        with self._lock:
            return key in self._period_results or key in self._task_index

    def __iter__(self):
        """Iterate over period results."""
        with self._lock:
            return iter(list(self._period_results.values()))

    def __len__(self) -> int:
        """Number of periods."""
        return len(self._period_results)

    def get_period(self, period: str | Period) -> EnhancedOhlcvPeriodResult | None:
        """
        Get result for specific period.

        Args:
            period: Period key string or Period object

        Returns:
            EnhancedOhlcvPeriodResult or None if not found
        """
        if isinstance(period, Period):
            period_key = period.to_key()
        else:
            period_key = period
        with self._lock:
            return self._period_results.get(period_key)

    def to_df(self) -> pl.DataFrame:
        """
        Combine all completed period DataFrames.

        Adds 'period' column to distinguish sources.

        Returns:
            Combined DataFrame with all Enhanced OHLCV data
        """
        with self._lock:
            dfs = []
            for period_key, result in self._period_results.items():
                if result.status == "completed" and result.data is not None:
                    df = result.data.clone()
                    df = df.with_columns(pl.lit(period_key).alias("period"))
                    dfs.append(df)

            if not dfs:
                return pl.DataFrame()

            return pl.concat(dfs)

    def _update_result(
        self,
        task_id: str,
        status: str,
        error: str | None = None,
        data: pl.DataFrame | None = None,
    ) -> None:
        """
        Update a period result (internal method).

        Args:
            task_id: Task identifier
            status: New status
            error: Error message if failed
            data: Enhanced OHLCV DataFrame if completed
        """
        with self._lock:
            result = self._task_index.get(task_id)
            if result:
                with result._lock:
                    result._status = status
                    if error:
                        result._error = error
                    if data is not None:
                        result._data = data

    def _repr_html_(self) -> str:
        """Jupyter HTML representation."""
        status = self.status
        progress_pct = int(self.progress * 100)
        progress_bar = "█" * (progress_pct // 5) + "░" * (20 - progress_pct // 5)

        html = f"""
        <div style="border: 2px solid #9C27B0; padding: 15px; border-radius: 8px; background-color: #F3E5F5;">
            <h3>📊 Enhanced OHLCV Export Progress</h3>
            <p><b>Tasks:</b> {self.task_count} periods</p>
            <p><b>Progress:</b> <code>{progress_bar}</code> {progress_pct}% ({status["completed"] + status["failed"]}/{self.task_count})</p>
            <p>
                <span style="color: #32CD32;">✅ Completed: {status["completed"]}</span> |
                <span style="color: #1E90FF;">🔄 Processing: {status["processing"]}</span> |
                <span style="color: #FFA500;">⏳ Pending: {status["pending"]}</span> |
                <span style="color: #DC143C;">❌ Failed: {status["failed"]}</span>
            </p>
        </div>
        """

        return html

    def __repr__(self) -> str:
        """String representation."""
        status = self.status
        return (
            f"EnhancedOhlcvResults("
            f"tasks={self.task_count}, "
            f"completed={status['completed']}, "
            f"failed={status['failed']}"
            f")"
        )
