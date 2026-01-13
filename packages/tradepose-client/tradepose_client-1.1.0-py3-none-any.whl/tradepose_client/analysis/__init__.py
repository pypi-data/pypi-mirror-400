"""Analysis module for TradePose Client.

This module provides data analysis and visualization tools for trading data.

Submodules:
    mae_mfe: MAE/MFE (Maximum Adverse/Favorable Excursion) analysis
"""

from .mae_mfe import (
    DARK_CONFIG,
    DEFAULT_CONFIG,
    ChartConfig,
    DashboardConfig,
    MAEMFEAnalyzer,
    MAEMFEStatistics,
)

__all__ = [
    # MAE/MFE Analysis
    "MAEMFEAnalyzer",
    "MAEMFEStatistics",
    "ChartConfig",
    "DashboardConfig",
    "DEFAULT_CONFIG",
    "DARK_CONFIG",
]
