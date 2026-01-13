# Low-Level API Reference

**Target Audience:** Advanced users who need fine-grained control over HTTP connections, custom retry logic, or manual event loop management.

**Most users should use [BatchTester](../README.md#quick-start) instead** - it provides a simpler, synchronous interface for common use cases.

---

## When to Use the Low-Level API

Use the async `TradePoseClient` directly when you need:

1. **Fine-grained HTTP control** - Custom timeouts, connection pooling, HTTP/2 settings
2. **Custom retry logic** - Implement your own retry strategies beyond exponential backoff
3. **Manual event loop management** - Integrate with existing async frameworks (aiohttp, FastAPI, etc.)
4. **Single-operation workflows** - One-off API calls where BatchTester overhead isn't justified
5. **Advanced concurrency patterns** - Complex async workflows with custom coordination

**For batch testing workflows, use [BatchTester](../README.md#batch-testing)** which handles async complexity automatically.

---

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [TradePoseClient](#tradeposeclient)
3. [Resource APIs](#resource-apis)
4. [Task Polling Pattern](#task-polling-pattern)
5. [Concurrent Operations](#concurrent-operations)
6. [Error Handling](#error-handling)
7. [Advanced Configuration](#advanced-configuration)

---

## Basic Usage

### Async Context Manager (Recommended)

```python
from tradepose_client import TradePoseClient

async def main():
    async with TradePoseClient(api_key="tp_live_xxx") as client:
        strategies = await client.strategies.list()
        print(f"Found {len(strategies.strategies)} strategies")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Benefits:**
- Automatic connection cleanup
- Proper resource management
- Exception safety

### Manual Lifecycle Management

```python
from tradepose_client import TradePoseClient

async def main():
    client = TradePoseClient(api_key="tp_live_xxx")

    try:
        strategies = await client.strategies.list()
        print(f"Found {len(strategies.strategies)} strategies")
    finally:
        await client.close()  # Manual cleanup

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## TradePoseClient

### Initialization

```python
from tradepose_client import TradePoseClient, TradePoseConfig

# Method 1: Direct parameters
client = TradePoseClient(
    api_key="tp_live_xxx",
    server_url="https://api.tradepose.com",
    timeout=60.0,
    max_retries=3
)

# Method 2: Config object
config = TradePoseConfig(
    api_key="tp_live_xxx",
    timeout=60.0,
    debug=True
)
client = TradePoseClient(config=config)

# Method 3: Environment variables (recommended)
# Set TRADEPOSE_API_KEY, TRADEPOSE_TIMEOUT, etc.
client = TradePoseClient()  # Auto-loads from env vars
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | None | API key (required if not in env) |
| `jwt_token` | str | None | JWT token (alternative auth) |
| `server_url` | str | https://api.tradepose.com | Gateway URL |
| `timeout` | float | 30.0 | Request timeout (1.0 - 600.0s) |
| `max_retries` | int | 3 | Max retry attempts (0 - 10) |
| `poll_interval` | float | 2.0 | Task polling interval (0.5 - 60.0s) |
| `poll_timeout` | float | 300.0 | Max polling duration (10.0 - 3600.0s) |
| `debug` | bool | False | Enable debug logging |

See [CONFIGURATION.md](CONFIGURATION.md) for details.

---

## Resource APIs

The client organizes API endpoints into logical resources:

### 1. Strategies Resource

```python
async with TradePoseClient() as client:
    # List all strategies
    response = await client.strategies.list()
    for strategy in response.strategies:
        print(f"{strategy.name}: {len(strategy.indicators)} indicators")

    # Register new strategy
    with open("my_strategy.py") as f:
        strategy_code = f.read()

    task = await client.strategies.register(
        strategy_code=strategy_code,
        poll=True,  # Wait for compilation
        timeout=120.0
    )
    print(f"Registered: {task.task_id}")

    # Get strategy details
    strategy = await client.strategies.get("MyStrategy")
    print(strategy.model_dump_json(indent=2))

    # Delete strategy
    await client.strategies.delete("OldStrategy")
```

### 2. Export Resource

```python
from tradepose_models.strategy import StrategyConfig
from tradepose_models.enums import Freq

async with TradePoseClient() as client:
    # Export backtest results
    response = await client.export.export_backtest_results(
        start_date="2024-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy_config],
        poll=True  # Auto-poll until completion
    )

    trades = response.trades  # Polars DataFrame
    performance = response.performance  # Polars DataFrame

    # Export enhanced OHLCV
    response = await client.export.export_enhanced_ohlcv(
        start_date="2024-01-01",
        end_date="2024-03-31",
        instrument="TXF_M1_SHIOAJI_FUTURE",
        freq=Freq.MIN_15,
        indicators=[{"type": "SMA", "period": 20}],
        poll=True
    )
    ohlcv = response.ohlcv  # Polars DataFrame

    # Export latest trades
    response = await client.export.export_latest_trades(
        strategy_name="MyStrategy",
        limit=100,
        poll=True
    )
    recent_trades = response.trades  # Polars DataFrame
```

### 3. Tasks Resource

```python
async with TradePoseClient() as client:
    # Get task status
    status = await client.tasks.get_status(task_id)
    print(f"Status: {status.status}")
    print(f"Progress: {status.progress:.1%}")

    # Download specific result type
    trades = await client.tasks.download_result_by_type(
        task_id, "trades"
    )

    # Download all results
    results = await client.tasks.download_result(task_id)
    print(f"Available results: {results.keys()}")
```

### 4. API Keys Resource

```python
async with TradePoseClient() as client:
    # Create new API key
    response = await client.api_keys.create(name="Production Key")
    print(f"New key: {response.key}")
    print(f"Key ID: {response.key_id}")

    # List all keys
    response = await client.api_keys.list()
    for key in response.api_keys:
        print(f"{key.name}: {key.preview} (last used: {key.last_used_at})")

    # Revoke key
    await client.api_keys.revoke(key_id)
```

### 5. Billing Resource

```python
async with TradePoseClient() as client:
    # List available plans
    response = await client.billing.list_plans()
    for plan in response.plans:
        print(f"{plan.name}: ${plan.price}/month")

    # Get current subscription
    subscription = await client.billing.get_subscription()
    print(f"Current plan: {subscription.plan_name}")
    print(f"Renewal date: {subscription.renewal_date}")

    # Get usage statistics
    usage = await client.billing.get_usage()
    print(f"API calls: {usage.api_calls}/{usage.api_call_limit}")
    print(f"Storage: {usage.storage_used}/{usage.storage_limit}")
```

### 6. Usage Resource

```python
async with TradePoseClient() as client:
    # Get detailed usage statistics
    response = await client.usage.get_stats(
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    print(f"Total API calls: {response.total_api_calls}")
    print(f"Total strategies tested: {response.total_strategies_tested}")
```

---

## Task Polling Pattern

Long-running operations (strategy registration, data exports) return `task_id` immediately. Poll for completion manually:

### Manual Polling

```python
import asyncio

async with TradePoseClient() as client:
    # Submit task without polling
    task = await client.export.export_backtest_results(
        start_date="2024-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy],
        poll=False  # Return immediately
    )

    task_id = task.task_id
    print(f"Task submitted: {task_id}")

    # Manual polling loop
    while True:
        status = await client.tasks.get_status(task_id)
        print(f"Status: {status.status} ({status.progress:.1%})")

        if status.status == "completed":
            break
        elif status.status == "failed":
            print(f"Error: {status.error_message}")
            break

        await asyncio.sleep(2.0)

    # Download result
    if status.status == "completed":
        trades = await client.tasks.download_result_by_type(
            task_id, "trades"
        )
        print(f"Downloaded {len(trades)} trades")
```

### Auto-Polling (Default)

```python
async with TradePoseClient() as client:
    # Auto-polls until completion
    response = await client.export.export_backtest_results(
        start_date="2024-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy],
        poll=True,  # Default
        poll_interval=2.0,
        timeout=600.0
    )

    # Result ready immediately
    trades = response.trades
    print(f"Total trades: {len(trades)}")
```

---

## Concurrent Operations

### Parallel API Calls

```python
import asyncio

async with TradePoseClient() as client:
    # Execute multiple calls concurrently
    strategies, plans, usage = await asyncio.gather(
        client.strategies.list(),
        client.billing.list_plans(),
        client.billing.get_usage()
    )

    print(f"Strategies: {len(strategies.strategies)}")
    print(f"Plans: {len(plans.plans)}")
    print(f"API calls: {usage.api_calls}")
```

### Parallel Task Submission

```python
async with TradePoseClient() as client:
    # Submit multiple tasks in parallel
    tasks = await asyncio.gather(
        client.export.export_backtest_results(
            start_date="2024-01-01",
            end_date="2024-03-31",
            strategy_configs=[strategy1],
            poll=False
        ),
        client.export.export_backtest_results(
            start_date="2024-04-01",
            end_date="2024-06-30",
            strategy_configs=[strategy2],
            poll=False
        ),
        client.export.export_backtest_results(
            start_date="2024-07-01",
            end_date="2024-09-30",
            strategy_configs=[strategy3],
            poll=False
        )
    )

    task_ids = [task.task_id for task in tasks]
    print(f"Submitted {len(task_ids)} tasks")

    # Poll all tasks concurrently
    while True:
        statuses = await asyncio.gather(
            *[client.tasks.get_status(tid) for tid in task_ids]
        )

        completed = sum(1 for s in statuses if s.status == "completed")
        print(f"Progress: {completed}/{len(task_ids)} completed")

        if completed == len(task_ids):
            break

        await asyncio.sleep(5.0)
```

**Note:** For multi-strategy, multi-period testing, use [BatchTester](../README.md#batch-testing) which handles this automatically.

---

## Error Handling

All exceptions inherit from `TradePoseError`:

```python
from tradepose_client import (
    TradePoseClient,
    AuthenticationError,
    RateLimitError,
    TaskTimeoutError,
    NetworkError
)
import asyncio

async def call_with_retry(client: TradePoseClient, max_retries: int = 3):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await client.strategies.list()

        except RateLimitError as e:
            wait_time = e.retry_after if e.retry_after else (2 ** attempt)
            print(f"Rate limited. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)

        except NetworkError as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt
            print(f"Network error. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

async def main():
    async with TradePoseClient() as client:
        try:
            response = await call_with_retry(client)
            print(f"Found {len(response.strategies)} strategies")

        except AuthenticationError:
            print("Invalid API key")

        except TaskTimeoutError as e:
            print(f"Task {e.task_id} timed out")
            # Check status manually
            status = await client.tasks.get_status(e.task_id)
            print(f"Current status: {status.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

See [ERROR_HANDLING.md](ERROR_HANDLING.md) for complete exception reference.

---

## Advanced Configuration

### Custom HTTP Client

```python
import httpx
from tradepose_client import TradePoseClient

# Custom limits
limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0
)

# Custom transport
transport = httpx.AsyncHTTPTransport(
    limits=limits,
    retries=3
)

# Create client with custom httpx client
http_client = httpx.AsyncClient(
    transport=transport,
    http2=True,
    timeout=60.0
)

client = TradePoseClient(
    api_key="tp_live_xxx",
    http_client=http_client  # Use custom client
)
```

### Event Loop Integration

#### With FastAPI

```python
from fastapi import FastAPI, Depends
from tradepose_client import TradePoseClient

app = FastAPI()

async def get_client():
    """Dependency injection for TradePoseClient."""
    async with TradePoseClient() as client:
        yield client

@app.get("/strategies")
async def list_strategies(client: TradePoseClient = Depends(get_client)):
    response = await client.strategies.list()
    return {"strategies": response.strategies}
```

#### With aiohttp

```python
from aiohttp import web
from tradepose_client import TradePoseClient

async def init_app():
    app = web.Application()
    app["tradepose_client"] = TradePoseClient()
    app.router.add_get("/strategies", list_strategies)
    return app

async def list_strategies(request):
    client = request.app["tradepose_client"]
    response = await client.strategies.list()
    return web.json_response({"strategies": [s.dict() for s in response.strategies]})

if __name__ == "__main__":
    app = asyncio.run(init_app())
    web.run_app(app)
```

---

## Performance Tuning

### Connection Pooling

```python
from tradepose_client import TradePoseClient

# High-concurrency configuration
client = TradePoseClient(
    api_key="tp_live_xxx",
    timeout=60.0,
    max_retries=5
)

# httpx automatically pools connections
# Default: 100 max connections, 20 keepalive connections
```

### Timeout Strategy

```python
# Fast operations (list, get)
client = TradePoseClient(timeout=10.0)

# Long operations (backtest, export)
client = TradePoseClient(
    timeout=120.0,
    poll_timeout=1800.0  # 30 minutes
)
```

### Concurrent Task Management

```python
import asyncio
from tradepose_client import TradePoseClient

async def process_tasks(task_ids: list[str]):
    """Process multiple tasks with controlled concurrency."""
    async with TradePoseClient() as client:
        # Semaphore to limit concurrent downloads
        sem = asyncio.Semaphore(5)  # Max 5 concurrent

        async def download_with_limit(task_id):
            async with sem:
                return await client.tasks.download_result_by_type(
                    task_id, "trades"
                )

        results = await asyncio.gather(
            *[download_with_limit(tid) for tid in task_ids]
        )

        return results
```

---

## Migration from BatchTester

If you're using BatchTester and need low-level control:

### BatchTester (High-Level)

```python
from tradepose_client import BatchTester
from tradepose_client.batch import Period

tester = BatchTester(api_key="tp_live_xxx")
batch = tester.submit(
    strategies=[s1, s2],
    periods=[Period.Q1(2024), Period.Q2(2024)]
)
batch.wait()
summary = batch.summary()
```

### TradePoseClient (Low-Level Equivalent)

```python
from tradepose_client import TradePoseClient
import asyncio

async def batch_test_manual():
    async with TradePoseClient(api_key="tp_live_xxx") as client:
        # Submit tasks
        tasks = []
        for period in [("2024-01-01", "2024-03-31"), ("2024-04-01", "2024-06-30")]:
            for strategy in [s1, s2]:
                task = await client.export.export_backtest_results(
                    start_date=period[0],
                    end_date=period[1],
                    strategy_configs=[strategy],
                    poll=False
                )
                tasks.append(task.task_id)

        # Poll all tasks
        while True:
            statuses = await asyncio.gather(
                *[client.tasks.get_status(tid) for tid in tasks]
            )
            if all(s.status in ["completed", "failed"] for s in statuses):
                break
            await asyncio.sleep(2.0)

        # Download results
        results = await asyncio.gather(
            *[client.tasks.download_result_by_type(tid, "trades") for tid in tasks]
        )

        return results

if __name__ == "__main__":
    results = asyncio.run(batch_test_manual())
```

**Takeaway:** Unless you need custom control, **use BatchTester** - it's simpler and handles complexity automatically.

---

## See Also

- [README.md](../README.md) - Primary documentation with BatchTester examples
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Exception types and handling strategies
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [EXAMPLES.md](EXAMPLES.md) - Real-world usage patterns
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions and data flow
