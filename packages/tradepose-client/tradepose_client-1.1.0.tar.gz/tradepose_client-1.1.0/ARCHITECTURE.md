# TradePose Client - Architecture Document

**Python Client Library for TradePose Quantitative Trading Platform**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Polars](https://img.shields.io/badge/Polars-1.19+-orange.svg)](https://pola.rs/)
[![httpx](https://img.shields.io/badge/httpx-0.28+-green.svg)](https://www.python-httpx.org/)

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Technology Stack](#technology-stack)
6. [API Coverage](#api-coverage)
7. [Model Reuse Strategy](#model-reuse-strategy)
8. [Configuration](#configuration)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Usage Examples](#usage-examples)

---

## Overview

The TradePose Client is a production-ready Python client library that provides a type-safe, async-first interface to the TradePose Gateway API. It handles authentication, task polling, result downloading, and automatic data deserialization with Polars DataFrames.

### Key Features

- ✅ **Async-First Design** - Built on httpx with full async/await support
- ✅ **Type-Safe** - Complete Pydantic model integration
- ✅ **Resource-Based API** - Organized by domain (strategies, tasks, billing, etc.)
- ✅ **Automatic Task Polling** - Smart polling with configurable intervals
- ✅ **Polars Integration** - Direct Parquet → DataFrame conversion
- ✅ **Dual Authentication** - API key + JWT support
- ✅ **Error Handling** - Comprehensive exception hierarchy
- ✅ **Retry Logic** - Automatic retries with exponential backoff
- ✅ **Rate Limit Aware** - Respects API rate limits

---

## Design Principles

### 1. **Async-First Architecture**

All API methods are async by default, using `httpx.AsyncClient` for non-blocking I/O. This enables:

- Concurrent API calls
- Efficient task polling
- High-throughput batch operations

### 2. **Resource-Based Organization**

API endpoints are grouped into logical resources:

- `client.api_keys` - API key management
- `client.billing` - Subscription and usage management
- `client.strategies` - Strategy registration and listing
- `client.tasks` - Task status and result retrieval
- `client.export` - Export and backtest operations

### 3. **Smart Task Polling**

Long-running operations return task IDs. The client provides:

- **Automatic polling** with configurable intervals
- **Exponential backoff** to reduce API load
- **Timeout handling** with clear error messages
- **Result streaming** for large datasets

### 4. **Type Safety**

All requests/responses use Pydantic models from `tradepose_models`:

- Compile-time type checking
- Runtime validation
- IDE autocomplete support
- Self-documenting API

### 5. **Shared Model Reuse**

Maximum reuse of models from `tradepose_models` package:

- Enums (TaskStatus, ExportType, IndicatorType, etc.)
- Schemas (trades_schema, performance_schema, enhanced_ohlcv_schema)
- Strategy models (StrategyConfig, Blueprint, Trigger)
- Export models (ExportTaskResponse, OnDemandOhlcvRequest)
- Indicator models (all typed indicator specifications)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  TradePoseClient                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Authentication Layer (API Key / JWT)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Resources (api_keys, billing, strategies, tasks)    │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Task Polling Engine                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Result Deserializer (Parquet → Polars)              │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            httpx.AsyncClient (HTTP Layer)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              TradePose Gateway API                           │
│  (FastAPI + Redis Streams + PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### **TradePoseClient**

- Main entry point and context manager
- Configuration management
- Resource initialization
- HTTP client lifecycle

#### **Authentication Layer**

- API key header injection
- JWT token management
- Session handling
- Credential validation

#### **Resources**

- Domain-specific API methods
- Request validation
- Response deserialization
- Error handling

#### **Task Polling Engine**

- Configurable polling intervals
- Exponential backoff
- Timeout management
- Status change detection

#### **Result Deserializer**

- Parquet binary → Polars DataFrame
- Schema validation
- Type coercion
- Error recovery

---

## Project Structure

```
packages/client/
├── src/
│   └── tradepose_client/
│       ├── __init__.py                 # Package exports
│       ├── client.py                   # Main TradePoseClient class
│       ├── config.py                   # Configuration management
│       ├── exceptions.py               # Custom exceptions
│       ├── types.py                    # Type aliases
│       │
│       ├── resources/                  # API resource modules
│       │   ├── __init__.py
│       │   ├── base.py                 # BaseResource
│       │   ├── api_keys.py             # APIKeysResource
│       │   ├── billing.py              # BillingResource
│       │   ├── strategies.py           # StrategiesResource
│       │   ├── tasks.py                # TasksResource
│       │   └── export.py               # ExportResource
│       │
│       ├── polling/                    # Task polling utilities
│       │   ├── __init__.py
│       │   ├── poller.py               # TaskPoller class
│       │   └── strategies.py           # Polling strategies
│       │
│       ├── serialization/              # Data serialization
│       │   ├── __init__.py
│       │   ├── parquet.py              # Parquet → Polars
│       │   └── validators.py           # Schema validators
│       │
│       └── auth/                       # Authentication
│           ├── __init__.py
│           ├── api_key.py              # API key auth
│           └── jwt.py                  # JWT auth (optional)
│
├── tests/                              # Test suite
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_client.py                  # Client tests
│   ├── test_resources/                 # Resource tests
│   ├── test_polling.py                 # Polling tests
│   └── test_integration.py             # Integration tests
│
├── examples/                           # Usage examples
│   ├── basic_usage.py
│   ├── strategy_registration.py
│   ├── backtest_export.py
│   └── billing_management.py
│
├── pyproject.toml                      # Project metadata
├── README.md                           # User documentation
├── ARCHITECTURE.md                     # This file
└── .env.example                        # Environment template
```

---

## Technology Stack

### Core Dependencies

| Package               | Version   | Purpose                               |
| --------------------- | --------- | ------------------------------------- |
| **httpx**             | 0.28+     | Async HTTP client with HTTP/2 support |
| **polars**            | 1.19+     | High-performance DataFrame library    |
| **pydantic**          | 2.12+     | Data validation and settings          |
| **pydantic-settings** | 2.7+      | Environment-based configuration       |
| **tradepose-models**  | workspace | Shared models and schemas             |

### Optional Dependencies

| Package      | Version | Purpose                              |
| ------------ | ------- | ------------------------------------ |
| **orjson**   | 3.10+   | Fast JSON serialization              |
| **tenacity** | 9.0+    | Retry logic with exponential backoff |
| **rich**     | 13.0+   | Pretty-printing for debugging        |

### Development Dependencies

| Package            | Version | Purpose                |
| ------------------ | ------- | ---------------------- |
| **pytest**         | 8.0+    | Testing framework      |
| **pytest-asyncio** | 0.24+   | Async test support     |
| **pytest-mock**    | 3.14+   | Mocking utilities      |
| **respx**          | 0.21+   | HTTPX mocking          |
| **mypy**           | 1.13+   | Type checking          |
| **ruff**           | 0.8+    | Linting and formatting |

---

## API Coverage

### 1. API Key Management (`client.api_keys`)

#### **Create API Key**

```python
async def create(self, name: str) -> APIKeyCreateResponse
```

- **Endpoint**: `POST /api/v1/keys`
- **Request**: `APIKeyCreate(name=name)`
- **Response**: `APIKeyCreateResponse` (includes plaintext key once)
- **Auth**: JWT required

#### **List API Keys**

```python
async def list(self) -> APIKeyListResponse
```

- **Endpoint**: `GET /api/v1/keys`
- **Response**: `APIKeyListResponse` (list of keys without plaintext)
- **Auth**: JWT required

#### **Revoke API Key**

```python
async def revoke(self, key_id: str) -> None
```

- **Endpoint**: `DELETE /api/v1/keys/{key_id}`
- **Response**: 204 No Content
- **Auth**: JWT required

---

### 2. Billing Management (`client.billing`)

#### **List Plans**

```python
async def list_plans(self) -> PlansListResponse
```

- **Endpoint**: `GET /api/v1/billing/plans`
- **Response**: `PlansListResponse` (all available plans)
- **Auth**: Required

#### **Create Checkout Session**

```python
async def create_checkout(
    self,
    plan_tier: str,
    billing_cycle: str
) -> CheckoutResponse
```

- **Endpoint**: `POST /api/v1/billing/checkout`
- **Request**: `CheckoutRequest(plan_tier, billing_cycle)`
- **Response**: `CheckoutResponse(checkout_url, variant_id)`
- **Auth**: Required

#### **Get Subscription**

```python
async def get_subscription(self) -> SubscriptionDetailResponse
```

- **Endpoint**: `GET /api/v1/billing/subscription`
- **Response**: `SubscriptionDetailResponse` (subscription + usage)
- **Auth**: Required

#### **Cancel Subscription**

```python
async def cancel_subscription(self) -> dict
```

- **Endpoint**: `POST /api/v1/billing/cancel`
- **Response**: Cancellation confirmation
- **Auth**: Required

#### **Get Usage Statistics**

```python
async def get_usage(self) -> UsageStatsResponse
```

- **Endpoint**: `GET /api/v1/billing/usage`
- **Response**: `UsageStatsResponse` (current month usage)
- **Auth**: Required

#### **Get Usage History**

```python
async def get_usage_history(
    self,
    start_date: str | None = None,
    end_date: str | None = None
) -> UsageHistoryResponse
```

- **Endpoint**: `GET /api/v1/billing/usage/history`
- **Query**: `start_date`, `end_date` (ISO 8601)
- **Response**: `UsageHistoryResponse` (historical usage)
- **Auth**: Required

---

### 3. Strategy Management (`client.strategies`)

#### **Register Strategy**

```python
async def register(
    self,
    strategy_code: str,
    overwrite: bool = False,
    poll: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 300.0
) -> RegisterStrategyResponse | ExportTaskResponse
```

- **Endpoint**: `POST /api/v1/strategies`
- **Request**: `RegisterStrategyRequest(strategy_code, overwrite)`
- **Response**: `RegisterStrategyResponse` (task_id)
- **Polling**: Optional automatic polling until completion
- **Auth**: Required

#### **List Strategies**

```python
async def list(
    self,
    full: bool = False,
    instrument_id: str | None = None,
    poll: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 60.0
) -> ListStrategiesResponse | ExportTaskResponse
```

- **Endpoint**: `GET /api/v1/strategies`
- **Query**: `full` (bool), `instrument_id` (optional)
- **Response**: `ListStrategiesResponse` (task_id)
- **Polling**: Optional automatic polling until completion
- **Auth**: Required

#### **Get Strategy**

```python
async def get(
    self,
    strategy_name: str,
    poll: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 60.0
) -> StrategyConfig | ExportTaskResponse
```

- **Endpoint**: `GET /api/v1/strategies/{strategy_name}`
- **Response**: task_id → `StrategyConfig`
- **Polling**: Optional automatic polling until completion
- **Auth**: Required

#### **Delete Strategy**

```python
async def delete(
    self,
    strategy_name: str,
    poll: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 60.0
) -> dict | ExportTaskResponse
```

- **Endpoint**: `DELETE /api/v1/strategies/{strategy_name}`
- **Response**: task_id → deletion confirmation
- **Polling**: Optional automatic polling until completion
- **Auth**: Required

---

### 4. Task Management (`client.tasks`)

#### **Get Task Status**

```python
async def get_status(self, task_id: str) -> ExportTaskResponse
```

- **Endpoint**: `GET /api/v1/tasks/{task_id}`
- **Response**: `ExportTaskResponse` (status, progress, results)
- **Auth**: Required

#### **Download Task Result (First Available)**

```python
async def download_result(
    self,
    task_id: str,
    as_dataframe: bool = True
) -> pl.DataFrame | bytes
```

- **Endpoint**: `GET /api/v1/tasks/{task_id}/result`
- **Response**: Binary Parquet → Polars DataFrame
- **Auth**: Required

#### **Download Specific Result Type**

```python
async def download_result_by_type(
    self,
    task_id: str,
    result_type: str,  # 'trades', 'performance', etc.
    as_dataframe: bool = True
) -> pl.DataFrame | bytes | dict
```

- **Endpoint**: `GET /api/v1/tasks/{task_id}/results/{result_type}`
- **Result Types**:
  - `trades` - Trade execution details (Parquet)
  - `performance` - Performance metrics (Parquet)
  - `enhanced_ohlcv` - Enhanced OHLCV with signals (Parquet)
  - `on_demand_ohlcv` - On-demand OHLCV (Parquet)
  - `latest_trades` - Latest trades (JSON)
- **Auth**: Required

#### **Poll Until Completion**

```python
async def poll_until_complete(
    self,
    task_id: str,
    poll_interval: float = 2.0,
    timeout: float = 300.0,
    on_progress: Callable[[ExportTaskResponse], None] | None = None
) -> ExportTaskResponse
```

- **Description**: Poll task status until completion or timeout
- **Progress Callback**: Optional callback for status updates
- **Auth**: Required

---

### 5. Export Operations (`client.export`)

#### **Generic Export**

```python
async def create_export(
    self,
    request: ExportRequest,
    poll: bool = True,
    poll_interval: float = 5.0,
    timeout: float = 600.0
) -> ExportResponse | ExportTaskResponse
```

- **Endpoint**: `POST /api/v1/export`
- **Request**: `ExportRequest` (complex conditional model)
- **Response**: `ExportResponse` (task_id)
- **Polling**: Optional automatic polling until completion
- **Auth**: Required

#### **Enhanced OHLCV Export**

```python
async def export_enhanced_ohlcv(
    self,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    strategy_names: list[str],
    poll: bool = True,
    poll_interval: float = 5.0,
    timeout: float = 600.0
) -> ExportResponse | ExportTaskResponse
```

- **Export Type**: `enhanced-ohlcv`
- **Required Fields**: symbol, timeframe, start_date, end_date, strategy_names
- **Polling**: Optional automatic polling until completion

#### **Backtest Results Export**

```python
async def export_backtest_results(
    self,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    strategy_names: list[str],
    poll: bool = True,
    poll_interval: float = 5.0,
    timeout: float = 600.0
) -> ExportResponse | ExportTaskResponse
```

- **Export Type**: `backtest-results`
- **Required Fields**: symbol, timeframe, start_date, end_date, strategy_names
- **Results**: trades + performance DataFrames

#### **Latest Trades Export**

```python
async def export_latest_trades(
    self,
    symbol: str,
    timeframe: str,
    strategy_names: list[str],
    poll: bool = True,
    poll_interval: float = 5.0,
    timeout: float = 600.0
) -> ExportResponse | ExportTaskResponse
```

- **Export Type**: `latest-trades`
- **Required Fields**: symbol, timeframe, strategy_names
- **Results**: Latest trade states (JSON)

#### **On-Demand OHLCV Export**

```python
async def export_on_demand_ohlcv(
    self,
    base_instrument: str,
    base_freq: str,
    start_date: str,
    end_date: str,
    indicator_specs: list[IndicatorSpec],
    poll: bool = True,
    poll_interval: float = 5.0,
    timeout: float = 600.0
) -> ExportResponse | ExportTaskResponse
```

- **Export Type**: `on-demand-ohlcv`
- **Required Fields**: base_instrument, base_freq, start_date, end_date, indicator_specs
- **Results**: OHLCV with custom indicators

---

### 6. Batch Testing (`BatchTester`)

The Batch Testing API simplifies multi-strategy, multi-period backtesting by automatically handling task submission, polling, and result downloading.

**Note**: This is a standalone API, not a resource on `TradePoseClient`. It operates independently with its own client instance.

#### **Submit Batch Backtest**

```python
def submit(
    self,
    strategies: list[StrategyConfig],
    periods: list[tuple[str, str]] | list[Period],
    cache: bool = True
) -> BatchResults
```

- **Behavior**: Creates one task per period (each task tests all strategies)
- **Returns Immediately**: Non-blocking, background polling starts automatically
- **Background Operations**: Auto-polls status and downloads completed results
- **Caching**: Optional in-memory result cache

**Usage**:
```python
from tradepose_client import BatchTester

tester = BatchTester(api_key="sk_xxx")
batch = tester.submit(
    strategies=[strategy1, strategy2],
    periods=[
        ("2021-01-01", "2021-12-31"),
        ("2022-01-01", "2022-12-31"),
    ]
)

# Returns immediately, background polling active
print(batch.status)  # {"pending": 1, "processing": 1, "completed": 0}
print(batch.progress)  # 0.5

# Wait for completion
batch.wait()

# Access results
for period_key, result in batch.results.items():
    print(result.summary())
```

**Key Features**:
- **Parallel Submission**: Uses `asyncio.gather()` for concurrent task creation
- **Background Poller**: Separate daemon thread with independent event loop
- **Reactive Results**: `BatchResults` and `PeriodResult` auto-update in background
- **Memory Cache**: Optional caching to avoid redundant downloads
- **Thread-Safe**: All operations protected with RLock

**Architecture**:
```
BatchTester.submit()
    ↓
[Thread] Submit all tasks in parallel (asyncio.gather)
    ↓
Create BatchResults (with PeriodResult objects)
    ↓
Start BackgroundPoller (daemon thread)
    ↓
Return immediately (non-blocking)
    ↓
[Background] Poll statuses every 2s
    ↓
[Background] Auto-download completed results
    ↓
User accesses batch.results (auto-updated)
```

**BatchResults Properties**:
- `status: dict[str, int]` - Real-time status counts
- `progress: float` - Overall progress (0.0 - 1.0)
- `is_complete: bool` - Whether all tasks done
- `results: dict[str, PeriodResult]` - Results by period
- `completed_tasks: list[str]` - List of completed task IDs
- `failed_tasks: list[dict]` - Failed tasks with errors

**BatchResults Methods**:
- `get_period(period) -> PeriodResult` - Get specific period result
- `wait(timeout=None)` - Block until all tasks complete
- `summary() -> pl.DataFrame` - Summary stats for all periods
- `all_trades() -> pl.DataFrame` - Combined trades from all periods
- `save(path)` - Save all results to directory

**PeriodResult Properties**:
- `task_id: str` - Server task identifier
- `period: tuple[datetime, datetime]` - Time period
- `status: TaskStatus` - Current status
- `trades: pl.DataFrame | None` - Auto-downloads on access
- `performance: pl.DataFrame | None` - Auto-downloads on access

**PeriodResult Methods**:
- `get_strategy_trades(name) -> pl.DataFrame` - Filter by strategy
- `get_strategy_performance(name) -> dict` - Get specific metrics
- `summary() -> dict` - Quick summary (auto-waits)
- `wait(timeout=None)` - Block until this task completes

**Configuration**:
- `api_key`: Authentication
- `server_url`: Gateway URL (default: https://api.tradepose.com)
- `poll_interval`: Status polling interval in seconds (default: 2.0)
- `auto_download`: Auto-download completed results (default: True)

**See Also**:
- [Batch Testing API Specification](/docs/BATCH_TESTING_API_SPECIFICATION.md)
- [Quickstart Notebook](/tradepose_client_quickstart.ipynb) - Batch testing examples

---

## Model Reuse Strategy

### Models to Reuse from `tradepose_models`

#### **1. Enums** (`from tradepose_models.enums import ...`)

| Enum             | Usage                                                |
| ---------------- | ---------------------------------------------------- |
| `Freq`           | Timeframe specification (MIN_1, HOUR_1, DAY_1, etc.) |
| `TaskStatus`     | Task status (PENDING, RUNNING, COMPLETED, FAILED)    |
| `ExportType`     | Export operation types                               |
| `IndicatorType`  | Available indicators (SMA, EMA, RSI, etc.)           |
| `OrderStrategy`  | Entry/exit strategies                                |
| `TradeDirection` | Trade directions (LONG, SHORT, BOTH)                 |
| `TrendType`      | Trend types for blueprint configuration              |
| `Weekday`        | Weekday enum for time-based filters                  |

#### **2. Schemas** (`from tradepose_models.schemas import ...`)

| Schema                  | Usage                                          |
| ----------------------- | ---------------------------------------------- |
| `trades_schema`         | Validate trades DataFrame (64 fields)          |
| `performance_schema`    | Validate performance DataFrame (20 fields)     |
| `enhanced_ohlcv_schema` | Validate enhanced OHLCV DataFrame (60+ fields) |

#### **3. Strategy Models** (`from tradepose_models.strategy import ...`)

| Model             | Usage                                 |
| ----------------- | ------------------------------------- |
| `StrategyConfig`  | Complete strategy configuration       |
| `Blueprint`       | Strategy blueprint (entry/exit rules) |
| `Trigger`         | Entry/exit trigger definitions        |
| `IndicatorSpec`   | Indicator specifications              |
| `IndicatorConfig` | Indicator configuration               |

#### **4. Export Models** (`from tradepose_models.export import ...`)

| Model                  | Usage                          |
| ---------------------- | ------------------------------ |
| `ExportTaskResponse`   | Export task status and results |
| `ResultSummary`        | Task result summary            |
| `OnDemandOhlcvRequest` | On-demand OHLCV request        |

#### **5. Indicator Models** (`from tradepose_models.indicators import ...`)

| Model                                | Usage                                  |
| ------------------------------------ | -------------------------------------- |
| `SMAIndicator`, `EMAIndicator`, etc. | Typed indicator specifications         |
| `Indicator`                          | Indicator factory with builder methods |
| `MarketProfileConfig`                | Market profile configuration helpers   |

---

### Models to Add to Shared Package

The following models currently exist only in the gateway and should be migrated to `tradepose_models`:

#### **1. Task Models** (Gateway: `task_models.py`)

```python
# tradepose_models/tasks/
class TaskMetadata(BaseModel):
    task_id: str
    user_id: str
    status: TaskStatus
    operation_type: str
    created_at: datetime
    updated_at: datetime

class StreamEvent(BaseModel):
    task_id: str
    user_id: str
    operation_type: str
    payload: dict
    created_at: datetime
    retry_count: int

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str
    result: dict | None = None
```

#### **2. Auth Models** (Gateway: `auth_models.py`)

```python
# tradepose_models/auth/
class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    key_id: str
    user_id: str
    name: str
    key_preview: str
    created_at: datetime
    last_used_at: datetime | None

class APIKeyCreateResponse(BaseModel):
    key: APIKeyResponse
    plaintext_key: str  # Only shown once

class APIKeyListResponse(BaseModel):
    keys: list[APIKeyResponse]
    total: int

class AuthUser(BaseModel):
    user_id: str
    email: str
    session_id: str | None

class AuthContext(BaseModel):
    user: AuthUser
    auth_type: str  # 'jwt' | 'api_key'
    api_key_id: str | None
```

#### **3. Billing Models** (Gateway: `billing_models.py`)

```python
# tradepose_models/billing/
class CheckoutRequest(BaseModel):
    plan_tier: str
    billing_cycle: str

class CheckoutResponse(BaseModel):
    checkout_url: str
    variant_id: str

class PlanLimitsResponse(BaseModel):
    max_strategies: int
    max_instruments: int
    max_backtest_years: int

class PlanResponse(BaseModel):
    plan_id: str
    name: str
    tier: str
    limits: PlanLimitsResponse
    price_monthly: float
    price_annual: float

class PlansListResponse(BaseModel):
    plans: list[PlanResponse]

class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    plan: PlanResponse
    status: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool

class SubscriptionDetailResponse(BaseModel):
    subscription: SubscriptionResponse
    usage: dict  # Current usage stats

class UsageDayResponse(BaseModel):
    date: str
    strategies_used: int
    instruments_used: int
    backtest_requests: int

class CurrentUsageResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    strategies_count: int
    instruments_count: int
    backtest_count: int
    limits: PlanLimitsResponse

class UsageHistoryResponse(BaseModel):
    days: list[UsageDayResponse]
    total_days: int

class UsageStatsResponse(BaseModel):
    current: CurrentUsageResponse
    is_over_limit: bool
    limits_exceeded: list[str]
```

#### **4. Strategy-Specific Response Models**

```python
# tradepose_models/strategy/responses.py
class RegisterStrategyResponse(BaseModel):
    task_id: str
    message: str
    operation_type: str

class ListStrategiesResponse(BaseModel):
    task_id: str
    message: str
    operation_type: str

class StrategyDetailResponse(BaseModel):
    strategy: StrategyConfig
    metadata: dict  # Created at, updated at, etc.
```

#### **5. Export Response Models**

```python
# tradepose_models/export/responses.py
class ExportResponse(BaseModel):
    task_id: str
    message: str
    operation_type: str
    export_type: ExportType
```

#### **6. Error Models**

```python
# tradepose_models/errors.py
class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None

class ErrorResponse(BaseModel):
    error: str
    details: list[ErrorDetail] | None = None
    request_id: str | None = None
```

---

## Configuration

### Environment Variables

```bash
# Required
TRADEPOSE_API_KEY=tp_live_xxxxxxxxxxxxxxxxxxxxx
TRADEPOSE_SERVER_URL=https://api.tradepose.com

# Optional
TRADEPOSE_TIMEOUT=30.0              # Request timeout (seconds)
TRADEPOSE_MAX_RETRIES=3             # Max retry attempts
TRADEPOSE_POLL_INTERVAL=2.0         # Default poll interval (seconds)
TRADEPOSE_POLL_TIMEOUT=300.0        # Default poll timeout (seconds)
TRADEPOSE_DEBUG=false               # Enable debug logging
TRADEPOSE_LOG_LEVEL=INFO            # Log level
```

### Configuration Class

```python
# tradepose_client/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class TradePoseConfig(BaseSettings):
    """TradePose client configuration"""

    model_config = SettingsConfigDict(
        env_prefix="TRADEPOSE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Required
    api_key: str
    server_url: str = "https://api.tradepose.com"

    # Optional
    timeout: float = 30.0
    max_retries: int = 3
    poll_interval: float = 2.0
    poll_timeout: float = 300.0
    debug: bool = False
    log_level: str = "INFO"

    # JWT (optional, for initial API key creation)
    jwt_token: str | None = None
```

---

## Implementation Roadmap

### Phase 1: Core Client + Authentication (Week 1)

#### Deliverables

- [ ] `TradePoseClient` main class with context manager
- [ ] `TradePoseConfig` configuration management
- [ ] `BaseResource` abstract base class
- [ ] API key authentication
- [ ] JWT authentication (optional)
- [ ] Custom exception hierarchy
- [ ] Basic logging setup

#### Files

```
src/tradepose_client/
├── __init__.py
├── client.py
├── config.py
├── exceptions.py
├── types.py
└── auth/
    ├── __init__.py
    ├── api_key.py
    └── jwt.py
```

---

### Phase 2: Resource Implementations (Week 2-3)

#### 2.1: API Keys Resource

- [ ] Create API key
- [ ] List API keys
- [ ] Revoke API key

#### 2.2: Billing Resource

- [ ] List plans
- [ ] Create checkout session
- [ ] Get subscription
- [ ] Cancel subscription
- [ ] Get usage statistics
- [ ] Get usage history

#### 2.3: Tasks Resource

- [ ] Get task status
- [ ] Download result (first available)
- [ ] Download result by type
- [ ] Basic polling implementation

#### Files

```
src/tradepose_client/resources/
├── __init__.py
├── base.py
├── api_keys.py
├── billing.py
└── tasks.py
```

---

### Phase 3: Strategy + Export Resources (Week 4)

#### 3.1: Strategies Resource

- [ ] Register strategy
- [ ] List strategies
- [ ] Get strategy detail
- [ ] Delete strategy
- [ ] Integrated polling for async operations

#### 3.2: Export Resource

- [ ] Generic export
- [ ] Enhanced OHLCV export
- [ ] Backtest results export
- [ ] Latest trades export
- [ ] On-demand OHLCV export
- [ ] Integrated polling for async operations

#### Files

```
src/tradepose_client/resources/
├── strategies.py
└── export.py
```

---

### Phase 4: Task Polling Engine (Week 5)

#### Deliverables

- [ ] `TaskPoller` class with configurable strategies
- [ ] Exponential backoff polling
- [ ] Linear interval polling
- [ ] Custom polling strategies
- [ ] Progress callbacks
- [ ] Timeout handling
- [ ] Cancel token support

#### Files

```
src/tradepose_client/polling/
├── __init__.py
├── poller.py
└── strategies.py
```

---

### Phase 5: Result Serialization (Week 6)

#### Deliverables

- [ ] Parquet → Polars DataFrame conversion
- [ ] Schema validation against `tradepose_models.schemas`
- [ ] Type coercion and error recovery
- [ ] Streaming support for large results
- [ ] Result caching (optional)

#### Files

```
src/tradepose_client/serialization/
├── __init__.py
├── parquet.py
└── validators.py
```

---

### Phase 6: Advanced Features (Week 7-8)

#### Deliverables

- [ ] Retry logic with exponential backoff (tenacity)
- [ ] Rate limit detection and handling
- [ ] Response caching (optional)
- [ ] Request batching (optional)
- [ ] Progress bars for long operations (rich)
- [ ] Comprehensive error messages
- [ ] Debug mode with request/response logging

---

### Phase 7: Testing + Documentation (Week 9-10)

#### Deliverables

- [ ] Unit tests for all resources (95% coverage)
- [ ] Integration tests with mocked API (respx)
- [ ] Polling tests with simulated delays
- [ ] Serialization tests with sample Parquet files
- [ ] User documentation (README.md)
- [ ] API reference documentation
- [ ] Usage examples for all features
- [ ] Migration guide from direct API usage

---

## Usage Examples

### Basic Usage

```python
import asyncio
from tradepose_client import TradePoseClient

async def main():
    async with TradePoseClient() as client:
        # List available plans
        plans = await client.billing.list_plans()
        print(f"Available plans: {len(plans.plans)}")

        # Get current subscription
        subscription = await client.billing.get_subscription()
        print(f"Plan: {subscription.subscription.plan.name}")
        print(f"Usage: {subscription.usage}")

asyncio.run(main())
```

### Strategy Registration

```python
from tradepose_client import TradePoseClient
from tradepose_models.strategy import StrategyConfig

async def register_strategy():
    async with TradePoseClient() as client:
        # Load strategy from file
        strategy = StrategyConfig.load("my_strategy.json")

        # Register strategy (auto-polls until complete)
        result = await client.strategies.register(
            strategy_code=strategy.to_json(),
            overwrite=True,
            poll=True,  # Auto-poll
            timeout=300.0
        )

        print(f"Strategy registered: {result.export_task_id}")
        print(f"Status: {result.status}")
```

### Backtest Export with Polling

```python
from tradepose_client import TradePoseClient
import polars as pl

async def run_backtest():
    async with TradePoseClient() as client:
        # Create backtest export (auto-polls)
        result = await client.export.export_backtest_results(
            symbol="BTCUSDT",
            timeframe="1h",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy_names=["my_strategy"],
            poll=True,
            timeout=600.0
        )

        # Download trades
        trades_df = await client.tasks.download_result_by_type(
            task_id=result.export_task_id,
            result_type="trades"
        )

        # Download performance
        perf_df = await client.tasks.download_result_by_type(
            task_id=result.export_task_id,
            result_type="performance"
        )

        print(f"Trades: {len(trades_df)} rows")
        print(f"Performance: {perf_df}")

        # Analyze results
        total_pnl = trades_df["pnl"].sum()
        win_rate = (trades_df["pnl"] > 0).mean() * 100

        print(f"Total PnL: ${total_pnl:.2f}")
        print(f"Win Rate: {win_rate:.1f}%")
```

### Manual Task Polling with Progress

```python
from tradepose_client import TradePoseClient

async def poll_with_progress():
    async with TradePoseClient() as client:
        # Start export (no auto-poll)
        response = await client.export.export_backtest_results(
            symbol="ETHUSDT",
            timeframe="15m",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy_names=["strategy_1", "strategy_2"],
            poll=False  # Manual polling
        )

        task_id = response.task_id

        # Poll with progress callback
        def on_progress(status):
            print(f"Status: {status.status} | Strategies: {status.executed_strategies}/{len(strategy_names)}")

        result = await client.tasks.poll_until_complete(
            task_id=task_id,
            poll_interval=5.0,
            timeout=600.0,
            on_progress=on_progress
        )

        print(f"Completed: {result.completed_at}")
        print(f"Result summary: {result.result_summary}")
```

### On-Demand OHLCV with Custom Indicators

```python
from tradepose_client import TradePoseClient
from tradepose_models.indicators import Indicator

async def custom_ohlcv():
    async with TradePoseClient() as client:
        # Define custom indicators
        indicators = [
            Indicator.sma(period=20),
            Indicator.ema(period=50),
            Indicator.rsi(period=14),
            Indicator.atr(period=14, quantile=0.618),
            Indicator.supertrend(atr_period=10, atr_multiplier=3.0),
        ]

        # Export with custom indicators
        result = await client.export.export_on_demand_ohlcv(
            base_instrument="BTCUSDT",
            base_freq="1h",
            start_date="2024-01-01",
            end_date="2024-12-31",
            indicator_specs=indicators,
            poll=True,
            timeout=600.0
        )

        # Download result
        ohlcv_df = await client.tasks.download_result_by_type(
            task_id=result.export_task_id,
            result_type="on_demand_ohlcv"
        )

        print(f"OHLCV shape: {ohlcv_df.shape}")
        print(f"Columns: {ohlcv_df.columns}")
```

### API Key Management

```python
from tradepose_client import TradePoseClient

async def manage_api_keys():
    # Initial setup with JWT token
    async with TradePoseClient(jwt_token="your_jwt_token") as client:
        # Create API key
        new_key = await client.api_keys.create(name="Production Key")
        print(f"New API key: {new_key.plaintext_key}")  # Save this!
        print(f"Key ID: {new_key.key.key_id}")

        # List all keys
        keys = await client.api_keys.list()
        for key in keys.keys:
            print(f"{key.name}: {key.key_preview} (created: {key.created_at})")

        # Revoke old key
        await client.api_keys.revoke(key_id="old_key_id")
        print("Key revoked")
```

### Error Handling

```python
from tradepose_client import TradePoseClient
from tradepose_client.exceptions import (
    TradePoseAPIError,
    TaskTimeoutError,
    TaskFailedError,
    AuthenticationError,
    RateLimitError
)

async def handle_errors():
    try:
        async with TradePoseClient() as client:
            result = await client.export.export_backtest_results(
                symbol="INVALID",
                timeframe="1h",
                start_date="2024-01-01",
                end_date="2024-12-31",
                strategy_names=["nonexistent_strategy"],
                poll=True,
                timeout=60.0
            )
    except AuthenticationError as e:
        print(f"Auth failed: {e}")
    except TaskTimeoutError as e:
        print(f"Task timed out after {e.timeout}s: {e.task_id}")
    except TaskFailedError as e:
        print(f"Task failed: {e.error}")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
    except TradePoseAPIError as e:
        print(f"API error: {e.message} (status: {e.status_code})")
```

---

## Summary

This architecture document defines a production-ready Python client for the TradePose Gateway API with:

✅ **Complete API coverage** - All 30+ endpoints mapped to intuitive Python methods
✅ **Type-safe design** - Full Pydantic model integration with IDE support
✅ **Async-first** - Built on httpx with efficient concurrent operations
✅ **Smart polling** - Automatic task polling with progress callbacks
✅ **Polars integration** - Direct Parquet → DataFrame conversion
✅ **Dual authentication** - API key + JWT support
✅ **Comprehensive error handling** - Detailed exception hierarchy
✅ **Resource-based organization** - Clean, intuitive API structure
✅ **Model reuse** - Maximum leverage of `tradepose_models` package
✅ **10-week roadmap** - Clear implementation phases with deliverables

**Next Steps**: Begin Phase 1 implementation (Core Client + Authentication)
