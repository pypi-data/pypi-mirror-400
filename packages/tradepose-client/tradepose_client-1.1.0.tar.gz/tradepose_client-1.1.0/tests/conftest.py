"""
Shared pytest fixtures for client unit tests.

This module provides common fixtures for testing client components:
- Mocked httpx.AsyncClient for HTTP requests
- Mocked authentication (API key and JWT)
- Sample configurations and responses
- Test data generators
"""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

# TODO: Import from tradepose_client
# from tradepose_client import TradePoseClient, TradePoseConfig


# ============================================================================
# HTTP Client Fixtures
# ============================================================================


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing HTTP requests."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    # Mock successful response
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.content = b"binary_data"
    mock_response.headers = {"content-type": "application/json"}
    mock_response.raise_for_status = Mock()

    # Default request behavior
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.put = AsyncMock(return_value=mock_response)
    mock_client.delete = AsyncMock(return_value=mock_response)

    # Context manager support
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.aclose = AsyncMock()

    return mock_client


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def test_config_api_key():
    """Test configuration with API key authentication."""
    return {
        "server_url": "https://api.tradepose.com",
        "api_key": "sk_test_1234567890abcdef",
        "timeout": 30.0,
        "max_retries": 3,
        "log_level": "INFO",
    }


@pytest.fixture
def test_config_jwt():
    """Test configuration with JWT authentication."""
    return {
        "server_url": "https://api.tradepose.com",
        "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "timeout": 30.0,
        "max_retries": 3,
    }


@pytest.fixture
def test_config_no_auth():
    """Test configuration without authentication (should fail)."""
    return {"server_url": "https://api.tradepose.com"}


# ============================================================================
# Response Fixtures
# ============================================================================


@pytest.fixture
def mock_task_response():
    """Mock task status response."""
    return {
        "task_id": "task_123456",
        "status": "completed",
        "operation_type": "export",
        "export_type": "backtest-results",
        "created_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:05:00Z",
    }


@pytest.fixture
def mock_api_key_response():
    """Mock API key creation response."""
    return {
        "key_id": "key_123456",
        "key": "sk_1234567890abcdef",
        "key_preview": "sk_123...def",
        "name": "Test API Key",
        "created_at": "2025-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_strategy_list_response():
    """Mock strategy list response."""
    return {"task_id": "task_list_123", "operation_type": "list_strategies"}


@pytest.fixture
def mock_export_response():
    """Mock export task creation response."""
    return {
        "task_id": "task_export_123",
        "export_type": "backtest-results",
        "status": "pending",
    }


@pytest.fixture
def mock_parquet_data():
    """Mock Parquet binary data for result downloads."""
    return b"\x50\x41\x52\x31\x00\x00..."  # Fake Parquet header


@pytest.fixture
def mock_performance_json():
    """Mock performance metrics JSON response."""
    return {
        "total_return": 0.25,
        "sharpe_ratio": 1.5,
        "max_drawdown": -0.15,
        "win_rate": 0.65,
    }


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def api_key_auth():
    """Mock API key authentication."""
    # TODO: Create APIKeyAuth instance
    pass


@pytest.fixture
def jwt_auth():
    """Mock JWT authentication."""
    # TODO: Create JWTAuth instance
    pass


# ============================================================================
# Resource Fixtures
# ============================================================================


@pytest.fixture
def mock_base_resource(mock_httpx_client):
    """Mock BaseResource with httpx client."""
    # TODO: Create BaseResource with mock client
    pass


# ============================================================================
# Builder Fixtures
# ============================================================================


@pytest.fixture
def strategy_builder():
    """Create StrategyBuilder instance for testing."""
    # TODO: from tradepose_client.builder import StrategyBuilder
    # return StrategyBuilder(name="test_strategy", base_instrument="BTCUSDT", base_freq="1h")
    pass


@pytest.fixture
def blueprint_builder():
    """Create BlueprintBuilder instance for testing."""
    # TODO: from tradepose_client.builder import BlueprintBuilder
    # return BlueprintBuilder(name="test_blueprint", direction="long", trend_type="trending")
    pass


# ============================================================================
# Test Data Generators
# ============================================================================


@pytest.fixture
def generate_mock_indicator_spec():
    """Generate mock IndicatorSpec."""

    def _generate(indicator_type="SMA", params=None):
        return {
            "indicator_type": indicator_type,
            "params": params or {"period": 20},
            "instrument_id": "BTCUSDT",
            "freq": "1h",
        }

    return _generate


@pytest.fixture
def generate_mock_trigger():
    """Generate mock trigger."""

    def _generate(name="test_trigger", conditions=None):
        return {
            "name": name,
            "conditions": conditions or ["price > sma_20"],
            "price_expr": "close",
            "order_strategy": "market",
        }

    return _generate
