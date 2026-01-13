"""Tasks resource for TradePose Client.

This module provides methods for managing async tasks and retrieving results.
"""

import io
import logging
import zipfile

import polars as pl
from tradepose_models.export import TaskMetadataResponse

from ..exceptions import SerializationError
from .base import BaseResource

logger = logging.getLogger(__name__)


class TasksResource(BaseResource):
    """Task management resource.

    This resource provides methods to check task status and download results.
    Many TradePose operations (strategy registration, exports, backtests) are
    asynchronous and return a task_id for polling.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Get task status
        ...     status = await client.tasks.get_status(task_id)
        ...     print(f"Status: {status.status}")
        ...
        ...     # Download backtest results
        ...     if status.status == "COMPLETED":
        ...         trades_df, perf = await client.tasks.download_backtest_results(task_id)
        ...         print(f"Trades: {trades_df.shape}")
    """

    async def get_status(self, task_id: str) -> TaskMetadataResponse:
        """Get task status and metadata.

        Returns the current status, progress, and result information for a task.
        Task statuses: PENDING, PROCESSING, COMPLETED, FAILED

        Args:
            task_id: UUID of the task

        Returns:
            TaskMetadataResponse with task status and metadata

        Raises:
            ResourceNotFoundError: If task_id not found
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> status = await client.tasks.get_status(task_id)
            >>> print(f"Status: {status.status}")
            >>> print(f"Started: {status.started_at}")
            >>> if status.status == "COMPLETED":
            ...     print(f"Completed: {status.completed_at}")
            >>> elif status.status == "FAILED":
            ...     print(f"Error: {status.error_message}")
        """
        logger.debug(f"Getting task status: {task_id}")

        response = await self._get(f"/api/v1/tasks/{task_id}")

        result = TaskMetadataResponse(**response)
        logger.info(f"Task {task_id}: {result.status}")
        return result

    async def download_backtest_results(
        self,
        task_id: str,
        as_dataframe: bool = True,
    ) -> tuple[pl.DataFrame, pl.DataFrame] | tuple[bytes, bytes]:
        """Download backtest results (trades + performance).

        Downloads trades and performance data from a completed backtest task.
        Uses the /result endpoint which returns a ZIP archive.

        Args:
            task_id: UUID of the backtest task
            as_dataframe: If True, convert Parquet to DataFrames (default: True)

        Returns:
            Tuple of (trades, performance):
            - trades: Polars DataFrame (if as_dataframe=True) or bytes
            - performance: Polars DataFrame (if as_dataframe=True) or bytes

        Raises:
            ResourceNotFoundError: If task_id not found or results unavailable
            AuthenticationError: If authentication fails
            SerializationError: If ZIP extraction or parsing fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Download backtest results
            >>> trades_df, perf_df = await client.tasks.download_backtest_results(task_id)
            >>> print(f"Trades: {trades_df.shape}")
            >>> print(f"Performance: {perf_df.shape}")
            >>>
            >>> # Get raw bytes
            >>> trades_bytes, perf_bytes = await client.tasks.download_backtest_results(
            ...     task_id,
            ...     as_dataframe=False
            ... )
        """
        logger.info(f"Downloading backtest results for task: {task_id}")

        # Download ZIP from /result endpoint
        zip_data = await self._get(
            f"/api/v1/tasks/{task_id}/result",
            expect_json=False,
        )

        # Extract ZIP contents
        try:
            with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:  # type: ignore
                # Extract trades.parquet
                trades_data = zf.read("trades.parquet")
                if as_dataframe:
                    trades = pl.read_parquet(io.BytesIO(trades_data))
                    logger.debug(f"Loaded trades DataFrame: shape={trades.shape}")
                else:
                    trades = trades_data
                    logger.debug(f"Loaded trades bytes: {len(trades_data)} bytes")

                # Extract performance.parquet
                performance_data = zf.read("performance.parquet")
                if as_dataframe:
                    performance = pl.read_parquet(io.BytesIO(performance_data))
                    logger.debug(f"Loaded performance DataFrame: shape={performance.shape}")
                else:
                    performance = performance_data
                    logger.debug(f"Loaded performance bytes: {len(performance_data)} bytes")

            logger.info(f"Successfully extracted backtest results for task: {task_id}")
            return (trades, performance)

        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file: {e}")
            raise SerializationError(f"Invalid ZIP file: {e}", data_type="zip")
        except KeyError as e:
            logger.error(f"Missing file in ZIP: {e}")
            raise SerializationError(f"Missing expected file in ZIP: {e}", data_type="zip")
        except Exception as e:
            logger.error(f"Failed to extract backtest results: {e}")
            raise SerializationError(
                f"Failed to extract backtest results: {e}",
                data_type="zip",
            )

    async def download_enhanced_ohlcv(
        self,
        task_id: str,
        as_dataframe: bool = True,
    ) -> pl.DataFrame | bytes:
        """Download enhanced OHLCV with indicators and signals.

        Downloads OHLCV data with strategy indicators from a completed enhanced OHLCV task.
        Uses the /results/enhanced_ohlcv endpoint.

        Args:
            task_id: UUID of the enhanced OHLCV task
            as_dataframe: If True, convert Parquet to DataFrame (default: True)

        Returns:
            Polars DataFrame (if as_dataframe=True) or bytes

        Raises:
            ResourceNotFoundError: If task_id not found or results unavailable
            AuthenticationError: If authentication fails
            SerializationError: If Parquet parsing fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Download enhanced OHLCV
            >>> ohlcv_df = await client.tasks.download_enhanced_ohlcv(task_id)
            >>> print(f"OHLCV shape: {ohlcv_df.shape}")
            >>> print(f"Columns: {ohlcv_df.columns}")
        """
        logger.info(f"Downloading enhanced OHLCV for task: {task_id}")

        parquet_data = await self._get(
            f"/api/v1/tasks/{task_id}/results/enhanced_ohlcv",
            expect_json=False,
        )

        if not as_dataframe:
            logger.debug(f"Returning {len(parquet_data)} bytes of Parquet data")  # type: ignore
            return parquet_data  # type: ignore

        try:
            df = pl.read_parquet(parquet_data)  # type: ignore
            logger.info(f"Loaded enhanced OHLCV DataFrame: shape={df.shape}")
            return df
        except Exception as e:
            logger.error(f"Failed to parse enhanced OHLCV Parquet: {e}")
            raise SerializationError(
                f"Failed to parse enhanced OHLCV Parquet: {e}",
                data_type="parquet",
            )

    async def download_on_demand_ohlcv(
        self,
        task_id: str,
        as_dataframe: bool = True,
    ) -> pl.DataFrame | bytes:
        """Download on-demand OHLCV with custom indicators.

        Downloads OHLCV data with custom indicators from a completed on-demand OHLCV task.
        Uses the /results/on_demand_ohlcv endpoint.

        Args:
            task_id: UUID of the on-demand OHLCV task
            as_dataframe: If True, convert Parquet to DataFrame (default: True)

        Returns:
            Polars DataFrame (if as_dataframe=True) or bytes

        Raises:
            ResourceNotFoundError: If task_id not found or results unavailable
            AuthenticationError: If authentication fails
            SerializationError: If Parquet parsing fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Download on-demand OHLCV
            >>> ohlcv_df = await client.tasks.download_on_demand_ohlcv(task_id)
            >>> print(f"OHLCV shape: {ohlcv_df.shape}")
            >>> print(f"Custom indicators: {[c for c in ohlcv_df.columns if not c in ['open', 'high', 'low', 'close', 'volume']]}")
        """
        logger.info(f"Downloading on-demand OHLCV for task: {task_id}")

        parquet_data = await self._get(
            f"/api/v1/tasks/{task_id}/results/on_demand_ohlcv",
            expect_json=False,
        )

        if not as_dataframe:
            logger.debug(f"Returning {len(parquet_data)} bytes of Parquet data")  # type: ignore
            return parquet_data  # type: ignore

        try:
            df = pl.read_parquet(parquet_data)  # type: ignore
            logger.info(f"Loaded on-demand OHLCV DataFrame: shape={df.shape}")
            return df
        except Exception as e:
            logger.error(f"Failed to parse on-demand OHLCV Parquet: {e}")
            raise SerializationError(
                f"Failed to parse on-demand OHLCV Parquet: {e}",
                data_type="parquet",
            )

    async def download_latest_trades(
        self,
        task_id: str,
    ) -> dict:
        """Download latest trade states (JSON format).

        Downloads the most recent trade information from a completed latest trades task.
        Uses the /results/latest_trades endpoint.

        Args:
            task_id: UUID of the latest trades task

        Returns:
            Dict with trade information

        Raises:
            ResourceNotFoundError: If task_id not found or results unavailable
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Download latest trades
            >>> trades = await client.tasks.download_latest_trades(task_id)
            >>> print(f"Active trades: {len(trades['trades'])}")
            >>> for trade in trades['trades']:
            ...     print(f"{trade['strategy']}: {trade['status']}")
        """
        logger.info(f"Downloading latest trades for task: {task_id}")

        response = await self._get(
            f"/api/v1/tasks/{task_id}/results/latest_trades",
            expect_json=True,
        )

        logger.debug("Loaded latest trades dict")
        return response  # type: ignore

    async def download_result_by_type(
        self,
        task_id: str,
        result_type: str,
        as_dataframe: bool = True,
    ) -> pl.DataFrame | bytes | dict:
        """Download specific result type from task.

        [DEPRECATED] This method is kept for backward compatibility.
        Prefer using specific download methods:
        - download_backtest_results() for backtest results
        - download_enhanced_ohlcv() for enhanced OHLCV
        - download_on_demand_ohlcv() for on-demand OHLCV
        - download_latest_trades() for latest trades

        Downloads a specific result type from a completed task.
        Different export types produce different result types.

        Args:
            task_id: UUID of the task
            result_type: Type of result to download
                - 'trades': Trade execution details (Parquet → DataFrame)
                - 'performance': Performance metrics (JSON → dict)
                - 'enhanced_ohlcv': Enhanced OHLCV with signals (Parquet → DataFrame)
                - 'on_demand_ohlcv': On-demand OHLCV (Parquet → DataFrame)
                - 'latest_trades': Latest trade states (JSON → dict)
            as_dataframe: If True and result is Parquet, convert to DataFrame

        Returns:
            Polars DataFrame, dict (for JSON), or bytes (raw Parquet)

        Raises:
            ResourceNotFoundError: If task_id or result_type not found
            AuthenticationError: If authentication fails
            SerializationError: If parsing fails
            TradePoseAPIError: For other API errors

        Example:
            >>> # Download trades DataFrame
            >>> trades = await client.tasks.download_result_by_type(
            ...     task_id,
            ...     result_type="trades"
            ... )
            >>> print(f"Trades: {len(trades)} rows")
        """
        logger.info(f"Downloading {result_type} for task: {task_id}")

        # All result types are Parquet binary format
        response = await self._get(
            f"/api/v1/tasks/{task_id}/results/{result_type}",
            expect_json=False,
        )

        # Handle Parquet response
        parquet_data = response  # type: ignore

        if not as_dataframe:
            logger.debug(f"Returning {len(parquet_data)} bytes of Parquet data")
            return parquet_data

        # Convert to DataFrame
        try:
            df = pl.read_parquet(parquet_data)
            logger.info(f"Loaded {result_type} DataFrame: shape={df.shape}")
            return df
        except Exception as e:
            logger.error(f"Failed to parse Parquet ({result_type}): {e}")
            raise SerializationError(
                f"Failed to parse {result_type} Parquet result: {e}",
                data_type="parquet",
            )
