"""Trades query resource for TradePose Client.

This module provides operations for querying trades from backtest results.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .base import BaseResource

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# RESPONSE MODELS
# =============================================================================


class TradeResponse(BaseModel):
    """Trade response model."""

    id: str
    strategy_name: str
    blueprint_name: str
    instrument: str
    direction: str
    entry_time: datetime
    exit_time: datetime | None = None
    entry_price: Decimal
    exit_price: Decimal | None = None
    quantity: Decimal
    pnl: Decimal | None = None
    pnl_pct: float | None = None
    mae: float | None = None
    mfe: float | None = None
    has_entry_signal: bool
    has_exit_signal: bool
    sl_price: Decimal | None = None
    tp_price: Decimal | None = None
    created_at: datetime


class TradesListResponse(BaseModel):
    """Trades list response."""

    trades: list[TradeResponse]
    count: int
    limit: int
    offset: int


# =============================================================================
# RESOURCE CLASS
# =============================================================================


class TradesResource(BaseResource):
    """Trades query resource.

    Provides operations for querying trades from backtest results.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Query trades by strategy
        ...     trades = await client.trades.query(
        ...         strategy_name="SuperTrend",
        ...         start_time=datetime(2024, 1, 1),
        ...         limit=100
        ...     )
        ...
        ...     for trade in trades.trades:
        ...         print(f"{trade.entry_time}: {trade.pnl}")
    """

    async def query(
        self,
        *,
        strategy_name: str | None = None,
        blueprint_name: str | None = None,
        portfolio_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        has_entry_signal: bool | None = None,
        has_exit_signal: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TradesListResponse:
        """Query trades with filters.

        Args:
            strategy_name: Filter by strategy name
            blueprint_name: Filter by blueprint name
            portfolio_name: Filter by portfolio name (via allocations)
            start_time: Filter by entry_time >= start_time
            end_time: Filter by entry_time <= end_time
            has_entry_signal: Filter by entry signal presence
            has_exit_signal: Filter by exit signal presence
            limit: Maximum records to return (1-1000)
            offset: Pagination offset

        Returns:
            List of trades matching filters

        Raises:
            ValidationError: If filter values are invalid
            TradePoseAPIError: For other API errors
        """
        logger.debug(
            f"Querying trades: strategy={strategy_name}, blueprint={blueprint_name}, limit={limit}"
        )

        params: dict = {"limit": limit, "offset": offset}

        if strategy_name:
            params["strategy_name"] = strategy_name
        if blueprint_name:
            params["blueprint_name"] = blueprint_name
        if portfolio_name:
            params["portfolio_name"] = portfolio_name
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        if has_entry_signal is not None:
            params["has_entry_signal"] = has_entry_signal
        if has_exit_signal is not None:
            params["has_exit_signal"] = has_exit_signal

        response = await self._get("/api/v1/trades", params=params)

        result = TradesListResponse(**response)
        logger.info(f"Queried {result.count} trades (limit={limit}, offset={offset})")
        return result
