"""Strategy Registry for local strategy management.

This module provides the StrategyRegistry class for managing strategies
locally with file persistence and server synchronization.

Usage:
    >>> from tradepose_client.registry import StrategyRegistry
    >>> from tradepose_client.builder import StrategyBuilder
    >>>
    >>> # Create registry
    >>> registry = StrategyRegistry()
    >>>
    >>> # Add strategies built with StrategyBuilder
    >>> strategy = builder.build(volatility_indicator=atr, note="...")
    >>> registry.add(strategy)
    >>>
    >>> # Save to file
    >>> registry.save("strategies.json")
    >>>
    >>> # Load from file
    >>> registry.load("strategies.json")
    >>>
    >>> # Sync to server
    >>> async with TradePoseClient(api_key="...") as client:
    ...     result = await registry.sync(client)
    ...     print(f"Created: {result.created}, Updated: {result.updated}")
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from tradepose_models.strategy import StrategyConfig

    from ..client import TradePoseClient

from tradepose_models.indicators import PolarsExprField

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of sync operation."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if sync was successful (no errors)."""
        return len(self.errors) == 0

    def __str__(self) -> str:
        return (
            f"SyncResult(created={self.created}, updated={self.updated}, "
            f"skipped={self.skipped}, errors={len(self.errors)})"
        )


class StrategyRegistry:
    """Local strategy registry with file persistence and server sync.

    The registry manages strategies in memory and provides:
    - Add/remove/get strategies
    - Save to / load from JSON file
    - Sync to server (create/update)
    - Pick strategies for Portfolio building

    Example:
        >>> registry = StrategyRegistry()
        >>>
        >>> # Add strategy
        >>> registry.add(my_strategy)
        >>>
        >>> # Get strategy
        >>> strategy = registry.get("SuperTrend_Strategy")
        >>>
        >>> # List all
        >>> for name, strategy in registry.list():
        ...     print(f"{name}: {strategy.note}")
        >>>
        >>> # Save/Load
        >>> registry.save("strategies.json")
        >>> registry.load("strategies.json")
        >>>
        >>> # Pick for portfolio
        >>> selections = registry.pick([
        ...     ("SuperTrend_Strategy", "base"),
        ...     ("SuperTrend_Strategy", "risk_mgmt"),
        ... ])
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._strategies: dict[str, "StrategyConfig"] = {}

    def add(self, strategy: "StrategyConfig") -> None:
        """Add or replace a strategy.

        Args:
            strategy: Strategy configuration to add

        Example:
            >>> registry.add(my_strategy)
        """
        self._strategies[strategy.name] = strategy
        logger.debug(f"Added strategy: {strategy.name}")

    def get(self, name: str) -> "StrategyConfig":
        """Get strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy configuration

        Raises:
            KeyError: If strategy not found
        """
        if name not in self._strategies:
            raise KeyError(f"Strategy '{name}' not found in registry")
        return self._strategies[name]

    def list(self) -> list[tuple[str, "StrategyConfig"]]:
        """List all strategies.

        Returns:
            List of (name, strategy) tuples
        """
        return list(self._strategies.items())

    def remove(self, name: str) -> bool:
        """Remove a strategy.

        Args:
            name: Strategy name

        Returns:
            True if removed, False if not found
        """
        if name in self._strategies:
            del self._strategies[name]
            logger.debug(f"Removed strategy: {name}")
            return True
        return False

    def clear(self) -> None:
        """Remove all strategies."""
        self._strategies.clear()
        logger.debug("Cleared all strategies")

    def __len__(self) -> int:
        """Return number of strategies."""
        return len(self._strategies)

    def __contains__(self, name: str) -> bool:
        """Check if strategy exists."""
        return name in self._strategies

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    def save(self, path: str | Path) -> None:
        """Save registry to JSON file.

        Args:
            path: File path to save to

        Example:
            >>> registry.save("strategies.json")
        """
        path = Path(path)

        data = {
            "version": "1.0",
            "strategies": {},
        }

        for name, strategy in self._strategies.items():
            # Use Pydantic's model_dump for serialization
            if hasattr(strategy, "model_dump"):
                data["strategies"][name] = strategy.model_dump(mode="json")
            else:
                # Fallback for dict-like objects
                data["strategies"][name] = dict(strategy)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self._strategies)} strategies to {path}")

    def load(self, path: str | Path) -> None:
        """Load registry from JSON file.

        This replaces all existing strategies.

        Args:
            path: File path to load from

        Raises:
            FileNotFoundError: If file not found
            ValueError: If file format is invalid

        Example:
            >>> registry.load("strategies.json")
        """
        from tradepose_models.strategy import StrategyConfig

        path = Path(path)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if "strategies" not in data:
            raise ValueError("Invalid registry file: missing 'strategies' key")

        self._strategies.clear()

        for name, strategy_data in data["strategies"].items():
            try:
                strategy = StrategyConfig(**strategy_data)
                self._strategies[name] = strategy
            except Exception as e:
                logger.error(f"Failed to load strategy '{name}': {e}")
                raise ValueError(f"Failed to load strategy '{name}': {e}")

        logger.info(f"Loaded {len(self._strategies)} strategies from {path}")

    # =========================================================================
    # SERVER SYNC
    # =========================================================================

    async def sync(self, client: "TradePoseClient") -> SyncResult:
        """Sync local strategies to server.

        Creates new strategies and updates existing ones.

        Args:
            client: TradePoseClient instance

        Returns:
            SyncResult with created/updated/skipped counts

        Example:
            >>> async with TradePoseClient(api_key="...") as client:
            ...     result = await registry.sync(client)
            ...     print(f"Synced: {result}")
        """

        result = SyncResult()

        # Get existing strategies from server
        try:
            server_strategies = await client.strategies_crud.list()
            existing_names = {s.name for s in server_strategies.strategies}
        except Exception as e:
            logger.error(f"Failed to fetch server strategies: {e}")
            result.errors.append(f"Failed to fetch server strategies: {e}")
            return result

        for name, strategy in self._strategies.items():
            try:
                if name in existing_names:
                    # Update existing strategy
                    await self._update_strategy(client, strategy)
                    result.updated += 1
                    logger.info(f"Updated strategy: {name}")
                else:
                    # Create new strategy
                    await self._create_strategy(client, strategy)
                    result.created += 1
                    logger.info(f"Created strategy: {name}")
            except Exception as e:
                logger.error(f"Failed to sync strategy '{name}': {e}")
                result.errors.append(f"Strategy '{name}': {e}")

        return result

    async def _create_strategy(
        self,
        client: "TradePoseClient",
        strategy: "StrategyConfig",
    ) -> None:
        """Create strategy and its blueprints on server."""
        from ..resources.strategies_crud import (
            IndicatorSpec,
            StrategyCreateRequest,
        )

        # Create strategy
        request = StrategyCreateRequest(
            name=strategy.name,
            base_instrument=strategy.base_instrument,
            base_freq=strategy.base_freq.value
            if hasattr(strategy.base_freq, "value")
            else str(strategy.base_freq),
            note=strategy.note,
            volatility_indicator=PolarsExprField.serialize(strategy.volatility_indicator)
            if strategy.volatility_indicator is not None
            else None,
            indicators=[
                IndicatorSpec(
                    name=ind.display_name() if hasattr(ind, "display_name") else str(ind),
                    type=ind.indicator.indicator_type.value
                    if hasattr(ind.indicator, "indicator_type")
                    else "unknown",
                    params=ind.indicator.model_dump()
                    if hasattr(ind.indicator, "model_dump")
                    else {},
                )
                for ind in (strategy.indicators or [])
            ],
        )
        await client.strategies_crud.create(request)

        # Create base blueprint
        if strategy.base_blueprint:
            await self._create_blueprint(
                client, strategy.name, strategy.base_blueprint, is_base=True
            )

        # Create advanced blueprints
        for blueprint in strategy.advanced_blueprints or []:
            await self._create_blueprint(client, strategy.name, blueprint, is_base=False)

    async def _update_strategy(
        self,
        client: "TradePoseClient",
        strategy: "StrategyConfig",
    ) -> None:
        """Update strategy on server (note and indicators only)."""
        from ..resources.strategies_crud import IndicatorSpec, StrategyUpdateRequest

        request = StrategyUpdateRequest(
            note=strategy.note,
            volatility_indicator=PolarsExprField.serialize(strategy.volatility_indicator)
            if strategy.volatility_indicator is not None
            else None,
            indicators=[
                IndicatorSpec(
                    name=ind.display_name() if hasattr(ind, "display_name") else str(ind),
                    type=ind.indicator.indicator_type.value
                    if hasattr(ind.indicator, "indicator_type")
                    else "unknown",
                    params=ind.indicator.model_dump()
                    if hasattr(ind.indicator, "model_dump")
                    else {},
                )
                for ind in (strategy.indicators or [])
            ],
        )
        await client.strategies_crud.update(strategy.name, request)

    async def _create_blueprint(
        self,
        client: "TradePoseClient",
        strategy_name: str,
        blueprint: "BaseModel",
        is_base: bool,
    ) -> None:
        """Create blueprint on server."""
        from ..resources.strategies_crud import BlueprintCreateRequest

        # Triggers are already Trigger instances from tradepose_models.strategy
        # Pass them directly since BlueprintCreateRequest now uses Trigger
        request = BlueprintCreateRequest(
            name=blueprint.name,
            direction=blueprint.direction.value
            if hasattr(blueprint.direction, "value")
            else str(blueprint.direction),
            trend_type=blueprint.trend_type.value
            if hasattr(blueprint.trend_type, "value")
            else str(blueprint.trend_type),
            entry_first=blueprint.entry_first,
            note=blueprint.note,
            entry_triggers=list(blueprint.entry_triggers or []),
            exit_triggers=list(blueprint.exit_triggers or []),
            is_base=is_base,
        )
        await client.strategies_crud.create_blueprint(strategy_name, request)

    def _indicator_to_dict(self, indicator) -> dict | None:
        """Convert IndicatorSpec to dict."""
        if indicator is None:
            return None
        if hasattr(indicator, "model_dump"):
            return indicator.model_dump(mode="json")
        return dict(indicator)

    # =========================================================================
    # PORTFOLIO BUILDING
    # =========================================================================

    def pick(
        self,
        selections: list[tuple[str, str]],
    ) -> list[dict]:
        """Pick strategy+blueprint pairs for Portfolio building.

        Args:
            selections: List of (strategy_name, blueprint_name) tuples

        Returns:
            List of selection dicts for PortfolioBuilder

        Raises:
            KeyError: If strategy not found

        Example:
            >>> selections = registry.pick([
            ...     ("SuperTrend_Strategy", "base"),
            ...     ("SuperTrend_Strategy", "risk_mgmt"),
            ... ])
        """
        result = []

        for strategy_name, blueprint_name in selections:
            # Validate strategy exists
            strategy = self.get(strategy_name)

            # Validate blueprint exists
            all_blueprints = [strategy.base_blueprint] + (strategy.advanced_blueprints or [])
            blueprint_names = [bp.name for bp in all_blueprints if bp]

            if blueprint_name not in blueprint_names:
                raise KeyError(
                    f"Blueprint '{blueprint_name}' not found in strategy '{strategy_name}'. "
                    f"Available: {blueprint_names}"
                )

            result.append(
                {
                    "strategy_name": strategy_name,
                    "blueprint_name": blueprint_name,
                }
            )

        return result

    def __repr__(self) -> str:
        """String representation."""
        return f"StrategyRegistry(strategies={len(self._strategies)})"
