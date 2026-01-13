"""MAE/MFE Analysis Module.

This module provides comprehensive analysis and visualization tools for
Maximum Adverse Excursion (MAE) and Maximum Favorable Excursion (MFE) metrics.

Example:
    >>> from tradepose_client.analysis import MAEMFEAnalyzer
    >>>
    >>> # Initialize with trades DataFrame
    >>> analyzer = MAEMFEAnalyzer(trades_df)
    >>>
    >>> # Core scatter plot
    >>> analyzer.scatter_mae_mfe().show()
    >>>
    >>> # Filtered analysis with chaining
    >>> analyzer.filter(direction=1, profitable=True).scatter_pnl_mae().show()
    >>>
    >>> # Statistics
    >>> stats = analyzer.statistics()
    >>> print(stats.summary())
    >>>
    >>> # Full dashboard
    >>> analyzer.dashboard().show()
"""

from .analyzer import MAEMFEAnalyzer
from .config import DARK_CONFIG, DEFAULT_CONFIG, ChartConfig, DashboardConfig
from .statistics import MAEMFEStatistics
from .types import ColorByOption, MetricType, NormalizeMode, ThemeType

__all__ = [
    # Main class
    "MAEMFEAnalyzer",
    # Statistics
    "MAEMFEStatistics",
    # Configuration
    "ChartConfig",
    "DashboardConfig",
    "DEFAULT_CONFIG",
    "DARK_CONFIG",
    # Types
    "MetricType",
    "NormalizeMode",
    "ColorByOption",
    "ThemeType",
]
