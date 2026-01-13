"""Strategy Builder API

Provides a more concise and user-friendly strategy building interface.

Core classes:
- TradingContext: Trading Context fixed field accessor
- BlueprintBuilder: Blueprint builder with chain calls
- StrategyBuilder: Strategy builder (main entry)

Example:
    from tradepose_client.builder import StrategyBuilder, BlueprintBuilder, TradingContext
    import polars as pl

    # Create strategy builder
    builder = StrategyBuilder(
        name="my_strategy",
        base_instrument="ES",
        base_freq="1h"
    )

    # Add indicators (returns IndicatorSpec)
    atr = builder.add_indicator("atr", period=14, freq="1D", shift=1)

    # Build blueprint
    bp = BlueprintBuilder("base", "Long", "Trend")\
        .add_entry_trigger(
            name="entry",
            conditions=[atr.col() > 10],
            price_expr=pl.col("open"),
            order_strategy="ImmediateEntry",
            priority=1
        )\
        .build()

    # Build strategy
    strategy = builder.set_base_blueprint(bp).build(volatility_indicator=atr)
"""

from .blueprint_builder import BlueprintBuilder
from .strategy_builder import StrategyBuilder
from .trading_context import TradingContext

__all__ = [
    "TradingContext",
    "BlueprintBuilder",
    "StrategyBuilder",
]
