"""TradePose Python Client SDK.

This package provides a type-safe, async-first Python client for interacting
with the TradePose Gateway API.

Example:
    >>> from tradepose_client import TradePoseClient
    >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
    ...     subscription = await client.billing.get_subscription()
    ...     print(subscription)
"""

# Import enums from tradepose_models for convenient access
from tradepose_models.enums import (
    Freq,
    IndicatorType,
    OrderStrategy,
    TradeDirection,
    TrendType,
)

# Analysis API
from .analysis import (
    ChartConfig,
    MAEMFEAnalyzer,
    MAEMFEStatistics,
)

# Batch testing API
from .batch import (
    BacktestRequest,
    BatchResults,
    BatchTester,
    Period,
    PeriodResult,
)
from .builder import (
    BlueprintBuilder,
    StrategyBuilder,
    TradingContext,
)
from .client import TradePoseClient
from .config import TradePoseConfig
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    SerializationError,
    ServerError,
    StrategyError,
    SubscriptionError,
    TaskCancelledError,
    TaskError,
    TaskFailedError,
    TaskTimeoutError,
    TradePoseAPIError,
    TradePoseConfigError,
    TradePoseError,
    ValidationError,
)

# Portfolio and Registry
from .portfolio import PortfolioBuilder
from .registry import StrategyRegistry, SyncResult

__version__ = "0.1.0"

__all__ = [
    # Main client
    "TradePoseClient",
    "TradePoseConfig",
    # Base exceptions
    "TradePoseError",
    "TradePoseConfigError",
    "TradePoseAPIError",
    # API exceptions
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    # Task exceptions
    "TaskError",
    "TaskTimeoutError",
    "TaskFailedError",
    "TaskCancelledError",
    # Data exceptions
    "SerializationError",
    # Business logic exceptions
    "SubscriptionError",
    "StrategyError",
    # Builder classes
    "StrategyBuilder",
    "BlueprintBuilder",
    "TradingContext",
    # Portfolio and Registry (v0.3.0)
    "PortfolioBuilder",
    "StrategyRegistry",
    "SyncResult",
    # Batch testing API
    "BatchTester",
    "BatchResults",
    "PeriodResult",
    "Period",
    "BacktestRequest",
    # Analysis API
    "MAEMFEAnalyzer",
    "MAEMFEStatistics",
    "ChartConfig",
    # Enums (for convenient strategy building)
    "Freq",
    "IndicatorType",
    "OrderStrategy",
    "TradeDirection",
    "TrendType",
]
