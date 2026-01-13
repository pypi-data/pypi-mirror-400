"""Utility functions for TradePose Client."""

import asyncio
import logging

logger = logging.getLogger(__name__)


def is_jupyter() -> bool:
    """
    Check if running in Jupyter/IPython environment.

    Returns:
        True if in Jupyter/IPython, False otherwise
    """
    try:
        get_ipython()  # type: ignore # noqa: F821
        return True
    except NameError:
        return False


def run_async_safe(coro):
    """
    Safely execute async coroutine with automatic Jupyter support.

    This function intelligently handles different environments:
    - Jupyter/IPython: Automatically applies nest_asyncio if needed
    - Standard Python: Uses standard asyncio.run() or event loop
    - No event loop: Creates new event loop

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of the coroutine

    Raises:
        RuntimeError: If in Jupyter but nest_asyncio is not installed

    Example:
        >>> result = run_async_safe(some_async_function())
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No event loop exists, create new one
        return asyncio.run(coro)

    if loop.is_running():
        # Event loop is already running (Jupyter environment)
        if is_jupyter():
            try:
                import nest_asyncio

                # Apply nest_asyncio to allow nested event loops
                nest_asyncio.apply()
                logger.debug("Applied nest_asyncio for Jupyter environment")
            except ImportError:
                raise RuntimeError(
                    "Jupyter environment detected but nest-asyncio is not installed.\n"
                    "Please install it with: pip install nest-asyncio\n"
                    "Or: uv pip install nest-asyncio"
                )

        return loop.run_until_complete(coro)
    else:
        # Event loop exists but not running (standard environment)
        return loop.run_until_complete(coro)


def setup_jupyter_support() -> bool:
    """
    Setup Jupyter support by applying nest_asyncio if needed.

    This should be called once during initialization to ensure
    Jupyter notebooks work seamlessly.

    Returns:
        True if nest_asyncio was applied, False otherwise
    """
    if not is_jupyter():
        # Not in Jupyter, nothing to do
        return False

    # In Jupyter environment, apply nest_asyncio proactively
    try:
        import nest_asyncio

        nest_asyncio.apply()
        logger.info(
            "📓 Jupyter environment detected - nest_asyncio automatically applied for seamless async support"
        )
        return True
    except ImportError:
        logger.warning(
            "⚠️  Jupyter environment detected but nest-asyncio not installed.\n"
            "   Some async operations may fail. Install with: pip install nest-asyncio"
        )
        return False
