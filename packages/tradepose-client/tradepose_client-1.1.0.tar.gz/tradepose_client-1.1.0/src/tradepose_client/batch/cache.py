"""Result cache for batch testing API."""

import threading
from typing import Any


class ResultCache:
    """
    Thread-safe in-memory cache for backtest results.

    Stores downloaded DataFrames and performance metrics to avoid
    redundant API calls.
    """

    def __init__(self):
        """Initialize empty cache with thread lock."""
        self._cache: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def get(self, task_id: str, result_type: str) -> Any | None:
        """
        Get cached result.

        Args:
            task_id: Task identifier
            result_type: Type of result ("trades", "performance", etc.)

        Returns:
            Cached data or None if not found
        """
        with self._lock:
            return self._cache.get(task_id, {}).get(result_type)

    def set(self, task_id: str, result_type: str, data: Any) -> None:
        """
        Store result in cache.

        Args:
            task_id: Task identifier
            result_type: Type of result ("trades", "performance", etc.)
            data: Data to cache
        """
        with self._lock:
            if task_id not in self._cache:
                self._cache[task_id] = {}
            self._cache[task_id][result_type] = data

    def has(self, task_id: str, result_type: str) -> bool:
        """Check if result exists in cache."""
        with self._lock:
            return task_id in self._cache and result_type in self._cache[task_id]

    def clear(self, task_id: str | None = None) -> None:
        """
        Clear cache.

        Args:
            task_id: If provided, clear only this task. Otherwise clear all.
        """
        with self._lock:
            if task_id is None:
                self._cache.clear()
            else:
                self._cache.pop(task_id, None)

    def size(self) -> int:
        """Get number of cached tasks."""
        with self._lock:
            return len(self._cache)
