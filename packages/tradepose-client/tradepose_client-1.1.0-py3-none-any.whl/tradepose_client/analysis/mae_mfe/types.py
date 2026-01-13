"""Type definitions for MAE/MFE analysis module."""

from __future__ import annotations

from typing import Literal

# MAE/MFE metric types available in trades_schema
MetricType = Literal["mae", "mfe", "g_mfe", "mae_lv1", "mhl"]

# Normalization modes for chart values
NormalizeMode = Literal["raw", "pct", "volatility"]

# PnL column options (absolute vs percentage)
PnLColumn = Literal["pnl", "pnl_pct"]

# Color-by options for scatter plots
ColorByOption = Literal["direction", "pnl", "holding_bars", "strategy", "blueprint"]

# Chart theme options
ThemeType = Literal["plotly", "plotly_dark", "seaborn", "ggplot2", "simple_white"]

# Metric volatility mapping (metric -> volatility column)
METRIC_VOLATILITY_MAP: dict[str, str] = {
    "mae": "mae_volatility",
    "mfe": "mfe_volatility",
    "g_mfe": "g_mfe_volatility",
    "mae_lv1": "mae_lv1_volatility",
    "mhl": "mhl_volatility",
}

# Required columns for MAE/MFE analysis (pnl column validated separately)
REQUIRED_COLUMNS: set[str] = {
    "direction",
}

# Optional metric columns (at least one MAE and one MFE type should be present)
MAE_COLUMNS: set[str] = {"mae", "mae_lv1"}
MFE_COLUMNS: set[str] = {"mfe", "g_mfe", "mhl"}

# All metric columns
ALL_METRIC_COLUMNS: set[str] = MAE_COLUMNS | MFE_COLUMNS

# Columns needed for specific features
HOLDING_COLUMNS: set[str] = {"holding_bars", "holding_seconds"}
VOLATILITY_COLUMNS: set[str] = set(METRIC_VOLATILITY_MAP.values()) | {
    "entry_volatility",
    "exit_volatility",
}
PRICE_COLUMNS: set[str] = {"entry_price", "exit_price"}
STRATEGY_COLUMNS: set[str] = {"strategy_name", "blueprint_name"}
