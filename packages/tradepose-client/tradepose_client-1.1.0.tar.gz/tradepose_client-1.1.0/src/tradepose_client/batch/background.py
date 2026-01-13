"""Background polling for batch testing API."""

import asyncio
import logging
import threading
import time
from typing import TYPE_CHECKING

from tradepose_models.enums import TaskStatus

if TYPE_CHECKING:
    from tradepose_client import TradePoseClient
    from tradepose_client.batch.results import (
        BatchResults,
        EnhancedOhlcvResults,
        OHLCVResults,
    )

logger = logging.getLogger(__name__)


class BackgroundPoller:
    """
    Background task status poller.

    Runs in separate daemon thread with independent event loop.
    Automatically polls task statuses and optionally downloads results.
    """

    def __init__(
        self,
        results: "BatchResults",
        client_config: dict,
        poll_interval: float,
        auto_download: bool,
    ):
        """
        Initialize background poller.

        Args:
            results: BatchResults object to update
            client_config: TradePoseClient configuration (api_key, server_url)
            poll_interval: Polling interval in seconds
            auto_download: Whether to auto-download completed results
        """
        self._results = results
        self._client_config = client_config
        self._poll_interval = poll_interval
        self._auto_download = auto_download

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start background polling thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("BackgroundPoller already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("BackgroundPoller started")

    def stop(self) -> None:
        """Stop background polling."""
        if self._thread is None:
            return

        self._stop_event.set()
        self._thread.join(timeout=5.0)
        logger.info("BackgroundPoller stopped")

    def _poll_loop(self) -> None:
        """
        Main polling loop (runs in separate thread).

        Creates independent event loop and continuously polls
        task statuses until all tasks complete.

        Client is created once and reused throughout the polling period
        for HTTP/2 connection reuse and reduced TLS handshake overhead.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Create client once for the entire polling period
            from tradepose_client import TradePoseClient

            client = TradePoseClient(**self._client_config)
            loop.run_until_complete(client.__aenter__())

            try:
                while not self._stop_event.is_set():
                    # Check if all tasks complete
                    if self._results.is_complete:
                        logger.info("All tasks complete, stopping poller")
                        break

                    # Update all task statuses
                    try:
                        loop.run_until_complete(self._update_all_statuses(client))
                    except Exception as e:
                        logger.error(f"Error updating statuses: {e}", exc_info=True)

                    # Auto-download if enabled
                    if self._auto_download:
                        try:
                            loop.run_until_complete(self._download_completed(client))
                        except Exception as e:
                            logger.error(f"Error downloading results: {e}", exc_info=True)

                    # Wait before next poll
                    time.sleep(self._poll_interval)
            finally:
                # Ensure client is properly closed
                loop.run_until_complete(client.__aexit__(None, None, None))

        finally:
            loop.close()

    async def _update_all_statuses(self, client: "TradePoseClient") -> None:
        """
        Batch update all pending/processing task statuses.

        Uses asyncio.gather for concurrent status checks.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Get all tasks that need status updates
        pending_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status in (TaskStatus.PENDING, TaskStatus.PROCESSING):
                pending_tasks.append(client.tasks.get_status(result.task_id))
                task_ids.append(result.task_id)

        if not pending_tasks:
            return

        # Fetch all statuses concurrently
        try:
            statuses = await asyncio.gather(*pending_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering task statuses: {e}")
            return

        # Update results
        for task_id, status_or_error in zip(task_ids, statuses):
            if isinstance(status_or_error, Exception):
                logger.error(f"Error fetching status for task {task_id}: {status_or_error}")
                continue

            # Update the result object with full metadata
            # status_or_error is TaskMetadataResponse
            self._results._update_period_status(
                task_id=task_id,
                status=status_or_error.status,
                error=status_or_error.error_message,
                metadata=status_or_error,  # Pass full TaskMetadataResponse
            )

    async def _download_completed(self, client: "TradePoseClient") -> None:
        """
        Download results for newly completed tasks.

        Only downloads tasks that are completed but haven't been downloaded yet.
        Downloads trades and performance separately since gateway doesn't support ZIP yet.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Find completed tasks that haven't been downloaded
        download_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status == TaskStatus.COMPLETED:
                # Check if trades are already cached
                if not self._results._cache or not self._results._cache.has(
                    result.task_id, "trades"
                ):
                    # Download both trades and performance separately
                    download_tasks.append(
                        asyncio.gather(
                            client.tasks.download_result_by_type(result.task_id, "trades"),
                            client.tasks.download_result_by_type(result.task_id, "performance"),
                            return_exceptions=True,
                        )
                    )
                    task_ids.append(result.task_id)

        if not download_tasks:
            return

        # Download all results concurrently
        try:
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering download results: {e}")
            return

        # Cache downloaded results
        for task_id, result_or_error in zip(task_ids, results):
            if isinstance(result_or_error, Exception):
                logger.error(f"Error downloading result for task {task_id}: {result_or_error}")
                continue

            # result_or_error is tuple of (trades_df, performance_df)
            # Each could be an Exception if that specific download failed
            if len(result_or_error) != 2:
                logger.error(f"Unexpected result format for task {task_id}")
                continue

            trades_result, perf_result = result_or_error

            # Cache trades if successful
            if not isinstance(trades_result, Exception) and self._results._cache:
                self._results._cache.set(task_id, "trades", trades_result)
            elif isinstance(trades_result, Exception):
                logger.error(f"Error downloading trades for task {task_id}: {trades_result}")

            # Cache performance if successful
            if not isinstance(perf_result, Exception) and self._results._cache:
                self._results._cache.set(task_id, "performance", perf_result)
            elif isinstance(perf_result, Exception):
                logger.error(f"Error downloading performance for task {task_id}: {perf_result}")

            logger.debug(f"Downloaded and cached results for task {task_id}")


class OHLCVBackgroundPoller:
    """
    Background poller for OHLCV export tasks.

    Similar to BackgroundPoller but for OHLCVResults.
    Creates client once and reuses for all polling and downloads.
    """

    def __init__(
        self,
        results: "OHLCVResults",
        client_config: dict,
        poll_interval: float,
        timeout: float | None = None,
    ):
        """
        Initialize OHLCV background poller.

        Args:
            results: OHLCVResults object to update
            client_config: TradePoseClient configuration (api_key, server_url)
            poll_interval: Polling interval in seconds
            timeout: Maximum polling time in seconds (None = no limit)
        """
        self._results = results
        self._client_config = client_config
        self._poll_interval = poll_interval
        self._timeout = timeout

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def start(self) -> None:
        """Start background polling thread."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.warning("OHLCVBackgroundPoller already running")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()
            logger.debug("OHLCVBackgroundPoller started")

    def stop(self) -> None:
        """Stop background polling."""
        with self._lock:
            if self._thread is None:
                return

            self._stop_event.set()
            self._thread.join(timeout=5.0)
            logger.debug("OHLCVBackgroundPoller stopped")

    def _poll_loop(self) -> None:
        """
        Main polling loop (runs in separate thread).

        Creates client once and reuses throughout polling period.
        Polls statuses, downloads completed results automatically.
        Stops when all tasks complete or timeout is reached.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_time = time.time()

        try:
            # Create client once for the entire polling period
            from tradepose_client import TradePoseClient

            client = TradePoseClient(**self._client_config)
            loop.run_until_complete(client.__aenter__())

            try:
                while not self._stop_event.is_set():
                    # Check if all tasks complete
                    if self._results.is_complete:
                        logger.info("All OHLCV tasks complete, stopping poller")
                        break

                    # Check for timeout
                    if self._timeout is not None:
                        elapsed = time.time() - start_time
                        if elapsed >= self._timeout:
                            logger.warning(f"OHLCV polling timeout after {elapsed:.1f}s")
                            break

                    # Update all task statuses
                    try:
                        loop.run_until_complete(self._update_all_statuses(client))
                    except Exception as e:
                        logger.error(f"Error updating OHLCV statuses: {e}", exc_info=True)

                    # Download completed results
                    try:
                        loop.run_until_complete(self._download_completed(client))
                    except Exception as e:
                        logger.error(f"Error downloading OHLCV results: {e}", exc_info=True)

                    # Wait before next poll
                    time.sleep(self._poll_interval)
            finally:
                # Ensure client is properly closed
                loop.run_until_complete(client.__aexit__(None, None, None))

        finally:
            loop.close()

    async def _update_all_statuses(self, client: "TradePoseClient") -> None:
        """
        Batch update all pending/processing task statuses.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Get all tasks that need status updates
        pending_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status in ("pending", "processing") and result.task_id:
                pending_tasks.append(client.tasks.get_status(result.task_id))
                task_ids.append(result.task_id)

        if not pending_tasks:
            return

        # Fetch all statuses concurrently
        try:
            statuses = await asyncio.gather(*pending_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering OHLCV task statuses: {e}")
            return

        # Update results
        for task_id, status_or_error in zip(task_ids, statuses):
            if isinstance(status_or_error, Exception):
                logger.error(f"Error fetching status for OHLCV task {task_id}: {status_or_error}")
                continue

            # status_or_error is TaskMetadataResponse
            status = status_or_error.status
            status_str = status.name.lower()  # TaskStatus is int enum, use .name

            self._results._update_result(
                task_id=task_id,
                status=status_str,
                error=status_or_error.error_message if status == TaskStatus.FAILED else None,
            )

    async def _download_completed(self, client: "TradePoseClient") -> None:
        """
        Download results for newly completed tasks.

        Only downloads tasks that are completed but don't have data yet.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Find completed tasks that haven't been downloaded
        download_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status == "completed" and result.data is None and result.task_id:
                download_tasks.append(client.tasks.download_on_demand_ohlcv(result.task_id))
                task_ids.append(result.task_id)

        if not download_tasks:
            return

        # Download all results concurrently
        try:
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering OHLCV download results: {e}")
            return

        # Update results with downloaded data
        for task_id, result_or_error in zip(task_ids, results):
            if isinstance(result_or_error, Exception):
                logger.error(f"Error downloading OHLCV for task {task_id}: {result_or_error}")
                self._results._update_result(task_id, "failed", str(result_or_error))
                continue

            if result_or_error is not None:
                self._results._update_result(task_id, "completed", data=result_or_error)
                logger.debug(f"Downloaded OHLCV for task {task_id}: shape={result_or_error.shape}")


class EnhancedOhlcvBackgroundPoller:
    """
    Background poller for Enhanced OHLCV export tasks.

    Similar to OHLCVBackgroundPoller but for ENHANCED_OHLCV (export_type=2).
    Uses client.tasks.download_enhanced_ohlcv() for downloading results.
    """

    def __init__(
        self,
        results: "EnhancedOhlcvResults",
        client_config: dict,
        poll_interval: float,
        timeout: float | None = None,
    ):
        """
        Initialize Enhanced OHLCV background poller.

        Args:
            results: EnhancedOhlcvResults object to update
            client_config: TradePoseClient configuration (api_key, server_url)
            poll_interval: Polling interval in seconds
            timeout: Maximum polling time in seconds (None = no limit)
        """
        self._results = results
        self._client_config = client_config
        self._poll_interval = poll_interval
        self._timeout = timeout

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def start(self) -> None:
        """Start background polling thread."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.warning("EnhancedOhlcvBackgroundPoller already running")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()
            logger.debug("EnhancedOhlcvBackgroundPoller started")

    def stop(self) -> None:
        """Stop background polling."""
        with self._lock:
            if self._thread is None:
                return

            self._stop_event.set()
            self._thread.join(timeout=5.0)
            logger.debug("EnhancedOhlcvBackgroundPoller stopped")

    def _poll_loop(self) -> None:
        """
        Main polling loop (runs in separate thread).

        Creates client once and reuses throughout polling period.
        Polls statuses, downloads completed results automatically.
        Stops when all tasks complete or timeout is reached.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_time = time.time()

        try:
            # Create client once for the entire polling period
            from tradepose_client import TradePoseClient

            client = TradePoseClient(**self._client_config)
            loop.run_until_complete(client.__aenter__())

            try:
                while not self._stop_event.is_set():
                    # Check if all tasks complete
                    if self._results.is_complete:
                        logger.info("All Enhanced OHLCV tasks complete, stopping poller")
                        break

                    # Check for timeout
                    if self._timeout is not None:
                        elapsed = time.time() - start_time
                        if elapsed >= self._timeout:
                            logger.warning(f"Enhanced OHLCV polling timeout after {elapsed:.1f}s")
                            break

                    # Update all task statuses
                    try:
                        loop.run_until_complete(self._update_all_statuses(client))
                    except Exception as e:
                        logger.error(
                            f"Error updating Enhanced OHLCV statuses: {e}",
                            exc_info=True,
                        )

                    # Download completed results
                    try:
                        loop.run_until_complete(self._download_completed(client))
                    except Exception as e:
                        logger.error(
                            f"Error downloading Enhanced OHLCV results: {e}",
                            exc_info=True,
                        )

                    # Wait before next poll
                    time.sleep(self._poll_interval)
            finally:
                # Ensure client is properly closed
                loop.run_until_complete(client.__aexit__(None, None, None))

        finally:
            loop.close()

    async def _update_all_statuses(self, client: "TradePoseClient") -> None:
        """
        Batch update all pending/processing task statuses.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Get all tasks that need status updates
        pending_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status in ("pending", "processing") and result.task_id:
                pending_tasks.append(client.tasks.get_status(result.task_id))
                task_ids.append(result.task_id)

        if not pending_tasks:
            return

        # Fetch all statuses concurrently
        try:
            statuses = await asyncio.gather(*pending_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering Enhanced OHLCV task statuses: {e}")
            return

        # Update results
        for task_id, status_or_error in zip(task_ids, statuses):
            if isinstance(status_or_error, Exception):
                logger.error(
                    f"Error fetching status for Enhanced OHLCV task {task_id}: {status_or_error}"
                )
                continue

            # status_or_error is TaskMetadataResponse
            status = status_or_error.status
            status_str = status.name.lower()  # TaskStatus is int enum, use .name

            self._results._update_result(
                task_id=task_id,
                status=status_str,
                error=status_or_error.error_message if status == TaskStatus.FAILED else None,
            )

    async def _download_completed(self, client: "TradePoseClient") -> None:
        """
        Download results for newly completed tasks.

        Only downloads tasks that are completed but don't have data yet.
        Uses client.tasks.download_enhanced_ohlcv() for downloading.

        Args:
            client: Reusable TradePoseClient instance
        """
        # Find completed tasks that haven't been downloaded
        download_tasks = []
        task_ids = []

        for result in self._results._period_results.values():
            if result.status == "completed" and result.data is None and result.task_id:
                download_tasks.append(client.tasks.download_enhanced_ohlcv(result.task_id))
                task_ids.append(result.task_id)

        if not download_tasks:
            return

        # Download all results concurrently
        try:
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error gathering Enhanced OHLCV download results: {e}")
            return

        # Update results with downloaded data
        for task_id, result_or_error in zip(task_ids, results):
            if isinstance(result_or_error, Exception):
                logger.error(
                    f"Error downloading Enhanced OHLCV for task {task_id}: {result_or_error}"
                )
                self._results._update_result(task_id, "failed", str(result_or_error))
                continue

            if result_or_error is not None:
                self._results._update_result(task_id, "completed", data=result_or_error)
                logger.debug(
                    f"Downloaded Enhanced OHLCV for task {task_id}: shape={result_or_error.shape}"
                )
