# Strategy Builder Usage Examples

The builder module provides a fluent, chainable API for constructing trading strategies, significantly reducing boilerplate code.

## Basic Usage

```python
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    TradingContext,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq,
)
import polars as pl

# 1. Create strategy builder
builder = StrategyBuilder(
    name="my_strategy",
    base_instrument="ES",
    base_freq=Freq.HOUR_1  # Use Freq enum
)

# 2. Add indicators (instrument_id automatically inherited)
atr = builder.add_indicator(
    IndicatorType.ATR,  # Use IndicatorType enum
    period=14,
    freq=Freq.DAY_1,
    shift=1
)

# 3. Create base blueprint with entry/exit logic
base_bp = BlueprintBuilder(
    "base",
    TradeDirection.LONG,  # Use TradeDirection enum
    TrendType.TREND  # Use TrendType enum
)\
    .add_entry_trigger(
        name="entry",
        conditions=[atr.col() > 10],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,  # Use OrderStrategy enum
        priority=1
    )\
    .add_exit_trigger(
        name="exit",
        conditions=[atr.col() < 5],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_EXIT,
        priority=1
    )\
    .build()

# 4. Build strategy
strategy = builder.set_base_blueprint(base_bp).build(
    volatility_indicator=atr.col(),  # Use .col() to get pl.Expr
    note="Simple ATR strategy"
)

# 5. Use the strategy (save to JSON, register via API, etc.)
print(strategy.to_json())
```

## Advanced Example: Risk Management with TradingContext

```python
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    TradingContext,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq,
)
import polars as pl

# Create builder
builder = StrategyBuilder(
    name="trend_strategy_with_risk",
    base_instrument="US100.cash_M15_FTMO_FUTURE",
    base_freq=Freq.MIN_15
)

# Add indicators
atr = builder.add_indicator(
    IndicatorType.ATR,
    period=21,
    freq=Freq.DAY_1,
    shift=1
)

st = builder.add_indicator(
    IndicatorType.SUPERTREND,
    multiplier=3.0,
    volatility_column=atr.display_name,  # Reference ATR by name
    freq=Freq.DAY_1,
    shift=0  # Dependent indicator
)

# Base blueprint: SuperTrend signals
base_bp = BlueprintBuilder(
    "base_trend",
    TradeDirection.LONG,
    TrendType.TREND
)\
    .add_entry_trigger(
        name="entry",
        conditions=[st.col().struct.field("direction") == 1],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
        priority=1,
        note="SuperTrend bullish"
    )\
    .add_exit_trigger(
        name="exit",
        conditions=[st.col().struct.field("direction") == -1],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_EXIT,
        priority=1,
        note="SuperTrend bearish"
    )\
    .build()

# Advanced blueprint: Risk management with TradingContext
risk_bp = BlueprintBuilder(
    "risk_mgmt",
    TradeDirection.LONG,
    TrendType.TREND
)\
    .add_exit_trigger(
        name="stop_loss",
        conditions=[],
        price_expr=TradingContext.advanced_entry.entry_price - atr.col() * 2,
        order_strategy=OrderStrategy.STOP_LOSS,
        priority=1,
        note="2 ATR stop loss"
    )\
    .add_exit_trigger(
        name="take_profit",
        conditions=[],
        price_expr=TradingContext.advanced_entry.entry_price + atr.col() * 3,
        order_strategy=OrderStrategy.TAKE_PROFIT,
        priority=2,
        note="3 ATR take profit"
    )\
    .build()

# Build complete strategy
strategy = builder\
    .set_base_blueprint(base_bp)\
    .add_advanced_blueprint(risk_bp)\
    .build(
        volatility_indicator=atr.col(),  # Use .col() to get pl.Expr
        note="US100 SuperTrend strategy with risk management"
    )
```

## Complete Example: KOG US100 Strategy

This example demonstrates a production-ready strategy with comprehensive risk management:

```python
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    TradingContext,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq,
)
import polars as pl

# Configuration
INSTRUMENT_ID = "US100.cash_M15_FTMO_FUTURE"
BASE_FREQ = Freq.MIN_15
STRATEGY_NAME = "KOG_US100_15T_ST_21_3"

# Create builder
builder = StrategyBuilder(
    name=STRATEGY_NAME,
    base_instrument=INSTRUMENT_ID,
    base_freq=BASE_FREQ
)

# Add indicators
atr_1d = builder.add_indicator(
    IndicatorType.ATR,
    period=21,
    freq=Freq.DAY_1,
    shift=1
)

atr_q2_1d = builder.add_indicator(
    IndicatorType.ATR_QUANTILE,
    atr_column=atr_1d.display_name,
    window=40,
    quantile=0.5,
    freq=Freq.DAY_1,
    shift=0
)

atr_1d_0s = builder.add_indicator(
    IndicatorType.ATR,
    period=21,
    freq=Freq.DAY_1,
    shift=0
)

st_21_3_1d = builder.add_indicator(
    IndicatorType.SUPERTREND,
    multiplier=3,
    volatility_column=atr_1d_0s.display_name,
    freq=Freq.DAY_1,
    shift=1
)

# Base blueprint
base_bp = BlueprintBuilder(
    "kog_us100_trend_follow",
    TradeDirection.LONG,
    TrendType.TREND,
    note="KOG Swing trend-following strategy"
)\
    .add_entry_trigger(
        name="long_entry_trend",
        conditions=[
            st_21_3_1d.col().struct.field("direction") == 1,
            pl.col("ts").dt.hour() >= 1,
            pl.col("ts").dt.hour() <= 11,
            atr_1d.col() < atr_q2_1d.col(),
        ],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
        priority=1,
        note="SuperTrend bullish + low volatility + time filter"
    )\
    .add_exit_trigger(
        name="friday_exit",
        conditions=[
            (pl.col("ts").dt.weekday() == 4) &
            (pl.col("ts").dt.hour() == 23) &
            (pl.col("ts").dt.minute() == 45)
        ],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_EXIT,
        priority=1,
        note="Friday 23:45 forced exit"
    )\
    .build()

# Advanced blueprint
adv_bp = BlueprintBuilder(
    "kog_us100_risk_management",
    TradeDirection.LONG,
    TrendType.TREND,
    note="Risk management layer"
)\
    .add_entry_trigger(
        name="favorable_entry_0.26atr",
        conditions=[],
        price_expr=TradingContext.base.entry_price - atr_1d.col() * 0.26,
        order_strategy=OrderStrategy.FAVORABLE_DELAY_ENTRY,
        priority=1,
        note="Wait for 0.26 ATR pullback"
    )\
    .add_exit_trigger(
        name="stop_loss_1.2atr",
        conditions=[],
        price_expr=TradingContext.advanced_entry.entry_price - atr_1d.col() * 1.2,
        order_strategy=OrderStrategy.STOP_LOSS,
        priority=1,
        note="Fixed stop loss 1.2 ATR"
    )\
    .add_exit_trigger(
        name="trailing_stop_2.1atr",
        conditions=[],
        price_expr=TradingContext.advanced_entry.highest_since_entry - atr_1d.col() * 2.1,
        order_strategy=OrderStrategy.TRAILING_STOP,
        priority=2,
        note="Trailing stop 2.1 ATR"
    )\
    .add_exit_trigger(
        name="breakeven_0.85atr",
        conditions=[
            TradingContext.advanced_entry.highest_since_entry >
            (TradingContext.advanced_entry.entry_price + atr_1d.col() * 0.85)
        ],
        price_expr=TradingContext.advanced_entry.entry_price + atr_1d.col() * 0.21,
        order_strategy=OrderStrategy.BREAKEVEN,
        priority=3,
        note="Move stop to cost + 0.21 ATR after 0.85 ATR profit"
    )\
    .build()

# Build final strategy
strategy = builder\
    .set_base_blueprint(base_bp)\
    .add_advanced_blueprint(adv_bp)\
    .build(
        volatility_indicator=atr_1d.col(),  # Use .col() to get pl.Expr
        note="US100 trend-following long strategy"
    )

print(strategy.to_json())
```

## Available Enums

All enums are imported from `tradepose_client` for convenience:

### Freq (Frequency)
```python
from tradepose_client import Freq

Freq.MIN_1      # 1 minute
Freq.MIN_5      # 5 minutes
Freq.MIN_15     # 15 minutes
Freq.MIN_30     # 30 minutes
Freq.HOUR_1     # 1 hour
Freq.HOUR_4     # 4 hours
Freq.DAY_1      # 1 day
Freq.WEEK_1     # 1 week
```

### IndicatorType
```python
from tradepose_client import IndicatorType

IndicatorType.SMA              # Simple Moving Average
IndicatorType.EMA              # Exponential Moving Average
IndicatorType.SMMA             # Smoothed Moving Average
IndicatorType.WMA              # Weighted Moving Average
IndicatorType.ATR              # Average True Range
IndicatorType.ATR_QUANTILE     # ATR Quantile
IndicatorType.SUPERTREND       # SuperTrend
IndicatorType.MACD             # MACD
IndicatorType.ADX              # ADX
IndicatorType.RSI              # RSI
IndicatorType.CCI              # CCI
IndicatorType.STOCHASTIC       # Stochastic
IndicatorType.BOLLINGER_BANDS  # Bollinger Bands
IndicatorType.MARKET_PROFILE   # Market Profile
IndicatorType.RAW_OHLCV        # Raw OHLCV data
```

### OrderStrategy
```python
from tradepose_client import OrderStrategy

# Entry strategies
OrderStrategy.IMMEDIATE_ENTRY
OrderStrategy.FAVORABLE_DELAY_ENTRY
OrderStrategy.ADVERSE_DELAY_ENTRY

# Exit strategies
OrderStrategy.IMMEDIATE_EXIT
OrderStrategy.STOP_LOSS
OrderStrategy.TAKE_PROFIT
OrderStrategy.TRAILING_STOP
OrderStrategy.BREAKEVEN
OrderStrategy.TIMEOUT_EXIT
```

### TradeDirection
```python
from tradepose_client import TradeDirection

TradeDirection.LONG
TradeDirection.SHORT
TradeDirection.BOTH
```

### TrendType
```python
from tradepose_client import TrendType

TrendType.TREND      # Trend-following
TrendType.RANGE      # Range-bound
TrendType.REVERSAL   # Mean reversion
```

## TradingContext Fields

The `TradingContext` class provides convenient access to trading context fields:

### Base Context (from Base Blueprint)
```python
TradingContext.base.entry_price           # Position entry price
TradingContext.base.bars_in_position      # Number of bars in position
TradingContext.base.highest_since_entry   # Highest price since entry
TradingContext.base.lowest_since_entry    # Lowest price since entry
```

### Advanced Entry Context
```python
TradingContext.advanced_entry.entry_price          # Entry price
TradingContext.advanced_entry.highest_since_entry  # Highest since entry
TradingContext.advanced_entry.lowest_since_entry   # Lowest since entry
```

### Advanced Exit Context
```python
TradingContext.advanced_exit.entry_price          # Entry price
TradingContext.advanced_exit.highest_since_entry  # Highest since exit trigger
TradingContext.advanced_exit.lowest_since_entry   # Lowest since exit trigger
```

## Cross-Instrument Indicators

You can reference indicators from different instruments:

```python
builder = StrategyBuilder(
    name="cross_instrument",
    base_instrument="ES",
    base_freq=Freq.HOUR_1
)

# ES ATR (uses base_instrument)
es_atr = builder.add_indicator(
    IndicatorType.ATR,
    period=14,
    freq=Freq.DAY_1,
    shift=1
)

# VIX ATR (override instrument_id)
vix_atr = builder.add_indicator(
    IndicatorType.ATR,
    period=14,
    freq=Freq.DAY_1,
    shift=1,
    instrument_id="VIX"  # Different instrument
)

# Use both in conditions
bp = BlueprintBuilder("base", TradeDirection.LONG, TrendType.TREND)\
    .add_entry_trigger(
        name="entry",
        conditions=[
            es_atr.col() > 10,    # ES volatility condition
            vix_atr.col() < 20    # VIX filter
        ],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
        priority=1
    )\
    .build()
```

## Benefits Over Manual Construction

- **60% less boilerplate**: No repeated `instrument_id` in every indicator
- **Type-safe enum references**: Use `IndicatorType.ATR` instead of `"atr"` strings
- **IDE autocomplete**: Full support for all enums and TradingContext fields
- **Chain-style API**: More readable and maintainable
- **Automatic indicator tracking**: No need to manually manage indicator lists

## Backward Compatibility

String-based API still works for backward compatibility:

```python
# Old style (still works, but not recommended)
atr = builder.add_indicator("atr", period=14, freq="1D", shift=1)

# New style (recommended)
atr = builder.add_indicator(IndicatorType.ATR, period=14, freq=Freq.DAY_1, shift=1)
```

## Organizing Strategies in Multiple Files

Users typically create multiple `.py` files to organize their strategies:

```
my_strategies/
├── trend_strategies.py
├── mean_reversion.py
├── breakout_strategies.py
└── risk_management.py
```

Each file can import and use the builder independently:

```python
# trend_strategies.py
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    IndicatorType,
    OrderStrategy,
    Freq,
)

def create_supertrend_strategy():
    builder = StrategyBuilder(...)
    # ... build strategy
    return builder.build(...)

# mean_reversion.py
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    IndicatorType,
    OrderStrategy,
    Freq,
)

def create_bollinger_strategy():
    builder = StrategyBuilder(...)
    # ... build strategy
    return builder.build(...)
```
