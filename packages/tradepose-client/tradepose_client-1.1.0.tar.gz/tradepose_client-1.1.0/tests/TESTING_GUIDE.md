# Client Package Testing Guide

## Overview

This directory contains unit tests for the `tradepose-client` package. All tests use mocked dependencies (no actual HTTP requests or external services).

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── test_client.py                   # TradePoseClient tests
├── test_config.py                   # Configuration tests
├── test_exceptions.py               # Exception hierarchy tests
├── auth/
│   ├── test_api_key_auth.py        # API key authentication
│   └── test_jwt_auth.py            # JWT authentication
├── resources/
│   ├── test_base_resource.py       # Base HTTP operations
│   ├── test_tasks.py               # Task operations
│   ├── test_api_keys.py            # API key management
│   ├── test_billing.py             # Billing operations
│   ├── test_strategies.py          # Strategy management
│   └── test_export.py              # Export operations
└── builder/
    ├── test_strategy_builder.py    # Strategy builder fluent API
    ├── test_blueprint_builder.py   # Blueprint builder
    ├── test_indicator_wrapper.py   # Indicator wrapper
    └── test_trading_context.py     # Trading context accessors
```

## Running Tests

### Run all client tests
```bash
uv run --package tradepose-client pytest packages/client/tests/ -v
```

### Run specific test file
```bash
uv run --package tradepose-client pytest packages/client/tests/test_client.py -v
```

### Run with coverage
```bash
uv run --package tradepose-client pytest packages/client/tests/ --cov=tradepose_client --cov-report=html
```

### Run tests by category
```bash
# Only authentication tests
uv run --package tradepose-client pytest packages/client/tests/auth/ -v

# Only resource tests
uv run --package tradepose-client pytest packages/client/tests/resources/ -v

# Only builder tests
uv run --package tradepose-client pytest packages/client/tests/builder/ -v
```

## Test Categories

### 1. Core Tests (`test_client.py`, `test_config.py`, `test_exceptions.py`)
- Client initialization and configuration
- Environment variable loading
- Exception hierarchy and error handling

### 2. Authentication Tests (`auth/`)
- API key header injection
- JWT header injection
- Authentication priority and fallback

### 3. Resource Tests (`resources/`)
- HTTP request/response handling
- Error mapping (401, 403, 404, 429, 5xx)
- Binary data handling (Parquet downloads)
- JSON response parsing

### 4. Builder Tests (`builder/`)
- Fluent API chaining
- Strategy and blueprint construction
- Indicator specification creation
- Trading context field accessors

## Mocking Strategy

### HTTP Requests
All HTTP requests are mocked using `unittest.mock.AsyncMock`:
```python
@pytest.fixture
def mock_httpx_client():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_client.get = AsyncMock(return_value=mock_response)
    return mock_client
```

### Configuration
Environment variables are mocked using `pytest.monkeypatch` or `unittest.mock.patch.dict`:
```python
def test_config_from_env(monkeypatch):
    monkeypatch.setenv("TRADEPOSE_API_KEY", "sk_test_123")
    config = TradePoseConfig()
    assert config.api_key == "sk_test_123"
```

### Authentication
Authentication handlers are tested independently with mocked headers:
```python
def test_api_key_auth():
    auth = APIKeyAuth("sk_test_123")
    headers = auth.get_headers()
    assert headers["X-API-Key"] == "sk_test_123"
```

## Writing New Tests

### Test Template
```python
"""
Test module for [Component Name]

Test Categories:
1. Happy path - Normal successful operations
2. Validation - Input validation and type checking
3. Error handling - Exception scenarios
4. Edge cases - Boundary conditions, None values
"""

import pytest
from unittest.mock import AsyncMock, Mock

class Test[ComponentName]:
    """Test suite for [ComponentName]."""

    @pytest.mark.asyncio
    async def test_[operation]_success(self, mock_httpx_client):
        """
        Test successful [operation].

        Given: [preconditions]
        When: [action]
        Then: [expected outcome]
        """
        # TODO: Arrange - Set up mocks and inputs
        # TODO: Act - Call the method under test
        # TODO: Assert - Verify expected behavior
        pass
```

### Best Practices
1. **One assertion per test** - Focus on testing one thing
2. **Clear test names** - Use `test_<what>_<condition>_<expected>` format
3. **Given-When-Then** - Structure tests with clear sections
4. **Mock at boundaries** - Mock httpx client, not internal methods
5. **Test error paths** - Don't just test happy paths

## Common Patterns

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_operation(self, mock_httpx_client):
    # Arrange
    resource = TasksResource(mock_httpx_client)

    # Act
    result = await resource.get_status("task_123")

    # Assert
    assert result["status"] == "completed"
```

### Testing HTTP Errors
```python
@pytest.mark.asyncio
async def test_handles_404(self, mock_httpx_client):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not found"}
    mock_httpx_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(ResourceNotFoundError):
        await resource.get_status("nonexistent")
```

### Testing Builder Pattern
```python
def test_fluent_api_chaining(self):
    # Act
    strategy = (
        StrategyBuilder("test", "BTCUSDT", "1h")
        .add_indicator("SMA", period=20)
        .add_indicator("RSI", period=14)
        .build()
    )

    # Assert
    assert len(strategy.indicators) == 2
    assert strategy.indicators[0].indicator_type == "SMA"
```

## Coverage Goals

- **Overall**: >80% line coverage
- **Core modules** (client, config): >90%
- **Resources**: >85%
- **Builders**: >75%
- **Utilities**: >80%

## Troubleshooting

### Test failures due to import errors
```bash
# Ensure package is installed in editable mode
uv pip install -e packages/client
```

### Async test warnings
```bash
# Install pytest-asyncio
uv pip install pytest-asyncio
```

### Coverage not generating
```bash
# Install pytest-cov
uv pip install pytest-cov
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
