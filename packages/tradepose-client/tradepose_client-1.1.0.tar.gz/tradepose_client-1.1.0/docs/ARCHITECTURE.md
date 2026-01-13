# Architecture

Design decisions, module relationships, and data flow for TradePose Client SDK.

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Key Design Decisions](#key-design-decisions)
5. [Performance Considerations](#performance-considerations)

---

## Design Philosophy

### Simple by Default, Powerful When Needed

**Primary Interface:** BatchTester provides a simple, synchronous API for common workflows.

**Low-Level Interface:** TradePoseClient offers async control for advanced use cases.

**Why this layering?**
- **90% of users** need batch testing with type-safe dates → BatchTester + Period
- **10% of users** need custom async workflows → TradePoseClient
- **Design principle:** Make simple things simple, complex things possible

### Type Safety First

**Problem:** String-based dates cause runtime errors:
```python
# Unsafe ❌
periods = [("2024-12-31", "2024-01-01")]  # Wrong order, no compile-time check
```

**Solution:** Pydantic-validated Period objects:
```python
# Safe ✅
period = Period(start="2024-01-01", end="2024-12-31")  # Validated at creation
period = Period.Q1(2024)  # Even safer with convenience constructors
```

**Benefits:**
- **Compile-time safety:** IDE catches errors before runtime
- **Clear error messages:** "Period start must be before end"
- **Self-documenting:** `Period.Q1(2024)` vs `("2024-01-01", "2024-03-31")`

### Async Under the Hood, Sync on Top

**Architecture:** BatchTester wraps async TradePoseClient with background polling.

**User experience:**
```python
# User sees synchronous API
tester = BatchTester()
batch = tester.submit(strategies=[s1], periods=[Period.Q1(2024)])
batch.wait()  # Blocks until complete
trades = batch.all_trades()
```

**Under the hood:**
- Background thread runs separate event loop
- Async tasks poll API in parallel
- Results auto-download on completion
- Jupyter compatibility via nest-asyncio

**Why?**
- Most users don't need async complexity
- Batch testing is inherently long-running (minutes to hours)
- Background polling is natural for this use case

---

## Core Components

### 1. BatchTester (Primary Interface)

High-level batch testing API with automatic background polling.

**Responsibilities:**
- Submit multiple strategies × periods (N × M tasks)
- Background polling in daemon thread
- Automatic result downloading
- Jupyter support (auto-detect and apply nest-asyncio)

**Architecture:**
```
BatchTester
    ↓
BackgroundPoller (daemon thread)
    ↓
TradePoseClient (async HTTP)
    ↓
Gateway API
```

**Key classes:**
- `BatchTester` - Main entry point
- `BatchResults` - Result container with lazy loading
- `PeriodResult` - Single period result wrapper
- `BackgroundPoller` - Daemon thread polling tasks
- `ResultCache` - Memory cache for downloaded results

**Example:**
```python
tester = BatchTester(api_key="tp_xxx")
batch = tester.submit(strategies=[s1, s2], periods=[Period.Q1(2024), Period.Q2(2024)])
# 2 strategies × 2 periods = 4 tasks submitted
# Background polling starts automatically
batch.wait()  # Block until all 4 tasks complete
```

### 2. Period (Type-Safe Dates)

Pydantic model for time period validation.

**Responsibilities:**
- Validate date formats (string, date, datetime)
- Enforce start < end constraint
- Provide convenience constructors (Q1-Q4, from_year, from_month)
- Convert to API format (ISO strings)

**Validation chain:**
```
Period(start="2024-01-01", end="2024-12-31")
    ↓ field_validator (parse dates)
    ↓ model_validator (check start < end)
    ↓ Validated Period object
```

**Convenience constructors:**
- `Period.Q1(2024)` → 2024-01-01 to 2024-03-31
- `Period.from_year(2024)` → Full year
- `Period.from_month(2024, 3)` → March 2024 (handles leap years)

### 3. TradePoseClient (Low-Level Interface)

Async HTTP client for fine-grained control.

**Responsibilities:**
- HTTP/2 connection management
- Authentication (API key, JWT)
- Retry with exponential backoff
- Task polling (manual or automatic)
- Resource-based API organization

**Resource structure:**
```python
TradePoseClient
├── strategies: StrategiesResource
├── export: ExportResource
├── tasks: TasksResource
├── api_keys: APIKeysResource
├── billing: BillingResource
└── usage: UsageResource
```

**When to use:**
- Custom async workflows
- Integration with FastAPI/aiohttp
- Fine-grained HTTP control
- Single-operation use cases

### 4. Builder API

Fluent API for strategy construction.

**Components:**
- `StrategyBuilder` - Build strategy configurations
- `BlueprintBuilder` - Build trading blueprints
- `IndicatorSpecWrapper` - Type-safe indicator references

**Design pattern:** Method chaining for readability
```python
strategy = (
    StrategyBuilder(name="MA", base_instrument="TXF", base_freq=Freq.MIN_15)
    .add_indicator(IndicatorType.SMA, period=20)
    .set_base_blueprint(blueprint)
    .build()
)
```

### 5. Model Reuse (tradepose_models)

Shared Pydantic models across gateway, client, and workers.

**Shared types:**
- Enums: TaskStatus, ExportType, IndicatorType, Freq
- Strategy models: StrategyConfig, Blueprint, Trigger
- Export models: ExportTaskResponse, ResultSummary
- Schemas: trades_schema, performance_schema

**Benefits:**
- Type safety at every boundary
- Single source of truth
- Automatic validation
- Self-documenting

---

## Data Flow

### Pattern 1: Batch Testing (Primary Flow)

```
User Code
    ↓
BatchTester.submit(strategies, periods)
    ↓
Create BacktestRequest (validates Period objects)
    ↓
BackgroundPoller (daemon thread with separate event loop)
    ↓
    ├─> TradePoseClient.export.export_backtest_results() [async]
    │       ↓
    │   Gateway API POST /api/v1/export/backtest
    │       ↓
    │   Task created, task_id returned
    │       ↓
    │   Poll GET /api/v1/tasks/{task_id} (every 2s)
    │       ↓
    │   Status: pending → processing → completed
    │       ↓
    │   Auto-download GET /api/v1/tasks/{task_id}/result
    │
    └─> Store in ResultCache
            ↓
User calls batch.summary() / batch.all_trades()
    ↓
Read from ResultCache (Polars DataFrames)
```

**Key points:**
- Returns immediately (< 100ms)
- Background polling automatic
- Results lazy-loaded
- Memory cached

### Pattern 2: Period Validation Flow

```
User creates Period object
    ↓
Period(start="2024-01-01", end="2024-12-31")
    ↓
field_validator: parse_datetime()
    ├─> Parse "2024-01-01" → datetime(2024, 1, 1)
    └─> Parse "2024-12-31" → datetime(2024, 12, 31)
    ↓
model_validator: validate_period_order()
    ├─> Check: start < end
    └─> Raise ValueError if start >= end
    ↓
Validated Period object ready for use
```

**Validation guarantees:**
- start < end (enforced)
- Valid date formats (string, date, datetime)
- ISO 8601 compatible

### Pattern 3: Async Task Polling (Low-Level)

```
User Code (async)
    ↓
client.export.export_backtest_results(poll=True)
    ↓
POST /api/v1/export/backtest
    ↓ (< 100ms)
ExportTaskResponse(task_id="abc123", status="pending")
    ↓
Auto-polling loop (if poll=True):
    while status not in ["completed", "failed"]:
        GET /api/v1/tasks/abc123
        await asyncio.sleep(poll_interval)
    ↓
GET /api/v1/tasks/abc123/result (download Parquet)
    ↓
Convert to Polars DataFrame
    ↓
Return BacktestExportResponse(trades=df, performance=df)
```

**Low-level control:**
- Manual polling with `poll=False`
- Custom poll intervals
- Timeout handling
- Concurrent task submission

---

## Key Design Decisions

### Decision 1: BatchTester as Primary Interface

**Rationale:**
- Most users need batch testing, not single API calls
- Synchronous API simpler than async for batch workflows
- Background polling natural for long-running tasks

**Alternative considered:** Async-only API
- ❌ Higher learning curve (async/await, event loops)
- ❌ Jupyter requires nest-asyncio (complexity)
- ❌ Most batch tests don't need async concurrency control

**Result:** Two-layer design
- BatchTester for 90% of users
- TradePoseClient for 10% with special needs

### Decision 2: Period Objects (Not Tuples)

**Rationale:**
- Type safety prevents runtime errors
- Validation at creation time
- Convenience constructors reduce boilerplate
- Self-documenting code

**Alternative considered:** `list[tuple[str, str]]`
- ❌ No validation until API call
- ❌ Wrong order not caught by IDE
- ❌ Less readable: `("2024-01-01", "2024-03-31")` vs `Period.Q1(2024)`

**Result:** Breaking change in v0.2.0
- Removed tuple support entirely
- Forced migration to Period objects
- Better UX long-term

### Decision 3: Polars over Pandas

**Rationale:**
- 10x faster for large datasets (millions of trades)
- Better memory efficiency
- Native Arrow format (gateway → worker → client)
- More expressive API for time series

**Alternative considered:** Pandas
- ❌ Slower for typical backtest sizes (100k+ rows)
- ❌ Higher memory usage
- ❌ Requires conversion from Arrow

**Result:** Polars-first API
- All DataFrames are `pl.DataFrame`
- Users can convert to Pandas if needed: `df.to_pandas()`

### Decision 4: Background Polling Thread

**Rationale:**
- Batch tests run for minutes/hours → polling makes sense
- Daemon thread keeps it simple (no event loop management)
- Auto-download on completion

**Alternative considered:** Manual polling
- ❌ User must write polling loop
- ❌ Easy to forget timeout handling
- ❌ More boilerplate code

**Result:** Automatic background polling
- Start immediately on `submit()`
- Daemon thread (exits with main program)
- Separate event loop for async operations

### Decision 5: Model Reuse (tradepose_models)

**Rationale:**
- Gateway, client, worker all use same types
- Single source of truth prevents drift
- Pydantic validation at every boundary

**Alternative considered:** Separate models per package
- ❌ Schema drift over time
- ❌ Duplicate validation logic
- ❌ Breaking changes harder to track

**Result:** Shared package
- All Pydantic models in `tradepose_models`
- Gateway and client depend on same version
- Type safety end-to-end

---

## Performance Considerations

### Connection Pooling

**HTTP/2 multiplexing:**
- Single connection handles multiple requests
- Default limits: 100 max connections, 20 keepalive

**Configuration:**
```python
# High-concurrency workload
client = TradePoseClient(
    timeout=60.0,
    max_retries=5
)
```

### Memory Management

**ResultCache design:**
- Lazy loading: Download only when accessed
- Memory cache: Avoid redundant downloads
- TTL: Results expire after batch completion

**Memory usage:**
- BatchTester: ~100MB baseline
- Per task result: ~10-50MB (depends on trade count)
- Cache clear: Call `batch._cache.clear()` if needed

### Concurrency Limits

**BatchTester background polling:**
- Polls all tasks in parallel
- No limit on concurrent polls (API rate-limited)

**TradePoseClient async:**
- User controls concurrency with `asyncio.gather()`
- Use `asyncio.Semaphore` for limits

**Example:**
```python
sem = asyncio.Semaphore(5)  # Max 5 concurrent

async def download_with_limit(task_id):
    async with sem:
        return await client.tasks.download_result(task_id)
```

### Timeout Strategy

**BatchTester defaults:**
- Task submission: 30s timeout
- Task polling: 300s (5 min) timeout per task
- Result download: 60s timeout

**TradePoseClient defaults:**
- Request timeout: 30s
- Poll timeout: 300s
- Retry backoff: 1s, 2s, 4s (exponential)

**Tuning for large backtests:**
```python
tester = BatchTester(poll_interval=5.0)  # Poll less frequently
batch = tester.submit(strategies, periods)
batch.wait(timeout=3600.0)  # Wait up to 1 hour
```

### Retry Configuration

**Automatic retry:**
- Network errors: 3 retries with exponential backoff
- Rate limits: Use `retry_after` from API response
- Server errors: 3 retries

**Custom retry:**
```python
client = TradePoseClient(
    max_retries=5,  # More retries for flaky networks
    timeout=60.0    # Longer timeout for slow connections
)
```

---

## Module Structure

```
tradepose_client/
├── __init__.py              # Public API exports
├── client.py                # TradePoseClient (low-level)
├── config.py                # TradePoseConfig
├── exceptions.py            # Exception hierarchy
├── batch/                   # Batch testing API
│   ├── __init__.py
│   ├── tester.py            # BatchTester
│   ├── results.py           # BatchResults, PeriodResult
│   ├── models.py            # Period, BacktestRequest
│   ├── background.py        # BackgroundPoller
│   └── cache.py             # ResultCache
├── builder/                 # Strategy builder API
│   ├── __init__.py
│   ├── strategy.py          # StrategyBuilder
│   ├── blueprint.py         # BlueprintBuilder
│   └── indicator.py         # IndicatorSpecWrapper
├── resources/               # API resources (low-level)
│   ├── base.py              # BaseResource
│   ├── strategies.py        # StrategiesResource
│   ├── export.py            # ExportResource
│   ├── tasks.py             # TasksResource
│   ├── api_keys.py          # APIKeysResource
│   ├── billing.py           # BillingResource
│   └── usage.py             # UsageResource
└── utils.py                 # Utility functions
```

**Import hierarchy:**
```python
# Top-level imports (recommended)
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Low-level imports (advanced)
from tradepose_client import TradePoseClient
from tradepose_client.resources import StrategiesResource
```

---

## See Also

- [README.md](../README.md) - Project overview and quick start
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [EXAMPLES.md](EXAMPLES.md) - Real-world usage patterns
- [LOW_LEVEL_API.md](LOW_LEVEL_API.md) - Async API documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Exception handling guide
