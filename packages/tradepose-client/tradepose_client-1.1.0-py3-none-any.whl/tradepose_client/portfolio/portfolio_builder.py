"""Portfolio Builder for constructing portfolios from strategy selections.

Usage:
    >>> from tradepose_client.portfolio import PortfolioBuilder
    >>> from tradepose_client.registry import StrategyRegistry
    >>>
    >>> # Create registry and add strategies
    >>> registry = StrategyRegistry()
    >>> registry.add(my_strategy)
    >>>
    >>> # Build portfolio
    >>> portfolio = (
    ...     PortfolioBuilder("Gold_Portfolio", registry)
    ...     .select("SuperTrend_Strategy", "base")
    ...     .select("SuperTrend_Strategy", "risk_mgmt")
    ...     .set_capital(100000, "USD")
    ...     .set_platform("MT5")
    ...     .set_instrument_mapping({"XAU": "XAUUSD"})
    ...     .build()
    ... )
    >>>
    >>> # Create on server
    >>> async with TradePoseClient(api_key="...") as client:
    ...     result = await client.portfolios.create(portfolio)
"""

import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from ..registry import StrategyRegistry
    from ..resources.portfolios import (
        PortfolioCreateRequest,
    )

logger = logging.getLogger(__name__)


class PortfolioBuilder:
    """Fluent builder for constructing portfolios.

    Provides a chainable interface for building portfolios from
    strategy selections in a StrategyRegistry.

    Example:
        >>> portfolio = (
        ...     PortfolioBuilder("Gold_Portfolio", registry)
        ...     .select("SuperTrend_Strategy", "base")
        ...     .set_capital(100000, "USD")
        ...     .set_platform("MT5")
        ...     .build()
        ... )
    """

    def __init__(
        self,
        name: str,
        registry: "StrategyRegistry | None" = None,
    ) -> None:
        """Initialize portfolio builder.

        Args:
            name: Portfolio name
            registry: Optional StrategyRegistry for validation
        """
        self._name = name
        self._registry = registry
        self._selections: list[dict] = []
        self._capital: Decimal | None = None
        self._currency: str | None = None
        self._platform: str | None = None
        self._instrument_mapping: dict | None = None

    def select(
        self,
        strategy_name: str,
        blueprint_name: str,
    ) -> Self:
        """Add a strategy+blueprint selection.

        Args:
            strategy_name: Strategy name
            blueprint_name: Blueprint name

        Returns:
            Self for chaining

        Raises:
            KeyError: If registry is set and strategy/blueprint not found
        """
        # Validate if registry is available
        if self._registry:
            strategy = self._registry.get(strategy_name)

            # Get all blueprint names
            all_blueprints = [strategy.base_blueprint] + (strategy.advanced_blueprints or [])
            blueprint_names = [bp.name for bp in all_blueprints if bp]

            if blueprint_name not in blueprint_names:
                raise KeyError(
                    f"Blueprint '{blueprint_name}' not found in strategy '{strategy_name}'. "
                    f"Available: {blueprint_names}"
                )

        self._selections.append(
            {
                "strategy_name": strategy_name,
                "blueprint_name": blueprint_name,
            }
        )

        logger.debug(f"Added selection: {strategy_name}/{blueprint_name}")
        return self

    def set_capital(
        self,
        amount: Decimal | int | float,
        currency: str,
    ) -> Self:
        """Set portfolio capital and currency.

        Args:
            amount: Capital amount
            currency: Currency code (e.g., "USD")

        Returns:
            Self for chaining
        """
        self._capital = Decimal(str(amount))
        self._currency = currency
        return self

    def set_platform(self, platform: str) -> Self:
        """Set trading platform.

        Args:
            platform: Platform name (e.g., "MT5", "BINANCE")

        Returns:
            Self for chaining
        """
        self._platform = platform
        return self

    def set_instrument_mapping(self, mapping: dict[str, str]) -> Self:
        """Set instrument mapping.

        Maps base instruments to target symbols for the platform.

        Args:
            mapping: Dict of base_instrument -> target_symbol

        Returns:
            Self for chaining

        Example:
            >>> builder.set_instrument_mapping({
            ...     "XAU": "XAUUSD",
            ...     "BTC": "BTCUSD",
            ... })
        """
        self._instrument_mapping = mapping
        return self

    def build(self) -> "PortfolioCreateRequest":
        """Build the PortfolioCreateRequest.

        Returns:
            PortfolioCreateRequest ready for API submission

        Raises:
            ValueError: If required fields are missing
        """
        from ..resources.portfolios import BlueprintSelection, PortfolioCreateRequest

        # Validate required fields
        if not self._selections:
            raise ValueError("At least one selection is required")
        if self._capital is None:
            raise ValueError("Capital is required. Use .set_capital()")
        if self._currency is None:
            raise ValueError("Currency is required. Use .set_capital()")
        if self._platform is None:
            raise ValueError("Platform is required. Use .set_platform()")

        return PortfolioCreateRequest(
            name=self._name,
            capital=self._capital,
            currency=self._currency,
            platform=self._platform,
            selections=[
                BlueprintSelection(
                    strategy_name=s["strategy_name"],
                    blueprint_name=s["blueprint_name"],
                )
                for s in self._selections
            ],
            instrument_mapping=self._instrument_mapping,
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PortfolioBuilder(name='{self._name}', "
            f"selections={len(self._selections)}, "
            f"capital={self._capital}, "
            f"platform={self._platform})"
        )
