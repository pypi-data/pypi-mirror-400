# Error Handling

Complete guide to exception handling in TradePose Client SDK.

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [Exception Reference](#exception-reference)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Best Practices](#best-practices)

---

## Exception Hierarchy

All SDK exceptions inherit from `TradePoseError`:

```
TradePoseError (root)
├── TradePoseConfigError
├── TradePoseAPIError
│   ├── AuthenticationError (401)
│   ├── AuthorizationError (403)
│   ├── ResourceNotFoundError (404)
│   ├── ValidationError (422)
│   ├── RateLimitError (429)
│   └── ServerError (5xx)
├── NetworkError
├── TaskError
│   ├── TaskTimeoutError
│   ├── TaskFailedError
│   └── TaskCancelledError
├── SerializationError
├── SchemaValidationError
├── SubscriptionError
└── StrategyError
```

**Import all exceptions:**

```python
from tradepose_client.exceptions import (
    TradePoseError,
    TradePoseConfigError,
    TradePoseAPIError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
    TaskError,
    TaskTimeoutError,
    TaskFailedError,
    TaskCancelledError,
    SerializationError,
    SchemaValidationError,
    SubscriptionError,
    StrategyError,
)
```

---

## Exception Reference

### TradePoseError (Base)

Root exception for all SDK errors.

**Attributes:**
- `message` (`str`): Human-readable error message
- `context` (`dict | None`): Additional context information

**When raised:** Never directly, only via subclasses

**Example:**

```python
from tradepose_client import TradePoseClient, TradePoseError

try:
    async with TradePoseClient(api_key="invalid") as client:
        await client.strategies.list()
except TradePoseError as e:
    # Catches all SDK exceptions
    print(f"SDK Error: {e.message}")
    if e.context:
        print(f"Context: {e.context}")
```

---

### TradePoseConfigError

Configuration validation error.

**Attributes:**
- Inherits from `TradePoseError`

**When raised:**
- Missing API key and JWT token
- Invalid timeout value (< 1.0 or > 600.0)
- Invalid max_retries value (< 0 or > 10)
- Invalid poll_interval or poll_timeout

**How to fix:**
1. Verify at least one authentication method provided
2. Check parameter ranges
3. Verify environment variable names (TRADEPOSE_*)

**Example:**

```python
from tradepose_client import TradePoseClient, TradePoseConfigError

try:
    # Missing both API key and JWT
    client = TradePoseClient()
except TradePoseConfigError as e:
    print(f"Config error: {e.message}")
    # Fix: Provide API key
    client = TradePoseClient(api_key="tp_live_xxx")

try:
    # Invalid timeout
    client = TradePoseClient(api_key="tp_xxx", timeout=1000.0)
except TradePoseConfigError as e:
    print(f"Invalid timeout: {e.message}")
    # Fix: Use valid range (1.0 - 600.0)
    client = TradePoseClient(api_key="tp_xxx", timeout=60.0)
```

---

### AuthenticationError (HTTP 401)

Authentication failed - invalid or expired credentials.

**Attributes:**
- `status_code`: 401
- `request_id` (`str | None`): X-Request-ID for debugging
- `response` (`dict`): Full API response

**When raised:**
- Invalid API key format
- Expired API key
- Revoked API key
- Invalid JWT token
- Expired JWT token

**How to fix:**
1. Verify API key format (tp_live_* or tp_test_*)
2. Check key hasn't been revoked via billing dashboard
3. Regenerate API key if needed
4. For JWT: verify token hasn't expired

**Example:**

```python
from tradepose_client import TradePoseClient, AuthenticationError
import logging

logger = logging.getLogger(__name__)

async def fetch_with_retry(api_key: str):
    try:
        async with TradePoseClient(api_key=api_key) as client:
            return await client.strategies.list()
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e.message}")
        logger.error(f"Request ID: {e.request_id}")

        # Solution: Get new API key
        new_key = await fetch_new_api_key()

        # Retry with new key
        async with TradePoseClient(api_key=new_key) as client:
            return await client.strategies.list()
```

**Prevention:**
- Store API keys securely (environment variables, secret manager)
- Implement key rotation policy
- Monitor key usage via `client.billing.get_usage()`
- Set up alerts for authentication failures

---

### AuthorizationError (HTTP 403)

Insufficient permissions for requested operation.

**Attributes:**
- `status_code`: 403
- `request_id` (`str | None`)
- `response` (`dict`)

**When raised:**
- Attempting to access resource owned by another user
- Subscription plan doesn't include feature
- API key has insufficient permissions

**How to fix:**
1. Verify resource ownership
2. Check subscription plan limits
3. Upgrade plan if needed
4. Use correct API key (production vs test)

**Example:**

```python
from tradepose_client import AuthorizationError

try:
    await client.strategies.delete("SomeoneElsesStrategy")
except AuthorizationError as e:
    print(f"Permission denied: {e.message}")

    # Check subscription limits
    subscription = await client.billing.get_subscription()
    print(f"Current plan: {subscription.plan_tier}")

    # Solution: Upgrade plan or verify ownership
```

---

### ResourceNotFoundError (HTTP 404)

Requested resource does not exist.

**Attributes:**
- `status_code`: 404
- `request_id` (`str | None`)
- `response` (`dict`)

**When raised:**
- Strategy name doesn't exist
- Task ID not found
- API key ID not found

**How to fix:**
1. Verify resource name/ID spelling (case-sensitive)
2. List all resources to confirm existence
3. Check resource wasn't deleted

**Example:**

```python
from tradepose_client import ResourceNotFoundError

async def get_strategy_safe(client, strategy_name: str):
    try:
        return await client.strategies.get(strategy_name)
    except ResourceNotFoundError:
        # Strategy doesn't exist, list all available
        all_strategies = await client.strategies.list()
        available = [s.name for s in all_strategies.strategies]
        print(f"Strategy '{strategy_name}' not found")
        print(f"Available strategies: {available}")
        return None
```

---

### ValidationError (HTTP 422)

Request parameters failed validation.

**Attributes:**
- `status_code`: 422
- `errors` (`list[dict]`): List of validation errors
  - Each error: `{"field": str, "message": str, "type": str}`
- `request_id` (`str | None`)
- `response` (`dict`)

**When raised:**
- Invalid date format
- Date range invalid (end < start)
- Invalid strategy configuration
- Missing required fields
- Field value out of range

**How to fix:**
1. Check each error in `errors` list
2. Verify field formats (dates: ISO format YYYY-MM-DD)
3. Validate strategy config before submission
4. Check parameter constraints

**Example:**

```python
from tradepose_client import ValidationError

try:
    response = await client.export.export_backtest_results(
        start_date="2024-13-01",  # Invalid month
        end_date="2024-12-31",
        strategy_configs=[strategy]
    )
except ValidationError as e:
    print(f"Validation failed: {e.message}")

    # Detailed error information
    for error in e.errors:
        print(f"Field: {error['field']}")
        print(f"Message: {error['message']}")
        print(f"Type: {error['type']}")

    # Fix and retry
    response = await client.export.export_backtest_results(
        start_date="2024-01-01",  # Corrected
        end_date="2024-12-31",
        strategy_configs=[strategy]
    )
```

**Common validation errors:**

| Field | Error | Fix |
|-------|-------|-----|
| start_date | Invalid format | Use "YYYY-MM-DD" format |
| end_date | Must be >= start_date | Swap dates or correct range |
| strategy_configs | Empty list | Provide at least one strategy |
| timeout | Out of range | Use 1.0 - 600.0 |
| poll_interval | Too small | Use >= 0.5 |

---

### RateLimitError (HTTP 429)

API rate limit exceeded.

**Attributes:**
- `status_code`: 429
- `retry_after` (`int | None`): Seconds to wait before retry
- `request_id` (`str | None`)
- `response` (`dict`)

**When raised:**
- Too many requests per minute
- Monthly quota exceeded
- Subscription plan limit reached

**How to fix:**
1. Respect `retry_after` header
2. Implement exponential backoff
3. Reduce request frequency
4. Upgrade subscription plan for higher limits

**Example:**

```python
import asyncio
from tradepose_client import RateLimitError

async def call_with_rate_limit_handling(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.strategies.list()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            # Use retry_after if provided, else exponential backoff
            wait_time = e.retry_after if e.retry_after else (2 ** attempt)

            logger.warning(
                f"Rate limited, waiting {wait_time}s "
                f"(attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(wait_time)

    raise Exception("Max retries exceeded")
```

**Best practices:**
- Check current usage: `await client.billing.get_usage()`
- Implement request queuing for batch operations
- Add jitter to backoff to avoid thundering herd
- Monitor rate limit headers in production

---

### ServerError (HTTP 5xx)

Gateway server error.

**Attributes:**
- `status_code`: 500, 502, 503, 504
- `request_id` (`str | None`)
- `response` (`dict`)

**When raised:**
- Internal server error (500)
- Bad gateway (502)
- Service unavailable (503)
- Gateway timeout (504)

**How to fix:**
1. Retry with exponential backoff
2. Check gateway status page
3. Contact support with request_id
4. Verify no ongoing maintenance

**Example:**

```python
from tradepose_client import ServerError

async def call_with_server_error_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.strategies.list()
        except ServerError as e:
            if attempt == max_retries - 1:
                logger.error(f"Server error after {max_retries} attempts")
                logger.error(f"Request ID: {e.request_id}")
                raise

            wait_time = min(2 ** attempt, 60)  # Cap at 60s
            logger.warning(f"Server error {e.status_code}, retry in {wait_time}s")
            await asyncio.sleep(wait_time)
```

---

### NetworkError

Network connection failed.

**Attributes:**
- `message` (`str`): Error description
- `context` (`dict | None`): Additional details

**When raised:**
- Connection timeout
- DNS resolution failed
- Connection refused
- SSL/TLS errors

**How to fix:**
1. Check internet connectivity
2. Verify server URL is correct
3. Check firewall/proxy settings
4. Increase timeout if needed

**Example:**

```python
from tradepose_client import NetworkError

try:
    async with TradePoseClient(
        api_key="tp_xxx",
        timeout=5.0  # Short timeout
    ) as client:
        await client.strategies.list()
except NetworkError as e:
    if "timeout" in str(e).lower():
        # Increase timeout and retry
        async with TradePoseClient(
            api_key="tp_xxx",
            timeout=30.0
        ) as client:
            await client.strategies.list()
    else:
        # Other network issues
        logger.error(f"Network error: {e.message}")
        # Check connectivity, DNS, etc.
```

---

### TaskTimeoutError

Task polling timeout exceeded.

**Attributes:**
- `task_id` (`str`): Task identifier
- `timeout` (`float`): Timeout duration in seconds
- `message` (`str`)

**When raised:**
- Task still processing after timeout
- Large backtest exceeds default timeout
- Worker overloaded or stuck

**How to fix:**
1. Increase timeout parameter
2. Check task status manually
3. Verify worker is running
4. Contact support with task_id if stuck

**Example:**

```python
from tradepose_client import TaskTimeoutError

try:
    # Large backtest with default timeout (600s)
    response = await client.export.export_backtest_results(
        start_date="2020-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy]
    )
except TaskTimeoutError as e:
    logger.warning(f"Task {e.task_id} timeout after {e.timeout}s")

    # Option 1: Check status manually
    status = await client.tasks.get_status(e.task_id)
    print(f"Current status: {status.status}")
    print(f"Progress: {status.progress}")

    if status.status == "completed":
        # Task completed after timeout
        result = await client.tasks.download_result(e.task_id)
    elif status.status == "processing":
        # Still processing, wait longer
        import asyncio
        await asyncio.sleep(300)  # Wait 5 more minutes
        result = await client.tasks.download_result(e.task_id)

    # Option 2: Retry with longer timeout
    response = await client.export.export_backtest_results(
        start_date="2020-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy],
        timeout=1800.0  # 30 minutes
    )
```

**Timeout guidelines by operation:**

| Operation | Typical Duration | Recommended Timeout |
|-----------|------------------|---------------------|
| Strategy list | < 5s | 60s |
| Strategy register | 10-30s | 300s |
| Backtest (1 year) | 30-120s | 600s |
| Backtest (5 years) | 120-600s | 1800s |
| OHLCV export | 10-60s | 300s |

---

### TaskFailedError

Task execution failed.

**Attributes:**
- `task_id` (`str`): Task identifier
- `error_message` (`str`): Error description from worker
- `message` (`str`)

**When raised:**
- Strategy compilation error
- Invalid strategy configuration
- Data not available for date range
- Worker crashed during execution

**How to fix:**
1. Check error_message for details
2. Validate strategy configuration
3. Verify data availability
4. Retry with corrected strategy

**Example:**

```python
from tradepose_client import TaskFailedError

try:
    response = await client.export.export_backtest_results(
        start_date="2024-01-01",
        end_date="2024-12-31",
        strategy_configs=[strategy]
    )
except TaskFailedError as e:
    logger.error(f"Task {e.task_id} failed: {e.error_message}")

    # Common failure reasons:
    if "compilation" in e.error_message.lower():
        # Strategy compilation error
        print("Strategy has syntax errors, check configuration")
    elif "data" in e.error_message.lower():
        # Data not available
        print("Data not available for date range")
    elif "indicator" in e.error_message.lower():
        # Invalid indicator configuration
        print("Indicator configuration error")
```

---

### TaskCancelledError

Task was cancelled.

**Attributes:**
- `task_id` (`str`): Task identifier
- `message` (`str`)

**When raised:**
- User cancelled task
- System cancelled task (resource limits)

**How to fix:**
- Resubmit task if needed
- Check if cancellation was intentional

---

### SerializationError

Data serialization/deserialization failed.

**Attributes:**
- `data_type` (`str`): Type of data (JSON, Parquet, etc.)
- `message` (`str`)

**When raised:**
- Parquet parsing failed
- JSON decoding error
- Invalid data format from server

**How to fix:**
1. Verify API version compatibility
2. Check for corrupted data
3. Contact support with request_id

---

### SchemaValidationError

Data schema validation failed.

**Attributes:**
- `expected_schema` (`dict | None`): Expected schema
- `actual_schema` (`dict | None`): Actual schema
- `message` (`str`)

**When raised:**
- API response schema changed
- Missing required fields
- Type mismatch

**How to fix:**
1. Update SDK to latest version
2. Check API version compatibility
3. Report schema mismatch to support

---

### SubscriptionError

Subscription or billing error.

**Attributes:**
- `message` (`str`)

**When raised:**
- Subscription inactive
- Plan limit exceeded
- Payment failed

**How to fix:**
1. Check subscription status: `await client.billing.get_subscription()`
2. Update payment method
3. Upgrade plan if limits exceeded

**Example:**

```python
from tradepose_client import SubscriptionError

try:
    response = await client.export.export_backtest_results(...)
except SubscriptionError as e:
    # Check subscription
    subscription = await client.billing.get_subscription()

    if subscription.status == "inactive":
        print("Subscription inactive, please renew")
    elif subscription.status == "past_due":
        print("Payment failed, please update payment method")
    else:
        # Plan limit exceeded
        usage = await client.billing.get_usage()
        print(f"Usage: {usage.current_usage} / {usage.quota}")
        print("Consider upgrading plan")
```

---

### StrategyError

Strategy-specific error.

**Attributes:**
- `message` (`str`)

**When raised:**
- Strategy compilation failed
- Invalid blueprint configuration
- Missing required indicators

**How to fix:**
1. Validate strategy with StrategyBuilder
2. Check all required fields present
3. Verify indicator references are correct

---

## Common Error Scenarios

### Scenario 1: Network Timeout

**Problem:** Request times out after 30 seconds

**Symptoms:**
```python
NetworkError: Connection timeout
```

**Diagnosis:**
```python
# Check if timeout is too short
client = TradePoseClient(api_key="tp_xxx", timeout=5.0)  # Too short!
```

**Solutions:**

```python
# Solution 1: Increase timeout
client = TradePoseClient(api_key="tp_xxx", timeout=60.0)

# Solution 2: Increase per-request timeout
response = await client.export.export_backtest_results(
    ...,
    timeout=1800.0  # 30 minutes for large backtest
)

# Solution 3: Check network connectivity
import httpx
async with httpx.AsyncClient() as http_client:
    response = await http_client.get("https://api.tradepose.com/health")
    print(response.status_code)  # Should be 200
```

---

### Scenario 2: Task Stuck in Processing

**Problem:** Task never completes, stuck at 50% progress

**Symptoms:**
```python
TaskTimeoutError: Task timeout after 600.0s
```

**Diagnosis:**
```python
# Check task status
status = await client.tasks.get_status(task_id)
print(f"Status: {status.status}")  # "processing"
print(f"Progress: {status.progress}")  # 0.5
```

**Solutions:**

```python
# Solution 1: Wait longer
import asyncio

# Poll manually with longer intervals
for i in range(10):  # Wait up to 10 more minutes
    await asyncio.sleep(60)
    status = await client.tasks.get_status(task_id)
    if status.status == "completed":
        result = await client.tasks.download_result(task_id)
        break

# Solution 2: Contact support with task_id
logger.error(f"Task {task_id} stuck, contact support")

# Solution 3: Cancel and resubmit
# (Manual cancellation via dashboard)
```

---

### Scenario 3: Rate Limit Hit During Batch Testing

**Problem:** Batch testing fails midway due to rate limits

**Symptoms:**
```python
RateLimitError: Rate limit exceeded, retry after 60s
```

**Solutions:**

```python
# Solution 1: Reduce poll frequency
tester = BatchTester(
    api_key="tp_xxx",
    poll_interval=5.0  # Slower polling (was 2.0)
)

# Solution 2: Add delay between submissions
import asyncio

for i, period in enumerate(periods):
    batch = tester.submit(strategies=[strategy], periods=[period])
    if i < len(periods) - 1:
        await asyncio.sleep(1.0)  # 1s delay between submissions

# Solution 3: Upgrade subscription plan
subscription = await client.billing.get_subscription()
plans = await client.billing.list_plans()
# Upgrade to higher tier for more quota
```

---

### Scenario 4: Strategy Compilation Error

**Problem:** Strategy registration fails with compilation error

**Symptoms:**
```python
TaskFailedError: Strategy compilation failed: Unknown indicator 'my_custom_indicator'
```

**Solutions:**

```python
# Solution 1: Validate strategy before registration
from tradepose_models import StrategyConfig

try:
    # This will catch validation errors early
    strategy_dict = strategy.model_dump()
    StrategyConfig.model_validate(strategy_dict)
except Exception as e:
    print(f"Validation error: {e}")

# Solution 2: Check indicator references
builder = StrategyBuilder(...)
atr = builder.add_indicator(IndicatorType.ATR, period=14)

# Ensure indicator is added before use
blueprint = BlueprintBuilder(...).add_entry_trigger(
    conditions=[
        atr.col() > 10  # ✓ Correct - atr was added
        # some_other.col() > 5  # ✗ Error - not added
    ],
    ...
)

# Solution 3: Use correct display_name for cross-indicator references
atr = builder.add_indicator(IndicatorType.ATR, period=14)
supertrend = builder.add_indicator(
    IndicatorType.SUPERTREND,
    multiplier=3.0,
    volatility_column=atr.display_name  # ✓ Correct
    # volatility_column="atr"  # ✗ May fail
)
```

---

### Scenario 5: Authentication Suddenly Fails

**Problem:** API calls worked yesterday, now getting 401 errors

**Symptoms:**
```python
AuthenticationError: Invalid API key
```

**Diagnosis:**
```python
# Check if key was revoked
keys = await client.api_keys.list()
for key in keys.api_keys:
    print(f"{key.name}: {key.key_preview} (status: {key.status})")
```

**Solutions:**

```python
# Solution 1: Generate new API key
new_key_response = await client.api_keys.create(name="New Production Key")
new_api_key = new_key_response.key

# Update environment variable
import os
os.environ["TRADEPOSE_API_KEY"] = new_api_key

# Solution 2: Check for JWT expiration (if using JWT)
import jwt

try:
    decoded = jwt.decode(jwt_token, options={"verify_signature": False})
    exp = decoded.get("exp")
    import time
    if exp < time.time():
        print("JWT expired, refresh token")
except Exception as e:
    print(f"JWT decode error: {e}")
```

---

## Best Practices

### 1. Retry Strategy with Exponential Backoff

```python
import asyncio
from typing import TypeVar, Callable
from tradepose_client import NetworkError, ServerError, RateLimitError

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> T:
    """
    Retry with exponential backoff and optional jitter.

    Retryable errors: NetworkError, ServerError, RateLimitError
    """
    import random

    for attempt in range(max_retries):
        try:
            return await func()
        except (NetworkError, ServerError, RateLimitError) as e:
            if attempt == max_retries - 1:
                # Last attempt, re-raise
                raise

            # Calculate delay with exponential backoff
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random() * 0.5)

            # Use retry_after for RateLimitError
            if isinstance(e, RateLimitError) and e.retry_after:
                delay = e.retry_after

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e.message}. "
                f"Retrying in {delay:.1f}s"
            )
            await asyncio.sleep(delay)

    raise Exception("Should never reach here")


# Usage
async def fetch_strategies():
    async with TradePoseClient(api_key="tp_xxx") as client:
        return await retry_with_backoff(
            lambda: client.strategies.list(),
            max_retries=5
        )
```

### 2. Structured Error Logging

```python
import logging
import json
from tradepose_client import TradePoseAPIError

logger = logging.getLogger(__name__)

async def log_api_call(func, operation: str):
    """Log API calls with structured error information."""
    try:
        result = await func()
        logger.info(f"{operation} succeeded")
        return result
    except TradePoseAPIError as e:
        # Structured logging for API errors
        logger.error(
            f"{operation} failed",
            extra={
                "operation": operation,
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_message": e.message,
                "response": json.dumps(e.response) if e.response else None
            }
        )
        raise
    except Exception as e:
        logger.error(f"{operation} failed with unexpected error", exc_info=True)
        raise


# Usage
await log_api_call(
    lambda: client.strategies.list(),
    operation="list_strategies"
)
```

### 3. Circuit Breaker Pattern

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    States:
    - Closed: Normal operation
    - Open: Failing, reject requests immediately
    - Half-Open: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_attempts: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    async def call(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
                self.failure_count = 0
            else:
                raise Exception(
                    f"Circuit breaker open, retry after "
                    f"{self.timeout - (time.time() - self.last_failure_time):.0f}s"
                )

        try:
            result = await func()

            # Success - reset or close circuit
            if self.state == "half_open":
                self.state = "closed"
            self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )

            raise


# Usage
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)

async def protected_call():
    async with TradePoseClient(api_key="tp_xxx") as client:
        return await circuit_breaker.call(
            lambda: client.strategies.list()
        )
```

### 4. Graceful Degradation

```python
async def get_strategies_with_fallback(client: TradePoseClient):
    """
    Get strategies with fallback to cached data.
    """
    try:
        # Try to fetch from API
        response = await client.strategies.list()

        # Cache successful response
        cache_strategies(response.strategies)

        return response.strategies

    except (NetworkError, ServerError) as e:
        logger.warning(f"API unavailable: {e.message}, using cached data")

        # Fallback to cache
        cached = load_cached_strategies()
        if cached:
            return cached

        # No cache available, return empty
        logger.error("No cached data available")
        return []

    except TradePoseAPIError as e:
        logger.error(f"API error: {e.message}")
        raise  # Don't degrade for auth/validation errors


def cache_strategies(strategies):
    """Cache strategies to file."""
    import json
    with open(".strategy_cache.json", "w") as f:
        json.dump([s.model_dump() for s in strategies], f)


def load_cached_strategies():
    """Load strategies from cache."""
    import json
    try:
        with open(".strategy_cache.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

### 5. Error Monitoring and Alerting

```python
import logging
from typing import Callable

class ErrorMonitor:
    """
    Monitor errors and send alerts.
    """

    def __init__(self, alert_threshold: int = 10):
        self.alert_threshold = alert_threshold
        self.error_counts = {}

    async def monitor(self, func: Callable, operation: str):
        """Execute function with error monitoring."""
        try:
            result = await func()
            # Reset error count on success
            self.error_counts[operation] = 0
            return result

        except Exception as e:
            # Increment error count
            self.error_counts[operation] = self.error_counts.get(operation, 0) + 1

            # Send alert if threshold exceeded
            if self.error_counts[operation] >= self.alert_threshold:
                await self.send_alert(operation, e)
                self.error_counts[operation] = 0  # Reset after alert

            raise

    async def send_alert(self, operation: str, error: Exception):
        """Send alert (implement based on your alerting system)."""
        logger.critical(
            f"ALERT: {operation} failed {self.alert_threshold} times",
            extra={"operation": operation, "error": str(error)}
        )
        # Send to Slack, PagerDuty, email, etc.


# Usage
monitor = ErrorMonitor(alert_threshold=10)

async def monitored_call():
    async with TradePoseClient(api_key="tp_xxx") as client:
        return await monitor.monitor(
            lambda: client.strategies.list(),
            operation="list_strategies"
        )
```

---

## Summary

**Key Takeaways:**

1. **Always catch specific exceptions** - Don't catch `Exception`, catch `TradePoseError` or specific subclasses
2. **Log request_id** - Essential for debugging with support
3. **Implement retries** - For `NetworkError`, `ServerError`, `RateLimitError`
4. **Respect rate limits** - Use `retry_after` header
5. **Monitor errors** - Set up alerting for production
6. **Fail gracefully** - Implement fallbacks and circuit breakers
7. **Validate early** - Check configuration before API calls

**Common Patterns:**

- ✅ Retry with exponential backoff
- ✅ Log errors with structured data
- ✅ Use circuit breakers for external services
- ✅ Implement graceful degradation
- ✅ Monitor error rates and alert

**Resources:**
- [Configuration Guide](CONFIGURATION.md) - Timeout and retry settings
- [API Reference](API_REFERENCE.md) - Complete exception documentation
- [Examples](EXAMPLES.md) - Error handling examples
