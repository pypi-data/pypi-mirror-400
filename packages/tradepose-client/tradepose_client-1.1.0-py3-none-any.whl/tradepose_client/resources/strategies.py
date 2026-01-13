"""Strategy resource for TradePose Client (StrategyConfig-centric).

This module provides synchronous CRUD operations for complete strategy configurations.
Treats StrategyConfig (strategy + blueprints) as an atomic unit.

Version: v0.3.0 (Unified API - 4 operations)
"""

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from tradepose_models.enums import Freq
from tradepose_models.indicators import PolarsExprField
from tradepose_models.strategy import Blueprint, IndicatorSpec, StrategyConfig

from .base import BaseResource

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class StrategyConfigRequest(BaseModel):
    """Complete strategy configuration request (includes blueprints)."""

    name: str = Field(..., description="Strategy name (unique per user)")
    base_instrument: str = Field(..., description="Base trading instrument")
    base_freq: str = Field(..., description="Base frequency (e.g., 1h, 15m, 1D)")
    note: str = Field(default="", description="Strategy notes")
    volatility_indicator: dict | None = Field(
        None, description="Volatility indicator expression (Polars Expr JSON)"
    )
    indicators: list[IndicatorSpec] = Field(
        default_factory=list, description="Indicator specifications"
    )
    base_blueprint: Blueprint = Field(..., description="Base blueprint (required)")
    advanced_blueprints: list[Blueprint] = Field(
        default_factory=list, description="Advanced blueprints"
    )


class StrategyConfigResponse(BaseModel):
    """Complete strategy configuration response (includes blueprints)."""

    name: str
    base_instrument: str
    base_freq: str
    note: str
    volatility_indicator: dict | None = None
    indicators: list[IndicatorSpec]
    base_blueprint: Blueprint
    advanced_blueprints: list[Blueprint]

    model_config = {"arbitrary_types_allowed": True}


class StrategyListItemResponse(BaseModel):
    """Strategy list item response (metadata only)."""

    name: str
    base_instrument: str
    base_freq: str
    note: str


class StrategyListResponse(BaseModel):
    """Strategy list response."""

    strategies: list[StrategyListItemResponse]
    count: int


# =============================================================================
# RESOURCE CLASS
# =============================================================================


class StrategiesResource(BaseResource):
    """Strategy CRUD resource (StrategyConfig-centric).

    Provides synchronous operations for managing complete strategy configurations.
    All operations treat StrategyConfig as an atomic unit containing strategy
    metadata and all blueprints (base + advanced).

    Example:
        >>> from tradepose_models.strategy import StrategyConfig, Blueprint
        >>> from tradepose_models.enums import Freq, TradeDirection, TrendType
        >>>
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Create complete strategy configuration
        ...     config = StrategyConfig(
        ...         name="my_strategy",
        ...         base_instrument="BTCUSDT",
        ...         base_freq=Freq.MIN_15,
        ...         note="Example strategy",
        ...         volatility_indicator=None,
        ...         indicators=[],
        ...         base_blueprint=Blueprint(
        ...             name="base",
        ...             direction=TradeDirection.LONG,
        ...             trend_type=TrendType.TREND,
        ...             entry_first=True,
        ...             note="Base blueprint",
        ...             entry_triggers=[],
        ...             exit_triggers=[],
        ...         ),
        ...         advanced_blueprints=[],
        ...     )
        ...
        ...     # Create or update (upsert)
        ...     result = await client.strategies.create(config)
        ...
        ...     # List all strategies (metadata only)
        ...     strategies = await client.strategies.list()
        ...
        ...     # Get complete configuration
        ...     strategy = await client.strategies.get("my_strategy")
        ...
        ...     # Delete strategy (cascades to blueprints)
        ...     await client.strategies.delete("my_strategy")
    """

    async def create(self, config: StrategyConfig) -> StrategyConfigResponse:
        """Create or update complete strategy configuration (upsert).

        If strategy name exists, deletes old blueprints and replaces with new ones.
        All operations are atomic (transaction-based).

        Args:
            config: Complete StrategyConfig (strategy + all blueprints)

        Returns:
            Complete strategy configuration

        Raises:
            ValidationError: If config data is invalid
            TradePoseAPIError: For other API errors

        Example:
            >>> config = StrategyConfig(
            ...     name="my_strategy",
            ...     base_instrument="BTCUSDT",
            ...     base_freq=Freq.MIN_15,
            ...     note="Example",
            ...     volatility_indicator=None,
            ...     indicators=[],
            ...     base_blueprint=Blueprint(...),
            ...     advanced_blueprints=[],
            ... )
            >>> result = await client.strategies.create(config)
            >>> print(f"Strategy created/updated: {result.name}")
        """
        logger.info(f"Upserting strategy: {config.name}")

        # Convert StrategyConfig to request format
        request_data = {
            "name": config.name,
            "base_instrument": config.base_instrument,
            "base_freq": config.base_freq.value
            if isinstance(config.base_freq, Freq)
            else config.base_freq,
            "note": config.note,
            "volatility_indicator": PolarsExprField.serialize(config.volatility_indicator)
            if config.volatility_indicator is not None
            else None,
            "indicators": [ind.model_dump() for ind in config.indicators],
            "base_blueprint": config.base_blueprint.model_dump(),
            "advanced_blueprints": [bp.model_dump() for bp in config.advanced_blueprints],
        }

        response = await self._post("/api/v1/strategies", json=request_data)

        result = StrategyConfigResponse(**response)
        logger.info(f"Upserted strategy: {result.name}")
        return result

    async def list(self) -> StrategyListResponse:
        """List all strategies (metadata only).

        Returns:
            List of strategy metadata

        Raises:
            TradePoseAPIError: For API errors

        Example:
            >>> strategies = await client.strategies.list()
            >>> print(f"Found {strategies.count} strategies")
            >>> for s in strategies.strategies:
            ...     print(f"  - {s.name} ({s.base_instrument})")
        """
        logger.debug("Listing strategies")

        response = await self._get("/api/v1/strategies")

        result = StrategyListResponse(**response)
        logger.info(f"Listed {result.count} strategies")
        return result

    async def get(self, name: str) -> StrategyConfigResponse:
        """Get complete strategy configuration.

        Args:
            name: Strategy name

        Returns:
            Complete strategy configuration (strategy + all blueprints)

        Raises:
            ResourceNotFoundError: If strategy not found
            TradePoseAPIError: For other API errors

        Example:
            >>> strategy = await client.strategies.get("my_strategy")
            >>> print(f"Strategy: {strategy.name}")
            >>> print(f"Base blueprint: {strategy.base_blueprint.name}")
            >>> print(f"Advanced blueprints: {len(strategy.advanced_blueprints)}")
        """
        logger.debug(f"Getting strategy: {name}")

        response = await self._get(f"/api/v1/strategies/{name}")

        result = StrategyConfigResponse(**response)
        logger.info(f"Retrieved strategy: {result.name}")
        return result

    async def delete(self, name: str, *, archive: bool = True) -> dict:
        """Delete strategy (cascades to blueprints).

        Args:
            name: Strategy name
            archive: If True, soft-delete (archive). If False, hard delete.
                     Defaults to True (soft delete).

        Returns:
            Success message

        Raises:
            ResourceNotFoundError: If strategy not found
            TradePoseAPIError: For other API errors

        Example:
            >>> # Soft delete (archive)
            >>> response = await client.strategies.delete("my_strategy")
            >>> print(response["message"])  # "Strategy 'my_strategy' archived"
            >>>
            >>> # Hard delete (permanent)
            >>> response = await client.strategies.delete("my_strategy", archive=False)
            >>> print(response["message"])  # "Strategy 'my_strategy' deleted"
        """
        action = "Archiving" if archive else "Deleting"
        logger.info(f"{action} strategy: {name}")

        response = await self._delete(
            f"/api/v1/strategies/{name}",
            params={"archive": str(archive).lower()},
        )

        result_action = "archived" if archive else "deleted"
        logger.info(f"Strategy {name} {result_action}")
        return response  # type: ignore
