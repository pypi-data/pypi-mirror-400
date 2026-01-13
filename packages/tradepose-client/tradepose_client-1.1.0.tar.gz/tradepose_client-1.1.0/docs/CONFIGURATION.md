# Configuration

Complete configuration reference for TradePose Client SDK.

## Table of Contents

1. [Quick Start](#quick-start)
2. [BatchTester Configuration](#batchtester-configuration)
3. [Environment Variables](#environment-variables)
4. [TradePoseClient Configuration](#tradeposeclient-configuration-low-level)
5. [Scenario-Based Examples](#scenario-based-examples)
6. [Security Best Practices](#security-best-practices)

---

## Quick Start

### Minimal Configuration

```python
from tradepose_client import BatchTester

# Simplest: API key from environment variable
# Set: export TRADEPOSE_API_KEY="tp_live_xxx"
tester = BatchTester()

# Or: API key as parameter
tester = BatchTester(api_key="tp_live_xxx")
```

**That's it!** Defaults work for most users.

---

## BatchTester Configuration

Primary interface for batch testing workflows.

### Initialization Parameters

```python
from tradepose_client import BatchTester

tester = BatchTester(
    api_key="tp_live_xxx",              # API key (or from TRADEPOSE_API_KEY)
    server_url="https://api.tradepose.com",  # Gateway URL (optional)
    poll_interval=2.0,                  # Polling interval in seconds
    auto_download=True                  # Auto-download results on completion
)
```

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `api_key` | str | None | - | API key for authentication (required if not in env) |
| `server_url` | str | https://api.tradepose.com | - | Gateway server URL |
| `poll_interval` | float | 2.0 | 0.5 - 60.0 | Status polling interval (seconds) |
| `auto_download` | bool | True | - | Automatically download completed results |

### Configuration Examples

#### Development (Fast Polling)

```python
tester = BatchTester(
    api_key="tp_test_xxx",       # Test API key
    poll_interval=1.0,           # Poll every second (faster feedback)
    auto_download=True
)
```

#### Production (Conservative Polling)

```python
tester = BatchTester(
    api_key="tp_live_xxx",       # Production API key
    poll_interval=5.0,           # Poll every 5 seconds (reduce API calls)
    auto_download=True
)
```

#### Staging Environment

```python
tester = BatchTester(
    api_key="tp_test_xxx",
    server_url="https://api-staging.tradepose.com",  # Staging server
    poll_interval=2.0
)
```

---

## Environment Variables

All environment variables use the `TRADEPOSE_` prefix.

### Authentication (Required)

#### TRADEPOSE_API_KEY

API key for authentication.

- **Type:** str
- **Format:** `tp_live_*` (production) or `tp_test_*` (test)
- **Required:** Yes (unless using JWT)
- **Example:** `export TRADEPOSE_API_KEY="tp_live_abc123..."`

**How to obtain:**
1. Log in to TradePose dashboard
2. Settings → API Keys
3. Create new key
4. Copy and store securely (shown only once)

**Security:**
- Never commit to version control
- Rotate every 90 days
- Use different keys for dev/prod
- Revoke unused keys

#### TRADEPOSE_JWT_TOKEN

JWT token for authentication (alternative to API key).

- **Type:** str
- **Format:** Standard JWT token
- **Use case:** Creating new API keys programmatically
- **Example:** `export TRADEPOSE_JWT_TOKEN="eyJhbGci..."`

**Note:** JWT tokens expire (typically 1 hour). API keys do not expire.

### Server Configuration

#### TRADEPOSE_SERVER_URL

Gateway server URL.

- **Type:** str
- **Default:** `https://api.tradepose.com`
- **Example:** `export TRADEPOSE_SERVER_URL="https://api-staging.tradepose.com"`

**Common values:**
- Production: `https://api.tradepose.com`
- Staging: `https://api-staging.tradepose.com`
- Local dev: `http://localhost:8000`

### HTTP Settings (Low-Level)

These settings apply to TradePoseClient (used internally by BatchTester).

#### TRADEPOSE_TIMEOUT

Request timeout in seconds.

- **Type:** float
- **Default:** 30.0
- **Range:** 1.0 - 600.0
- **Example:** `export TRADEPOSE_TIMEOUT="60.0"`

**Recommended values:**
- Fast operations (list, get): 10.0
- Long operations (backtest, export): 60.0 - 120.0

#### TRADEPOSE_MAX_RETRIES

Maximum retry attempts for failed requests.

- **Type:** int
- **Default:** 3
- **Range:** 0 - 10
- **Example:** `export TRADEPOSE_MAX_RETRIES="5"`

**When to increase:**
- Flaky network connections
- High-latency environments
- Critical production workloads

### Task Polling Settings

#### TRADEPOSE_POLL_INTERVAL

Status polling interval in seconds (for TradePoseClient auto-poll).

- **Type:** float
- **Default:** 2.0
- **Range:** 0.5 - 60.0
- **Example:** `export TRADEPOSE_POLL_INTERVAL="5.0"`

**Note:** BatchTester uses its own `poll_interval` parameter (not this env var).

#### TRADEPOSE_POLL_TIMEOUT

Maximum polling duration in seconds.

- **Type:** float
- **Default:** 300.0 (5 minutes)
- **Range:** 10.0 - 3600.0
- **Example:** `export TRADEPOSE_POLL_TIMEOUT="600.0"`

### Logging

#### TRADEPOSE_DEBUG

Enable debug logging.

- **Type:** bool
- **Default:** false
- **Example:** `export TRADEPOSE_DEBUG="true"`

**When enabled:**
- Logs all HTTP requests/responses
- Logs polling status changes
- Logs authentication details (excluding secrets)

#### TRADEPOSE_LOG_LEVEL

Logging level.

- **Type:** str
- **Default:** INFO
- **Values:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Example:** `export TRADEPOSE_LOG_LEVEL="DEBUG"`

---

## TradePoseClient Configuration (Low-Level)

For advanced users needing async control. Most users should use BatchTester.

### Configuration Object

```python
from tradepose_client import TradePoseClient, TradePoseConfig

config = TradePoseConfig(
    api_key="tp_live_xxx",
    timeout=60.0,
    max_retries=5,
    poll_interval=2.0,
    poll_timeout=600.0,
    debug=True
)

async with TradePoseClient(config=config) as client:
    strategies = await client.strategies.list()
```

### Direct Parameters

```python
async with TradePoseClient(
    api_key="tp_live_xxx",
    timeout=60.0,
    max_retries=3
) as client:
    pass
```

**See [LOW_LEVEL_API.md](LOW_LEVEL_API.md) for complete TradePoseClient documentation.**

---

## Scenario-Based Examples

### Development Environment

```bash
# .env.development
TRADEPOSE_API_KEY="tp_test_dev_xxx"
TRADEPOSE_SERVER_URL="http://localhost:8000"
TRADEPOSE_DEBUG="true"
TRADEPOSE_LOG_LEVEL="DEBUG"
```

```python
from tradepose_client import BatchTester

# Auto-loads from .env.development
tester = BatchTester(poll_interval=1.0)  # Fast polling for dev
```

### Testing / CI Environment

```bash
# .env.test
TRADEPOSE_API_KEY="tp_test_ci_xxx"
TRADEPOSE_SERVER_URL="https://api-staging.tradepose.com"
TRADEPOSE_TIMEOUT="120.0"
TRADEPOSE_MAX_RETRIES="5"
TRADEPOSE_LOG_LEVEL="INFO"
```

```python
from tradepose_client import BatchTester

tester = BatchTester(
    poll_interval=2.0,
    auto_download=True
)
```

### Production Environment

```bash
# .env.production
TRADEPOSE_API_KEY="tp_live_prod_xxx"
TRADEPOSE_TIMEOUT="60.0"
TRADEPOSE_MAX_RETRIES="3"
TRADEPOSE_POLL_INTERVAL="5.0"
TRADEPOSE_POLL_TIMEOUT="1800.0"  # 30 minutes
TRADEPOSE_DEBUG="false"
TRADEPOSE_LOG_LEVEL="WARNING"
```

```python
from tradepose_client import BatchTester

tester = BatchTester(
    poll_interval=5.0,  # Reduce API calls
    auto_download=True
)
```

### Jupyter Notebook

```python
# Jupyter notebooks work out of the box
from tradepose_client import BatchTester
from tradepose_client.batch import Period

tester = BatchTester(api_key="tp_live_xxx")

batch = tester.submit(
    strategies=[strategy],
    periods=[Period.Q1(2024)]
)

# No async/await needed!
batch.wait()
trades = batch.all_trades()
```

**Note:** BatchTester automatically detects Jupyter and applies `nest_asyncio`.

### Multiple Environments

```python
import os
from tradepose_client import BatchTester

# Switch based on environment variable
env = os.getenv("APP_ENV", "development")

config = {
    "development": {
        "api_key": "tp_test_dev_xxx",
        "server_url": "http://localhost:8000",
        "poll_interval": 1.0
    },
    "staging": {
        "api_key": "tp_test_staging_xxx",
        "server_url": "https://api-staging.tradepose.com",
        "poll_interval": 2.0
    },
    "production": {
        "api_key": os.getenv("TRADEPOSE_API_KEY"),  # From env var
        "poll_interval": 5.0
    }
}

tester = BatchTester(**config[env])
```

---

## Security Best Practices

### API Key Management

#### Never Commit Secrets

```python
# ❌ BAD: Hardcoded API key
tester = BatchTester(api_key="tp_live_abc123...")

# ✅ GOOD: From environment variable
tester = BatchTester()  # Reads TRADEPOSE_API_KEY

# ✅ GOOD: From secrets manager
import boto3
def get_api_key():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='tradepose/api-key')
    return json.loads(response['SecretString'])['api_key']

tester = BatchTester(api_key=get_api_key())
```

#### Use .gitignore

```bash
# .gitignore
.env
.env.local
.env.*.local
*.key
secrets.json
```

#### Rotate API Keys Regularly

```python
# Recommended: Every 90 days
from tradepose_client import TradePoseClient
import asyncio

async def rotate_api_key():
    async with TradePoseClient(api_key="old_key_xxx") as client:
        # Create new key
        new_key = await client.api_keys.create(name="Production (2025-Q1)")
        print(f"New key: {new_key.key}")

        # Test new key
        test_client = TradePoseClient(api_key=new_key.key)
        await test_client.strategies.list()  # Verify it works

        # Update secrets manager
        update_secret_manager(new_key.key)

        # Revoke old key
        await client.api_keys.revoke(old_key_id)

asyncio.run(rotate_api_key())
```

### Secure Storage

#### AWS Secrets Manager

```python
import boto3
import json

def get_api_key_from_aws():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='tradepose/api-key')
    secret = json.loads(response['SecretString'])
    return secret['api_key']

from tradepose_client import BatchTester
tester = BatchTester(api_key=get_api_key_from_aws())
```

#### GitHub Actions Secrets

```yaml
# .github/workflows/test.yml
name: Run Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run batch tests
        env:
          TRADEPOSE_API_KEY: ${{ secrets.TRADEPOSE_API_KEY }}
        run: |
          python run_batch_tests.py
```

#### Docker Secrets

```bash
# Create secret
echo "tp_live_xxx" | docker secret create tradepose_api_key -

# Use in docker-compose.yml
version: '3.8'
services:
  app:
    image: my-trading-app
    secrets:
      - tradepose_api_key
    environment:
      TRADEPOSE_API_KEY_FILE: /run/secrets/tradepose_api_key

secrets:
  tradepose_api_key:
    external: true
```

```python
# Read secret from file
import os

def get_api_key():
    secret_file = os.getenv('TRADEPOSE_API_KEY_FILE')
    if secret_file:
        with open(secret_file) as f:
            return f.read().strip()
    return os.getenv('TRADEPOSE_API_KEY')

from tradepose_client import BatchTester
tester = BatchTester(api_key=get_api_key())
```

### Least Privilege Principle

**Create separate keys for different purposes:**

```python
# Key 1: Read-only (CI/CD testing)
readonly_key = await client.api_keys.create(
    name="CI Read-Only",
    permissions=["strategies:read", "export:read"]
)

# Key 2: Full access (production deployment)
admin_key = await client.api_keys.create(
    name="Production Admin",
    permissions=["*"]
)

# Key 3: Development
dev_key = await client.api_keys.create(
    name="Development",
    permissions=["strategies:*", "export:*"]
)
```

**Use appropriate key for each environment.**

### Monitoring and Auditing

```python
# Log API key usage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from tradepose_client import BatchTester

tester = BatchTester(api_key=get_api_key())
logger.info(f"Initialized BatchTester with key preview: {tester._api_key[:10]}...")

batch = tester.submit(strategies=[s1], periods=[Period.Q1(2024)])
logger.info(f"Submitted batch {batch.batch_id} with {batch.task_count} tasks")
```

**Review API key usage regularly:**
- Check last_used_at timestamps
- Revoke keys not used in 90+ days
- Monitor for unusual activity

---

## See Also

- [README.md](../README.md) - Project overview and quick start
- [EXAMPLES.md](EXAMPLES.md) - Real-world usage examples
- [LOW_LEVEL_API.md](LOW_LEVEL_API.md) - Async API documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Exception handling guide
