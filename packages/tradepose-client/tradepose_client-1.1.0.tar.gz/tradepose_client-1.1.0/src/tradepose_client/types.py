"""Type aliases and type hints for TradePose Client.

This module defines common type aliases used throughout the client library
to improve code readability and maintainability.
"""

from typing import Any, TypeAlias

import polars as pl

# HTTP-related types
Headers: TypeAlias = dict[str, str]
QueryParams: TypeAlias = dict[str, str | int | float | bool]
JSONData: TypeAlias = dict[str, Any]

# Response types
ResponseData: TypeAlias = dict[str, Any] | list[Any] | bytes

# Data types
DataFrame: TypeAlias = pl.DataFrame
ParquetData: TypeAlias = bytes

# Authentication types
AuthType: TypeAlias = str  # 'api_key' | 'jwt'
