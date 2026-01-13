# Real-World Usage Examples

Complete, runnable examples for common TradePose Client SDK scenarios. All examples use the recommended BatchTester API with type-safe Period objects.

## Table of Contents

1. [Period Object Usage](#period-object-usage)
2. [Basic Batch Testing](#basic-batch-testing)
3. [Strategy Management](#strategy-management)
4. [Multi-Period Testing](#multi-period-testing)
5. [Parameter Optimization](#parameter-optimization)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Builder API Complete Examples](#builder-api-complete-examples)

**Note:** For low-level async API examples, see [LOW_LEVEL_API.md](LOW_LEVEL_API.md).

---

## Period Object Usage

### Example 1: Period Convenience Constructors

**Scenario:** Create periods using convenient constructors for common date ranges

```python
from tradepose_client.batch import Period

# Quarterly testing
periods = [
    Period.Q1(2024),  # 2024-01-01 to 2024-03-31
    Period.Q2(2024),  # 2024-04-01 to 2024-06-30
    Period.Q3(2024),  # 2024-07-01 to 2024-09-30
    Period.Q4(2024),  # 2024-10-01 to 2024-12-31
]

# Full year testing
full_year = Period.from_year(2024)  # 2024-01-01 to 2024-12-31

# Monthly testing
months = [
    Period.from_month(2024, 1),   # January 2024
    Period.from_month(2024, 2),   # February 2024 (handles leap year)
    Period.from_month(2024, 3),   # March 2024
]

# Flexible multi-month ranges
three_months = Period.from_month(2024, 3, n_months=3)  # Mar-May 2024
six_months = Period.from_month(2024, 1, n_months=6)    # Jan-Jun 2024 (half year)
cross_year = Period.from_month(2024, 11, n_months=3)   # Nov 2024 - Jan 2025

# Custom date range
custom = Period(start="2024-01-15", end="2024-02-15")

# Access period data
print(f"Q1 start: {Period.Q1(2024).start}")  # datetime object
print(f"Q1 end: {Period.Q1(2024).end}")      # datetime object
print(f"Q1 key: {Period.Q1(2024).to_key()}")  # "2024-01-01_2024-03-31"
```

**Benefits:**
- Type-safe with IDE autocomplete
- Automatic validation (start < end)
- Clear, self-documenting code
- No string manipulation errors

---

### Example 2: Period Validation

**Scenario:** Period objects automatically validate date ranges

```python
from tradepose_client.batch import Period

# Valid period ✅
period = Period(start="2024-01-01", end="2024-12-31")
print("Valid period created")

# Invalid period: start >= end ❌
try:
    invalid = Period(start="2024-12-31", end="2024-01-01")
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: "Period start (2024-12-31) must be before end (2024-01-01)"

# Invalid date format ❌
try:
    invalid = Period(start="not-a-date", end="2024-12-31")
except ValueError as e:
    print(f"Parse error: {e}")
    # Output: "Cannot parse datetime from type..."

# Invalid month ❌
try:
    invalid = Period.from_month(2024, 13)  # Month must be 1-12
except ValueError as e:
    print(f"Month error: {e}")
    # Output: "Month must be between 1 and 12, got 13"

# Invalid n_months ❌
try:
    invalid = Period.from_month(2024, 1, n_months=0)  # Must be >= 1
except ValueError as e:
    print(f"n_months error: {e}")
    # Output: "n_months must be at least 1, got 0"
```

**Key Features:**
- Automatic leap year detection
- Cross-year boundary handling (e.g., Nov 2024 - Jan 2025)
- Flexible multi-month ranges with `n_months` parameter
- Clear error messages for debugging

---

## Basic Batch Testing

### Example 3: Simple Batch Test

**Scenario:** Test a single strategy across one period

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Create strategy (see Builder API examples for details)
strategy = build_my_strategy()

# Create tester
tester = BatchTester(api_key="tp_live_xxx")

# Submit batch
batch = tester.submit(
    strategies=[strategy],
    periods=[Period.from_year(2024)]
)

print(f"Submitted {batch.task_count} task(s)")

# Wait for completion
batch.wait()

# Get results
trades = batch.all_trades()
print(f"Total trades: {len(trades)}")
print(f"Total PNL: {trades['pnl'].sum():,.2f}")
print(f"Win rate: {(trades['pnl'] > 0).mean():.1%}")
```

**Output:**
```
Submitted 1 task(s)
Total trades: 245
Total PNL: 123,456.78
Win rate: 58.4%
```

---

### Example 4: Multiple Strategies, Single Period

**Scenario:** Compare multiple strategies over the same period

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Create strategies
supertrend = build_supertrend_strategy()
ma_crossover = build_ma_crossover_strategy()
rsi_reversal = build_rsi_strategy()

# Test all strategies on same period
tester = BatchTester()
batch = tester.submit(
    strategies=[supertrend, ma_crossover, rsi_reversal],
    periods=[Period.from_year(2024)]
)

print(f"Testing {len(batch.strategies)} strategies")
batch.wait()

# Compare results
summary = batch.summary()
summary = summary.sort("total_pnl", descending=True)

print("\nStrategy Performance:")
for row in summary.iter_rows(named=True):
    print(f"{row['strategy']}: PNL={row['total_pnl']:,.2f}, Win Rate={row['win_rate']:.1%}")
```

**Output:**
```
Testing 3 strategies
Strategy Performance:
SuperTrend: PNL=156,789.00, Win Rate=62.3%
MA_CrossOver: PNL=98,234.50, Win Rate=55.1%
RSI_Reversal: PNL=45,678.90, Win Rate=48.7%
```

---

## Strategy Management

### Example 5: Register and Test Strategy

**Scenario:** Register a new strategy and immediately test it

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Register strategy first (using low-level API)
from tradepose_client import TradePoseClient
import asyncio

async def register_strategy():
    with open("my_strategy.py") as f:
        strategy_code = f.read()

    async with TradePoseClient() as client:
        await client.strategies.register(
            strategy_code=strategy_code,
            poll=True  # Wait for compilation
        )

asyncio.run(register_strategy())

# Now test the registered strategy
tester = BatchTester()
batch = tester.submit(
    strategies=[strategy_config],
    periods=[Period.Q1(2024), Period.Q2(2024)]
)

batch.wait()
print(f"Q1 PNL: {batch.get_period(Period.Q1(2024)).trades['pnl'].sum():,.2f}")
print(f"Q2 PNL: {batch.get_period(Period.Q2(2024)).trades['pnl'].sum():,.2f}")
```

---

## Multi-Period Testing

### Example 6: Walk-Forward Analysis

**Scenario:** Test strategy across sequential quarters to assess consistency

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

strategy = build_supertrend_strategy()

# Test across all four quarters
tester = BatchTester()
batch = tester.submit(
    strategies=[strategy],
    periods=[
        Period.Q1(2024),
        Period.Q2(2024),
        Period.Q3(2024),
        Period.Q4(2024)
    ]
)

print(f"Submitted {batch.task_count} tasks")
batch.wait()

# Analyze each period
print("\nQuarterly Performance:")
for period in batch.periods:
    result = batch.get_period(period)
    trades = result.trades

    quarter_name = period.to_key().replace("2024-", "").replace("-01_2024-", " to ")
    total_pnl = trades['pnl'].sum()
    trade_count = len(trades)
    win_rate = (trades['pnl'] > 0).mean()

    print(f"{quarter_name}:")
    print(f"  Trades: {trade_count}")
    print(f"  PNL: {total_pnl:,.2f}")
    print(f"  Win Rate: {win_rate:.1%}")

# Overall summary
all_trades = batch.all_trades()
print(f"\nYearly Total:")
print(f"  Total PNL: {all_trades['pnl'].sum():,.2f}")
print(f"  Avg Win Rate: {(all_trades['pnl'] > 0).mean():.1%}")
```

**Output:**
```
Submitted 4 tasks
Quarterly Performance:
01-01 to 03-31:
  Trades: 58
  PNL: 34,567.00
  Win Rate: 62.1%
04-01 to 06-30:
  Trades: 62
  PNL: 41,234.50
  Win Rate: 59.7%
07-01 to 09-30:
  Trades: 55
  PNL: 28,901.20
  Win Rate: 54.5%
10-01 to 12-31:
  Trades: 70
  PNL: 52,086.30
  Win Rate: 64.3%

Yearly Total:
  Total PNL: 156,789.00
  Avg Win Rate: 60.4%
```

---

### Example 7: Monthly Granular Analysis

**Scenario:** Test strategy at monthly granularity for detailed analysis

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

strategy = build_ma_crossover_strategy()

# Generate all 12 months
periods = [Period.from_month(2024, month) for month in range(1, 13)]

tester = BatchTester()
batch = tester.submit(strategies=[strategy], periods=periods)

print(f"Testing {len(periods)} months...")
batch.wait()

# Find best and worst months
import polars as pl

monthly_results = []
for period in periods:
    result = batch.get_period(period)
    pnl = result.trades['pnl'].sum()
    monthly_results.append({
        'month': period.start.strftime('%B'),
        'pnl': pnl,
        'trades': len(result.trades)
    })

df = pl.DataFrame(monthly_results)
df = df.sort('pnl', descending=True)

print("\nMonthly Performance:")
print(df)

print(f"\nBest month: {df['month'][0]} (PNL: {df['pnl'][0]:,.2f})")
print(f"Worst month: {df['month'][-1]} (PNL: {df['pnl'][-1]:,.2f})")
```

---

### Example 8: Custom Period Comparison

**Scenario:** Test strategy across custom date ranges

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

strategy = build_rsi_strategy()

# Define custom periods (e.g., market regimes)
periods = [
    Period(start="2024-01-01", end="2024-02-15"),  # Bull market
    Period(start="2024-02-16", end="2024-04-30"),  # Correction
    Period(start="2024-05-01", end="2024-08-15"),  # Sideways
    Period(start="2024-08-16", end="2024-12-31"),  # Recovery
]

tester = BatchTester()
batch = tester.submit(strategies=[strategy], periods=periods)
batch.wait()

# Compare regime performance
print("Performance by Market Regime:")
for idx, period in enumerate(periods, 1):
    result = batch.get_period(period)
    pnl = result.trades['pnl'].sum()
    print(f"Period {idx} ({period.to_key()}): PNL={pnl:,.2f}")
```

---

## Parameter Optimization

### Example 9: Optimize SuperTrend Multiplier

**Scenario:** Test different SuperTrend multipliers to find optimal parameter

```python
from tradepose_client import BatchTester, StrategyBuilder, IndicatorType, Freq
from tradepose_client.batch import Period

# Test multipliers from 2.0 to 4.0 in steps of 0.5
multipliers = [2.0, 2.5, 3.0, 3.5, 4.0]
strategies = []

for mult in multipliers:
    builder = StrategyBuilder(
        name=f"SuperTrend_M{mult}",
        base_instrument="TXF_M1_SHIOAJI_FUTURE",
        base_freq=Freq.MIN_15
    )

    atr = builder.add_indicator(IndicatorType.ATR, period=14, freq=Freq.DAY_1, shift=1)
    supertrend = builder.add_indicator(
        IndicatorType.SUPERTREND,
        multiplier=mult,  # Variable parameter
        volatility_column=atr.display_name,
        freq=Freq.DAY_1,
        shift=1
    )

    # Add blueprint (simplified for brevity)
    strategy = builder.build(volatility_indicator=atr.col())
    strategies.append(strategy)

# Test all variants
tester = BatchTester()
batch = tester.submit(
    strategies=strategies,
    periods=[Period.from_year(2024)]
)

print(f"Testing {len(multipliers)} parameter combinations...")
batch.wait()

# Find best parameter
summary = batch.summary()
summary = summary.sort("total_pnl", descending=True)

print("\nOptimization Results:")
print(summary.select(["strategy", "total_pnl", "win_rate", "max_drawdown"]))

best = summary.head(1)
print(f"\nBest multiplier: {best['strategy'][0]}")
print(f"PNL: {best['total_pnl'][0]:,.2f}")
print(f"Win Rate: {best['win_rate'][0]:.1%}")
```

**Output:**
```
Testing 5 parameter combinations...
Optimization Results:
┌─────────────────┬────────────┬──────────┬──────────────┐
│ strategy        │ total_pnl  │ win_rate │ max_drawdown │
├─────────────────┼────────────┼──────────┼──────────────┤
│ SuperTrend_M3.0 │ 156789.00  │ 0.604    │ -23456.00    │
│ SuperTrend_M2.5 │ 142345.00  │ 0.587    │ -21234.00    │
│ SuperTrend_M3.5 │ 134567.00  │ 0.621    │ -28901.00    │
│ SuperTrend_M4.0 │ 123456.00  │ 0.634    │ -31245.00    │
│ SuperTrend_M2.0 │ 98765.00   │ 0.543    │ -19876.00    │
└─────────────────┴────────────┴──────────┴──────────────┘

Best multiplier: SuperTrend_M3.0
PNL: 156,789.00
Win Rate: 60.4%
```

---

### Example 10: Multi-Dimensional Grid Search

**Scenario:** Optimize two parameters simultaneously (MA periods)

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Grid search: fast MA (5, 10, 20) × slow MA (30, 50, 100)
fast_periods = [5, 10, 20]
slow_periods = [30, 50, 100]

strategies = []
for fast in fast_periods:
    for slow in slow_periods:
        if fast >= slow:
            continue  # Skip invalid combinations

        strategy = build_ma_crossover_strategy(fast_period=fast, slow_period=slow)
        strategies.append(strategy)

print(f"Grid search: {len(strategies)} combinations")

tester = BatchTester()
batch = tester.submit(
    strategies=strategies,
    periods=[Period.from_year(2024)]
)
batch.wait()

# Find optimal parameters
summary = batch.summary()
summary = summary.with_columns([
    pl.col("strategy").str.extract(r"MA_(\d+)_(\d+)").alias("params")
])
summary = summary.sort("total_pnl", descending=True)

print("\nTop 5 Combinations:")
print(summary.head(5).select(["strategy", "total_pnl", "win_rate"]))
```

---

### Example 11: Matrix Testing (Strategies × Periods)

**Scenario:** Test multiple strategies across multiple periods (full matrix)

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# 3 strategies
strategies = [
    build_supertrend_strategy(),
    build_ma_crossover_strategy(),
    build_rsi_strategy()
]

# 4 quarters
periods = [
    Period.Q1(2024),
    Period.Q2(2024),
    Period.Q3(2024),
    Period.Q4(2024)
]

# Submit 3 × 4 = 12 tasks
tester = BatchTester()
batch = tester.submit(strategies=strategies, periods=periods)

print(f"Matrix test: {len(strategies)} strategies × {len(periods)} periods = {batch.task_count} tasks")

# Monitor progress
import time
while not batch.is_completed:
    print(f"Progress: {batch.progress:.1%} ({batch.completed_count}/{batch.task_count})")
    time.sleep(5)

batch.wait()

# Analyze by strategy
summary = batch.summary()

for strategy_name in [s.name for s in strategies]:
    strategy_results = summary.filter(pl.col("strategy") == strategy_name)

    total_pnl = strategy_results["total_pnl"].sum()
    avg_win_rate = strategy_results["win_rate"].mean()

    print(f"\n{strategy_name}:")
    print(f"  Total PNL (all periods): {total_pnl:,.2f}")
    print(f"  Avg win rate: {avg_win_rate:.1%}")
    print(f"  Consistency: {strategy_results['total_pnl'].std():.2f} (lower is better)")
```

**Output:**
```
Matrix test: 3 strategies × 4 periods = 12 tasks
Progress: 25.0% (3/12)
Progress: 50.0% (6/12)
Progress: 75.0% (9/12)
Progress: 100.0% (12/12)

SuperTrend_Long:
  Total PNL (all periods): 156,789.00
  Avg win rate: 60.4%
  Consistency: 9234.56 (lower is better)

MA_CrossOver:
  Total PNL (all periods): 98,234.50
  Avg win rate: 55.1%
  Consistency: 12456.78

RSI_Reversal:
  Total PNL (all periods): 45,678.90
  Avg win rate: 48.7%
  Consistency: 15678.90
```

---

## Error Handling Patterns

### Example 12: Graceful Error Handling

**Scenario:** Handle errors during batch testing without stopping entire workflow

```python
from tradepose_client import (
    BatchTester,
    ValidationError,
    TaskTimeoutError,
    RateLimitError
)
from tradepose_client.batch import Period
import time

tester = BatchTester()

try:
    # Attempt batch submission
    batch = tester.submit(
        strategies=[strategy1, strategy2],
        periods=[Period.Q1(2024), Period.Q2(2024)]
    )

    print(f"Submitted {batch.task_count} tasks")

    # Wait with timeout
    batch.wait(timeout=600.0)

    # Check results
    if batch.is_completed:
        summary = batch.summary()
        print(f"All tasks completed successfully")
        print(f"Total PNL: {summary['total_pnl'].sum():,.2f}")
    else:
        print(f"Warning: {batch.failed_count} tasks failed")
        # Continue with partial results
        if batch.completed_count > 0:
            summary = batch.summary()
            print(f"Partial results: {len(summary)} periods completed")

except ValidationError as e:
    print(f"Invalid configuration: {e.errors}")
    # Fix configuration and retry

except RateLimitError as e:
    wait_time = e.retry_after or 60
    print(f"Rate limited. Waiting {wait_time}s...")
    time.sleep(wait_time)
    # Retry batch submission

except TaskTimeoutError as e:
    print(f"Task {e.task_id} timed out after {e.timeout}s")
    # Check task status manually or continue with other results
```

---

### Example 13: Retry with Exponential Backoff

**Scenario:** Retry failed batch submissions with exponential backoff

```python
from tradepose_client import BatchTester, RateLimitError, NetworkError
from tradepose_client.batch import Period
import time

def submit_with_retry(tester, strategies, periods, max_retries=3):
    """Submit batch with retry logic."""
    for attempt in range(max_retries):
        try:
            batch = tester.submit(strategies=strategies, periods=periods)
            print(f"Submitted successfully on attempt {attempt + 1}")
            return batch

        except RateLimitError as e:
            wait_time = e.retry_after if e.retry_after else (2 ** attempt)
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)

        except NetworkError as e:
            if attempt == max_retries - 1:
                raise  # Final attempt, give up

            wait_time = 2 ** attempt
            print(f"Network error. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)

    raise Exception(f"Failed after {max_retries} retries")

# Usage
tester = BatchTester()
batch = submit_with_retry(
    tester,
    strategies=[strategy],
    periods=[Period.from_year(2024)]
)
batch.wait()
```

---

## Builder API Complete Examples

### Example 14: SuperTrend Strategy (Complete)

**Scenario:** Build a complete trend-following strategy with SuperTrend indicator

```python
from tradepose_client import (
    BatchTester,
    StrategyBuilder,
    BlueprintBuilder,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq
)
from tradepose_client.batch import Period
import polars as pl

def build_supertrend_strategy():
    """Complete SuperTrend long strategy."""

    builder = StrategyBuilder(
        name="SuperTrend_Long_Complete",
        base_instrument="TXF_M1_SHIOAJI_FUTURE",
        base_freq=Freq.MIN_15
    )

    # Add indicators
    atr = builder.add_indicator(
        IndicatorType.ATR,
        period=21,
        freq=Freq.DAY_1,
        shift=1,
        display_name="ATR_21D"
    )

    supertrend = builder.add_indicator(
        IndicatorType.SUPERTREND,
        multiplier=3.0,
        volatility_column=atr.display_name,
        freq=Freq.DAY_1,
        shift=1,
        display_name="SuperTrend_3x"
    )

    # Build blueprint
    blueprint = (
        BlueprintBuilder(
            name="trend_follow",
            direction=TradeDirection.LONG,
            trend_type=TrendType.TREND
        )
        .add_entry_trigger(
            name="supertrend_long",
            conditions=[
                supertrend.col().struct.field("direction") == 1,  # Bullish
                pl.col("ts").dt.hour().is_between(1, 11)  # Avoid overnight
            ],
            price_expr=pl.col("open"),
            order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
            priority=1
        )
        .add_exit_trigger(
            name="supertrend_exit",
            conditions=[
                supertrend.col().struct.field("direction") == -1  # Bearish
            ],
            price_expr=pl.col("open"),
            order_strategy=OrderStrategy.IMMEDIATE_EXIT,
            priority=1
        )
        .add_exit_trigger(
            name="friday_exit",
            conditions=[
                (pl.col("ts").dt.weekday() == 4) &  # Friday
                (pl.col("ts").dt.hour() == 23)
            ],
            price_expr=pl.col("open"),
            order_strategy=OrderStrategy.IMMEDIATE_EXIT,
            priority=2
        )
        .build()
    )

    return builder.set_base_blueprint(blueprint).build(volatility_indicator=atr.col())

# Test strategy
strategy = build_supertrend_strategy()

tester = BatchTester()
batch = tester.submit(
    strategies=[strategy],
    periods=[Period.from_year(2024)]
)
batch.wait()

trades = batch.all_trades()
print(f"Total trades: {len(trades)}")
print(f"Total PNL: {trades['pnl'].sum():,.2f}")
print(f"Win rate: {(trades['pnl'] > 0).mean():.1%}")
```

---

### Example 15: MA Crossover Strategy (Complete)

**Scenario:** Classic moving average crossover with volume filter

```python
from tradepose_client import (
    BatchTester,
    StrategyBuilder,
    BlueprintBuilder,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
    Freq
)
from tradepose_client.batch import Period
import polars as pl

def build_ma_crossover_strategy(fast_period=20, slow_period=50):
    """Moving average crossover with volume confirmation."""

    builder = StrategyBuilder(
        name=f"MA_CrossOver_{fast_period}_{slow_period}",
        base_instrument="TXF_M1_SHIOAJI_FUTURE",
        base_freq=Freq.MIN_5
    )

    # Add indicators
    atr = builder.add_indicator(IndicatorType.ATR, period=14, freq=Freq.HOUR_1, shift=1)

    sma_fast = builder.add_indicator(
        IndicatorType.SMA,
        period=fast_period,
        freq=Freq.MIN_5,
        shift=1,
        display_name=f"SMA_{fast_period}"
    )

    sma_slow = builder.add_indicator(
        IndicatorType.SMA,
        period=slow_period,
        freq=Freq.MIN_5,
        shift=1,
        display_name=f"SMA_{slow_period}"
    )

    volume_sma = builder.add_indicator(
        IndicatorType.SMA,
        period=20,
        column="volume",
        freq=Freq.MIN_5,
        shift=1,
        display_name="Volume_SMA_20"
    )

    # Long blueprint
    blueprint = (
        BlueprintBuilder(
            name="ma_cross_long",
            direction=TradeDirection.LONG,
            trend_type=TrendType.TREND
        )
        .add_entry_trigger(
            name="golden_cross",
            conditions=[
                sma_fast.col() > sma_slow.col(),
                sma_fast.col().shift(1) <= sma_slow.col().shift(1),
                pl.col("volume") > volume_sma.col() * 1.2
            ],
            price_expr=pl.col("close"),
            order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
            priority=1
        )
        .add_exit_trigger(
            name="death_cross",
            conditions=[
                sma_fast.col() < sma_slow.col(),
                sma_fast.col().shift(1) >= sma_slow.col().shift(1)
            ],
            price_expr=pl.col("close"),
            order_strategy=OrderStrategy.IMMEDIATE_EXIT,
            priority=1
        )
        .build()
    )

    return builder.set_base_blueprint(blueprint).build(volatility_indicator=atr.col())

# Test strategy
strategy = build_ma_crossover_strategy(fast_period=20, slow_period=50)

tester = BatchTester()
batch = tester.submit(
    strategies=[strategy],
    periods=[Period.Q1(2024), Period.Q2(2024)]
)
batch.wait()

# Compare quarters
for period in [Period.Q1(2024), Period.Q2(2024)]:
    result = batch.get_period(period)
    pnl = result.trades['pnl'].sum()
    print(f"{period.to_key()}: PNL={pnl:,.2f}")
```

---

## Summary

This document provides **15 complete, production-ready examples** covering:

1. **Period Objects** - Type-safe date construction and validation
2. **Basic Batch Testing** - Single and multi-strategy workflows
3. **Multi-Period Testing** - Walk-forward, monthly, custom ranges
4. **Parameter Optimization** - Single and multi-dimensional grid search
5. **Error Handling** - Graceful failures and retry patterns
6. **Builder API** - Complete strategy construction examples

**All examples use:**
- ✅ BatchTester (synchronous, simple)
- ✅ Period objects (type-safe)
- ✅ Best practices (error handling, validation)
- ✅ Production patterns (monitoring, logging)

For low-level async API examples, see [LOW_LEVEL_API.md](LOW_LEVEL_API.md).
