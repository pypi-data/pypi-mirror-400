# TradePose Client SDK

Python SDK for TradePose quantitative trading platform. Simple, type-safe, production-ready.

## What is this?

Official Python client for the TradePose trading platform API. Designed for quantitative traders, algo developers, and trading system architects who need:

- 🎯 **Simple synchronous API** - No async/await required, works out of the box
- 📊 **Batch testing** - Multi-strategy, multi-period backtesting with background polling
- 🔒 **Type safety** - Pydantic models, IDE autocomplete, compile-time validation
- 🎨 **Fluent builder API** - 60% less boilerplate for strategy construction
- 🔄 **Production-ready** - Comprehensive error handling, automatic retries, Jupyter support

## Installation

```bash
pip install tradepose-client
```

**Requirements:**
- Python 3.13+
- Dependencies: httpx, pydantic, polars, nest-asyncio

## Quick Start

### Batch Testing (Recommended)

Test multiple strategies across multiple periods - no async/await needed:

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Create tester
tester = BatchTester(api_key="tp_live_xxx")

# Submit batch (non-blocking, returns immediately)
batch = tester.submit(
    strategies=[strategy1, strategy2, strategy3],
    periods=[
        Period.Q1(2024),  # 2024-01-01 to 2024-03-31
        Period.Q2(2024),  # 2024-04-01 to 2024-06-30
        Period.Q3(2024),  # 2024-07-01 to 2024-09-30
    ]
)

print(f"Submitted {batch.task_count} tasks")
print(f"Progress: {batch.progress:.1%}")

# Wait for completion (blocking)
batch.wait()

# Access results (Polars DataFrames)
summary_df = batch.summary()  # Performance across all periods
all_trades_df = batch.all_trades()  # All trades with period column

# Period-specific results
q1 = batch.get_period(Period.Q1(2024))
print(f"Q1 trades: {len(q1.trades)}")
print(f"Q1 PNL: {q1.trades['pnl'].sum()}")
```

### Period Objects (Type-Safe Dates)

Use `Period` objects for type-safe date validation:

```python
from tradepose_client.batch import Period

# Quarterly testing
periods = [
    Period.Q1(2024),  # Jan-Mar
    Period.Q2(2024),  # Apr-Jun
    Period.Q3(2024),  # Jul-Sep
    Period.Q4(2024),  # Oct-Dec
]

# Full year
full_year = Period.from_year(2024)  # 2024-01-01 to 2024-12-31

# Single month
march = Period.from_month(2024, 3)  # 2024-03-01 to 2024-03-31

# Flexible multi-month ranges
three_months = Period.from_month(2024, 3, n_months=3)  # Mar-May 2024
half_year = Period.from_month(2024, 1, n_months=6)     # Jan-Jun 2024
winter = Period.from_month(2024, 11, n_months=3)       # Nov 2024 - Jan 2025

# Custom range
custom = Period(start="2024-01-15", end="2024-02-15")
```

**Benefits:**
- ✅ Compile-time type checking
- ✅ IDE autocomplete and validation
- ✅ Automatic validation (start < end)
- ✅ Clear error messages

### Strategy Builder

Build strategies with a fluent, type-safe API:

```python
from tradepose_client import (
    StrategyBuilder,
    BlueprintBuilder,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq
)
import polars as pl

# Create strategy builder
builder = StrategyBuilder(
    name="SuperTrend_Strategy",
    base_instrument="TXF_M1_SHIOAJI_FUTURE",
    base_freq=Freq.MIN_15
)

# Add indicators
atr = builder.add_indicator(
    IndicatorType.ATR,
    period=21,
    freq=Freq.DAY_1,
    shift=1
)

supertrend = builder.add_indicator(
    IndicatorType.SUPERTREND,
    multiplier=3.0,
    volatility_column=atr.display_name,
    freq=Freq.DAY_1,
    shift=1
)

# Build blueprint with entry/exit conditions
blueprint = (
    BlueprintBuilder(
        name="trend_follow",
        direction=TradeDirection.LONG,
        trend_type=TrendType.TREND
    )
    .add_entry_trigger(
        name="supertrend_long",
        conditions=[
            supertrend.col().struct.field("direction") == 1,
            pl.col("ts").dt.hour().is_between(1, 11)
        ],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
        priority=1
    )
    .add_exit_trigger(
        name="friday_exit",
        conditions=[
            (pl.col("ts").dt.weekday() == 4) &
            (pl.col("ts").dt.hour() == 23)
        ],
        price_expr=pl.col("open"),
        order_strategy=OrderStrategy.IMMEDIATE_EXIT,
        priority=1
    )
    .build()
)

# Build final strategy
strategy = builder.set_base_blueprint(blueprint).build(
    volatility_indicator=atr
)

# Use in backtest
tester = BatchTester(api_key="tp_live_xxx")
batch = tester.submit(
    strategies=[strategy],
    periods=[Period.from_year(2024)]
)
batch.wait()

trades_df = batch.all_trades()
print(f"Total PNL: {trades_df['pnl'].sum():,.2f}")
```

## Core Concepts

### Batch Testing API (Primary Interface)

`BatchTester` is the main way to interact with the platform:

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

tester = BatchTester(api_key="tp_live_xxx")

# Submit tasks
batch = tester.submit(
    strategies=[strategy1, strategy2],
    periods=[Period.Q1(2024), Period.Q2(2024)]
)

# Monitor progress
print(f"Progress: {batch.progress:.1%}")
print(f"Completed: {batch.completed_count}/{batch.task_count}")

# Wait for completion
batch.wait()  # Blocks until all tasks complete

# Access results
summary = batch.summary()  # Aggregate results
all_trades = batch.all_trades()  # All trades across periods

# Period-specific results
q1_result = batch.get_period(Period.Q1(2024))
print(f"Q1 trades: {len(q1_result.trades)}")
```

**Features:**
- **Synchronous interface** - No async/await required
- **Background polling** - Tasks execute in background, results auto-download
- **Type-safe dates** - Period objects with validation
- **Polars DataFrames** - High-performance data analysis
- **Jupyter-friendly** - Automatic event loop setup

### Low-Level API (Advanced Users)

For fine-grained control over HTTP connections, custom retry logic, or manual event loop management, see [Low-Level API Documentation](docs/LOW_LEVEL_API.md).

**Most users should use BatchTester** - it's simpler and handles async complexity automatically.

### Task Polling Pattern

Long-running operations return immediately with a task ID. Results are downloaded automatically in the background:

```python
# Submit returns immediately
batch = tester.submit(strategies=[strategy], periods=[Period.Q1(2024)])
print(f"Task ID: {batch.task_ids[0]}")  # Submitted

# Background polling starts automatically
# Do other work while tasks run...

# Wait when you need results
batch.wait()  # Blocks until completion

# Results ready
trades = batch.all_trades()
```

## Documentation

- 💡 **[Examples](docs/EXAMPLES.md)** - Real-world usage patterns (start here!)
- 📚 **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- 🔧 **[Low-Level API](docs/LOW_LEVEL_API.md)** - Advanced async API (for experts)
- ⚠️ **[Error Handling](docs/ERROR_HANDLING.md)** - Exception types and handling strategies
- ⚙️ **[Configuration](docs/CONFIGURATION.md)** - Environment variables, timeout settings
- 📐 **[Architecture](docs/ARCHITECTURE.md)** - Design decisions and data flow

## Features

### Current (Alpha)

#### Batch Testing API
- ✅ Multi-strategy, multi-period testing
- ✅ Background polling (daemon thread)
- ✅ Auto-download on completion
- ✅ Type-safe Period objects with validation
- ✅ Convenient constructors (Q1, Q2, from_year, from_month)
- ✅ Reactive results (lazy loading)
- ✅ Memory caching
- ✅ Jupyter support (nest_asyncio auto-applied)

#### Builder API
- ✅ Fluent strategy construction
- ✅ Type-safe indicator references
- ✅ 60% less boilerplate
- ✅ TradingContext convenience accessors
- ✅ Automatic field inheritance

#### Low-Level Client API
- ✅ Authentication (API key + JWT)
- ✅ Resource-based organization (6 resources, 21 methods)
- ✅ Async-first with HTTP/2
- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive error handling (18 exception types)
- ✅ Type-safe with Pydantic models

### Roadmap

- ⏳ Webhook support (replace polling)
- ⏳ GraphQL endpoint (reduce requests)
- ⏳ Result streaming (large datasets)

## Configuration

### Environment Variables

```bash
# Authentication (required, at least one)
export TRADEPOSE_API_KEY="tp_live_xxx"
export TRADEPOSE_JWT_TOKEN="eyJ..."

# Server (optional)
export TRADEPOSE_SERVER_URL="https://api.tradepose.com"

# HTTP (optional)
export TRADEPOSE_TIMEOUT="30.0"        # Request timeout (1.0 - 600.0s)
export TRADEPOSE_MAX_RETRIES="3"        # Max retry attempts (0 - 10)

# Task polling (optional)
export TRADEPOSE_POLL_INTERVAL="2.0"    # Poll interval (0.5 - 60.0s)
export TRADEPOSE_POLL_TIMEOUT="300.0"   # Max poll duration (10.0 - 3600.0s)

# Logging (optional)
export TRADEPOSE_DEBUG="false"
export TRADEPOSE_LOG_LEVEL="INFO"       # DEBUG/INFO/WARNING/ERROR/CRITICAL
```

### Configuration Methods

```python
# Method 1: Environment variables (recommended)
tester = BatchTester()  # Auto-loads from TRADEPOSE_API_KEY

# Method 2: Direct parameters
tester = BatchTester(
    api_key="tp_live_xxx",
    poll_interval=2.0,
    auto_download=True
)

# Method 3: Configuration file (see Configuration Guide)
```

See [Configuration Guide](docs/CONFIGURATION.md) for details.

## Error Handling

All exceptions inherit from `TradePoseError`:

```python
from tradepose_client import (
    BatchTester,
    AuthenticationError,
    RateLimitError,
    TaskTimeoutError,
    ValidationError
)
from tradepose_client.batch import Period

tester = BatchTester(api_key="tp_xxx")

try:
    batch = tester.submit(
        strategies=[strategy],
        periods=[Period.Q1(2024)]
    )
    batch.wait(timeout=600.0)

except AuthenticationError:
    # Invalid API key
    print("Authentication failed")

except ValidationError as e:
    # Invalid Period or strategy configuration
    print(f"Validation error: {e.errors}")

except RateLimitError as e:
    # Rate limit exceeded
    print(f"Rate limited. Wait {e.retry_after}s")

except TaskTimeoutError as e:
    # Task didn't complete in time
    print(f"Timeout. Task ID: {e.task_id}")
```

See [Error Handling Guide](docs/ERROR_HANDLING.md) for complete reference.

## Period Validation

Period objects automatically validate date ranges:

```python
from tradepose_client.batch import Period

# Valid period
period = Period(start="2024-01-01", end="2024-12-31")  # ✅ OK

# Invalid period (start >= end)
try:
    period = Period(start="2024-12-31", end="2024-01-01")  # ❌ Error
except ValueError as e:
    print(e)  # "Period start (2024-12-31) must be before end (2024-01-01)"

# Invalid date format
try:
    period = Period(start="invalid", end="2024-12-31")  # ❌ Error
except ValueError as e:
    print(e)  # "Cannot parse datetime from type..."
```

## Migration from Tuple-Based Periods

**Before (deprecated):**
```python
# ❌ No longer supported
batch = tester.submit(
    strategies=[strategy],
    periods=[("2024-01-01", "2024-12-31")]  # Tuple not accepted
)
```

**After (type-safe):**
```python
# ✅ Required: Use Period objects
from tradepose_client.batch import Period

batch = tester.submit(
    strategies=[strategy],
    periods=[Period(start="2024-01-01", end="2024-12-31")]
)

# ✅ Even better: Use convenience constructors
batch = tester.submit(
    strategies=[strategy],
    periods=[Period.from_year(2024)]  # Clearer and type-safe
)
```

**This is a Breaking Change in version 0.2.0+**. Update your code to use `Period` objects.

## Development Status

**Alpha** - API is stable but subject to minor changes. Production use at your own risk.

## Python Version Support

Requires Python 3.13+ to leverage:
- Type parameter syntax (`[T]`)
- `Self` type hint
- Performance improvements

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tradepose/tradepose-gateway/issues)
- **Email**: support@tradepose.com
