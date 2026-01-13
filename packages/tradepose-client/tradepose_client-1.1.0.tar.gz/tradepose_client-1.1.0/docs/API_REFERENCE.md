# API Reference

Complete API documentation for the TradePose Client SDK.

**Primary Interface:** BatchTester (synchronous, simple)
**Low-Level Interface:** TradePoseClient (async, advanced)

## Table of Contents

### Primary API (Recommended)
1. [BatchTester](#batchtester) - Batch testing interface
2. [Period](#period) - Type-safe date periods
3. [BatchResults](#batchresults) - Test results container
4. [PeriodResult](#periodresult) - Single period results

### Builder API
5. [StrategyBuilder](#strategybuilder) - Strategy construction
6. [BlueprintBuilder](#blueprintbuilder) - Blueprint creation
7. [IndicatorSpecWrapper](#indicatorspecwrapper) - Indicator reference

### Low-Level API (Advanced Users)
8. [TradePoseClient](#tradeposeclient) - Async HTTP client
9. [Resources](#resources) - API resource interfaces

---

## BatchTester

Main entry point for batch testing workflows. Handles multi-strategy, multi-period backtesting with automatic background polling.

### Initialization

```python
from tradepose_client import BatchTester

tester = BatchTester(
    api_key="tp_live_xxx",            # API key (or set TRADEPOSE_API_KEY)
    server_url="https://api.tradepose.com",  # Gateway URL (optional)
    poll_interval=2.0,                # Polling interval in seconds (default: 2.0)
    auto_download=True                # Auto-download results (default: True)
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | None | API key for authentication (required if not in env) |
| `server_url` | str | https://api.tradepose.com | Gateway server URL |
| `poll_interval` | float | 2.0 | Status polling interval (0.5-60.0s) |
| `auto_download` | bool | True | Automatically download completed results |

### Methods

#### `submit(strategies, periods, cache=True)`

Submit batch backtest tasks. Returns immediately, polls in background.

**Parameters:**

- `strategies` (list[StrategyConfig]): List of strategy configurations to test
- `periods` (list[Period]): List of Period objects defining test ranges
- `cache` (bool): Enable result caching (default: True)

**Returns:** `BatchResults` object

**Raises:**
- `ValidationError`: Invalid strategy or period configuration
- `AuthenticationError`: Invalid API key
- `NetworkError`: Connection failed

**Example:**

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

tester = BatchTester()
batch = tester.submit(
    strategies=[strategy1, strategy2],
    periods=[Period.Q1(2024), Period.Q2(2024)]
)

print(f"Submitted {batch.task_count} tasks")
batch.wait()  # Block until complete
summary = batch.summary()
```

---

## Period

Type-safe time period definition with automatic validation.

### Initialization

```python
from tradepose_client.batch import Period

# Direct construction
period = Period(start="2024-01-01", end="2024-12-31")

# Convenience constructors
q1 = Period.Q1(2024)         # 2024-01-01 to 2024-03-31
q2 = Period.Q2(2024)         # 2024-04-01 to 2024-06-30
q3 = Period.Q3(2024)         # 2024-07-01 to 2024-09-30
q4 = Period.Q4(2024)         # 2024-10-01 to 2024-12-31

year = Period.from_year(2024)      # Full year
month = Period.from_month(2024, 3)  # March 2024
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `start` | datetime | Period start time (validated) |
| `end` | datetime | Period end time (validated) |

### Methods

#### `to_iso() -> tuple[str, str]`

Convert to ISO format strings for API requests.

**Returns:** Tuple of (start_iso, end_iso)

**Example:**

```python
period = Period.Q1(2024)
start, end = period.to_iso()
# ("2024-01-01T00:00:00", "2024-03-31T00:00:00")
```

#### `to_key() -> str`

Generate unique key for this period.

**Returns:** String key (e.g., "2024-01-01_2024-03-31")

**Example:**

```python
period = Period.Q1(2024)
key = period.to_key()
# "2024-01-01_2024-03-31"
```

### Class Methods

#### `Q1(year: int) -> Period`

Create Q1 period (January - March).

#### `Q2(year: int) -> Period`

Create Q2 period (April - June).

#### `Q3(year: int) -> Period`

Create Q3 period (July - September).

#### `Q4(year: int) -> Period`

Create Q4 period (October - December).

#### `from_year(year: int) -> Period`

Create period covering entire year.

#### `from_month(year: int, month: int, n_months: int = 1) -> Period`

Create period starting from a specific month, spanning n months.

**Parameters:**
- `year`: The year (e.g., 2024)
- `month`: Starting month (1-12)
- `n_months`: Number of months to span (default: 1)

**Returns:** Period covering n consecutive months

**Raises:**
- `ValueError` if month not in 1-12
- `ValueError` if n_months < 1

**Examples:**
```python
# Single month
march = Period.from_month(2024, 3)  # 2024-03-01 to 2024-03-31

# Three months (custom quarter)
q2_custom = Period.from_month(2024, 3, n_months=3)  # 2024-03-01 to 2024-05-31

# Six months (half year)
h1 = Period.from_month(2024, 1, n_months=6)  # 2024-01-01 to 2024-06-30
h2 = Period.from_month(2024, 7, n_months=6)  # 2024-07-01 to 2024-12-31

# Cross year boundary
winter = Period.from_month(2024, 11, n_months=3)  # 2024-11-01 to 2025-01-31
```

### Validation

Period objects automatically validate:
- `start < end` (enforced via model_validator)
- Valid date formats (string, date, datetime)
- Leap year handling in `from_month()`

**Example:**

```python
# Valid ✅
period = Period(start="2024-01-01", end="2024-12-31")

# Invalid: start >= end ❌
try:
    invalid = Period(start="2024-12-31", end="2024-01-01")
except ValueError as e:
    print(e)  # "Period start (2024-12-31) must be before end (2024-01-01)"
```

---

## BatchResults

Container for batch test results with lazy loading and background polling.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `batch_id` | str | Unique batch identifier |
| `task_ids` | list[str] | List of all task IDs |
| `task_count` | int | Total number of tasks |
| `completed_count` | int | Number of completed tasks |
| `failed_count` | int | Number of failed tasks |
| `progress` | float | Completion progress (0.0 - 1.0) |
| `is_completed` | bool | All tasks completed? |
| `strategies` | list[StrategyConfig] | Strategy configurations |
| `periods` | list[Period] | Period objects |

### Methods

#### `wait(timeout=None) -> None`

Block until all tasks complete or timeout.

**Parameters:**
- `timeout` (float | None): Max wait time in seconds (default: None = infinite)

**Raises:**
- `TaskTimeoutError`: Timeout exceeded before completion

**Example:**

```python
batch = tester.submit(strategies=[s1], periods=[Period.Q1(2024)])
batch.wait(timeout=600.0)  # Wait max 10 minutes

if batch.is_completed:
    print("All tasks completed")
```

#### `summary() -> pl.DataFrame`

Get aggregate performance summary across all periods.

**Returns:** Polars DataFrame with columns:
- `strategy` (str): Strategy name
- `total_pnl` (float): Total profit/loss
- `win_rate` (float): Proportion of winning trades
- `sharpe_ratio` (float): Risk-adjusted return
- `max_drawdown` (float): Maximum drawdown

**Example:**

```python
summary = batch.summary()
summary = summary.sort("total_pnl", descending=True)

print("Top strategies:")
print(summary.head(3).select(["strategy", "total_pnl", "win_rate"]))
```

#### `all_trades() -> pl.DataFrame`

Get all trades across all periods with period labels.

**Returns:** Polars DataFrame with columns:
- `entry_time` (datetime): Trade entry time
- `exit_time` (datetime): Trade exit time
- `entry_price` (float): Entry price
- `exit_price` (float): Exit price
- `pnl` (float): Profit/loss
- `period` (str): Period key (e.g., "2024-01-01_2024-03-31")
- ... (additional trade fields)

**Example:**

```python
all_trades = batch.all_trades()

# Filter Q1 trades
q1_trades = all_trades.filter(
    pl.col("period") == Period.Q1(2024).to_key()
)

print(f"Q1 PNL: {q1_trades['pnl'].sum():,.2f}")
```

#### `get_period(period: Period) -> PeriodResult`

Get results for specific period.

**Parameters:**
- `period` (Period): Period object to retrieve

**Returns:** `PeriodResult` object

**Raises:**
- `KeyError`: Period not found in batch

**Example:**

```python
q1_result = batch.get_period(Period.Q1(2024))
print(f"Q1 trades: {len(q1_result.trades)}")
print(f"Q1 PNL: {q1_result.trades['pnl'].sum():,.2f}")
```

---

## PeriodResult

Results for a single period.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `period` | Period | Period object |
| `trades` | pl.DataFrame | All trades in this period |
| `performance` | pl.DataFrame | Performance metrics by strategy |

### Example

```python
q1 = batch.get_period(Period.Q1(2024))

# Trades DataFrame
print(f"Total trades: {len(q1.trades)}")
print(f"Total PNL: {q1.trades['pnl'].sum():,.2f}")

# Performance DataFrame
print(q1.performance.select(["strategy", "total_pnl", "win_rate"]))
```

---

## StrategyBuilder

Fluent API for building strategy configurations.

### Initialization

```python
from tradepose_client import StrategyBuilder, Freq

builder = StrategyBuilder(
    name="MyStrategy",
    base_instrument="TXF_M1_SHIOAJI_FUTURE",
    base_freq=Freq.MIN_15
)
```

### Methods

#### `add_indicator(indicator_type, **kwargs) -> IndicatorSpecWrapper`

Add indicator to strategy.

**Parameters:**
- `indicator_type` (IndicatorType): Indicator type enum
- `**kwargs`: Indicator-specific parameters (period, multiplier, etc.)

**Returns:** `IndicatorSpecWrapper` for referencing indicator

**Example:**

```python
from tradepose_client import IndicatorType

atr = builder.add_indicator(
    IndicatorType.ATR,
    period=14,
    freq=Freq.DAY_1,
    shift=1,
    display_name="ATR_14"
)
```

#### `set_base_blueprint(blueprint: Blueprint) -> StrategyBuilder`

Set base trading blueprint.

**Parameters:**
- `blueprint` (Blueprint): Blueprint object

**Returns:** Self for chaining

#### `build(volatility_indicator=None) -> StrategyConfig`

Build final strategy configuration.

**Parameters:**
- `volatility_indicator` (IndicatorSpecWrapper | None): Volatility indicator for position sizing

**Returns:** `StrategyConfig` ready for backtesting

---

## BlueprintBuilder

Fluent API for building trading blueprints.

### Initialization

```python
from tradepose_client import BlueprintBuilder, TradeDirection, TrendType

blueprint_builder = BlueprintBuilder(
    name="trend_follow",
    direction=TradeDirection.LONG,
    trend_type=TrendType.TREND
)
```

### Methods

#### `add_entry_trigger(name, conditions, price_expr, order_strategy, priority) -> BlueprintBuilder`

Add entry trigger.

**Parameters:**
- `name` (str): Trigger name
- `conditions` (list[pl.Expr]): List of Polars conditions (AND logic)
- `price_expr` (pl.Expr): Price expression
- `order_strategy` (OrderStrategy): Entry order strategy
- `priority` (int): Trigger priority (lower = higher priority)

**Returns:** Self for chaining

#### `add_exit_trigger(name, conditions, price_expr, order_strategy, priority) -> BlueprintBuilder`

Add exit trigger (same signature as `add_entry_trigger`).

#### `build() -> Blueprint`

Build final blueprint.

**Returns:** `Blueprint` object

### Example

```python
import polars as pl
from tradepose_client import OrderStrategy

blueprint = (
    BlueprintBuilder(name="ma_cross", direction=TradeDirection.LONG, trend_type=TrendType.TREND)
    .add_entry_trigger(
        name="golden_cross",
        conditions=[sma_fast.col() > sma_slow.col()],
        price_expr=pl.col("close"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
        priority=1
    )
    .add_exit_trigger(
        name="death_cross",
        conditions=[sma_fast.col() < sma_slow.col()],
        price_expr=pl.col("close"),
        order_strategy=OrderStrategy.IMMEDIATE_EXIT,
        priority=1
    )
    .build()
)
```

---

## IndicatorSpecWrapper

Wrapper for referencing indicators in trigger conditions.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `spec` | IndicatorSpec | Underlying indicator specification |
| `display_name` | str | Indicator display name |

### Methods

#### `col() -> pl.Expr`

Get Polars column expression for indicator.

**Returns:** Polars expression referencing indicator column

**Example:**

```python
atr = builder.add_indicator(IndicatorType.ATR, period=14, freq=Freq.DAY_1, shift=1)
supertrend = builder.add_indicator(
    IndicatorType.SUPERTREND,
    multiplier=3.0,
    volatility_column=atr.display_name,  # Reference ATR
    freq=Freq.DAY_1,
    shift=1
)

# Use in trigger conditions
blueprint_builder.add_entry_trigger(
    name="supertrend_long",
    conditions=[
        supertrend.col().struct.field("direction") == 1,  # Access struct field
        pl.col("ts").dt.hour().is_between(1, 11)
    ],
    price_expr=pl.col("open"),
    order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
    priority=1
)
```

---

## TradePoseClient

**Low-Level API (Advanced Users)**

Async HTTP client for fine-grained control. Most users should use [BatchTester](#batchtester) instead.

For complete low-level API documentation, see [LOW_LEVEL_API.md](LOW_LEVEL_API.md).

### Initialization

```python
from tradepose_client import TradePoseClient

async with TradePoseClient(api_key="tp_live_xxx") as client:
    strategies = await client.strategies.list()
```

### Resources

Client organizes API endpoints into resources:

- `client.strategies` - Strategy management (list, register, get, delete)
- `client.export` - Data export (backtest results, OHLCV, trades)
- `client.tasks` - Task management (status, download)
- `client.api_keys` - API key management (create, list, revoke)
- `client.billing` - Billing & subscription (plans, usage)
- `client.usage` - Usage statistics

**See [LOW_LEVEL_API.md](LOW_LEVEL_API.md) for complete resource documentation.**

---

## Enums

### Freq

Time frequency enum for indicators and data.

```python
from tradepose_client import Freq

Freq.SEC_1    # 1 second
Freq.SEC_5    # 5 seconds
Freq.MIN_1    # 1 minute
Freq.MIN_5    # 5 minutes
Freq.MIN_15   # 15 minutes
Freq.HOUR_1   # 1 hour
Freq.DAY_1    # 1 day
```

### IndicatorType

Technical indicator types.

```python
from tradepose_client import IndicatorType

IndicatorType.SMA         # Simple Moving Average
IndicatorType.EMA         # Exponential Moving Average
IndicatorType.RSI         # Relative Strength Index
IndicatorType.ATR         # Average True Range
IndicatorType.SUPERTREND  # SuperTrend
# ... (additional indicators)
```

### OrderStrategy

Order execution strategies.

```python
from tradepose_client import OrderStrategy

OrderStrategy.IMMEDIATE_ENTRY  # Enter immediately on trigger
OrderStrategy.IMMEDIATE_EXIT   # Exit immediately on trigger
OrderStrategy.LIMIT_ENTRY      # Limit order entry
OrderStrategy.LIMIT_EXIT       # Limit order exit
```

### TradeDirection

Trade direction.

```python
from tradepose_client import TradeDirection

TradeDirection.LONG   # Long trades
TradeDirection.SHORT  # Short trades
```

### TrendType

Trend following vs mean reversion.

```python
from tradepose_client import TrendType

TrendType.TREND       # Trend following
TrendType.REVERSION   # Mean reversion
```

---

## Exception Hierarchy

All exceptions inherit from `TradePoseError`:

```python
TradePoseError
├── AuthenticationError      # 401 - Invalid API key
├── AuthorizationError       # 403 - Insufficient permissions
├── ResourceNotFoundError    # 404 - Resource not found
├── ValidationError          # 422 - Invalid parameters
├── RateLimitError          # 429 - Rate limit exceeded
├── ServerError             # 500 - Server error
├── TaskTimeoutError        # Task polling timeout
├── TaskExecutionError      # Task execution failed
└── NetworkError            # Connection failed
```

See [ERROR_HANDLING.md](ERROR_HANDLING.md) for complete exception reference.

---

## See Also

- [README.md](../README.md) - Project overview and quick start
- [EXAMPLES.md](EXAMPLES.md) - Real-world usage examples
- [LOW_LEVEL_API.md](LOW_LEVEL_API.md) - Complete async API documentation
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Exception handling guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions and data flow
