# MAE/MFE Analysis Module Specification

## Overview

MAE/MFE (Maximum Adverse/Favorable Excursion) analysis helps traders understand how far a trade moved against them (adverse) or in their favor (favorable) before closing.

```
                    Entry                              Exit
                      │                                  │
    ┌─────────────────┼──────────────────────────────────┼─────────────────┐
    │                 │          Trade Lifecycle         │                 │
    │     ▲           │                                  │                 │
    │     │ MFE       │    ╭─────╮      ╭──────╮        │                 │
    │     │           │   ╱       ╲    ╱        ╲       │                 │
Price   ──┼───────────┼──╱─────────╲──╱──────────╲──────┼─── Final PnL    │
    │     │           │ ╱           ╲╱            ╲     │                 │
    │     │           │╱                           ╲    │                 │
    │     │ MAE       ╰─────────────────────────────╲───│                 │
    │     ▼                                          ╲──┤                 │
    │                                                   │                 │
    └───────────────────────────────────────────────────┴─────────────────┘
                                  Time →

    MAE = Maximum Adverse Excursion (worst drawdown during trade)
    MFE = Maximum Favorable Excursion (best unrealized profit during trade)
```

## Core Concepts

### Metric Types

| Metric | Description | Use Case |
|--------|-------------|----------|
| `mae` | Maximum Adverse Excursion | Basic stop-loss analysis |
| `mae_lv1` | MAE at Level 1 | Entry quality assessment |
| `mfe` | Maximum Favorable Excursion | Take-profit optimization |
| `g_mfe` | Guaranteed MFE | Conservative profit target |
| `mhl` | Maximum High-Low range | Volatility assessment |

### Normalization Modes

```
┌────────────────────────────────────────────────────────────────────┐
│                     Normalization Modes                            │
├─────────────┬──────────────────────────────────────────────────────┤
│ raw         │ Absolute price units (e.g., $150)                    │
│ pct         │ Percentage of entry price (e.g., 1.5%)               │
│ volatility  │ ATR-normalized (e.g., 2.3x ATR)                      │
└─────────────┴──────────────────────────────────────────────────────┘
```

### PnL Column Selection

Users can analyze trades using either:
- `pnl`: Absolute profit/loss value
- `pnl_pct`: Percentage profit/loss

```python
# Absolute PnL analysis (default)
analyzer = MAEMFEAnalyzer(trades)

# Percentage PnL analysis
analyzer = MAEMFEAnalyzer(trades, pnl_column="pnl_pct")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       MAEMFEAnalyzer                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Configuration                                           │   │
│  │  • ChartConfig (colors, sizes, theme)                    │   │
│  │  • pnl_column selection                                  │   │
│  │  • Available metrics detection                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Fluent Filtering API                                    │   │
│  │  • .filter(direction=1, profitable=True, ...)            │   │
│  │  • .reset_filters()                                      │   │
│  │  • Returns new instance (immutable pattern)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────┬─────────────┬─────────────┬────────────────┐   │
│  │  Scatter    │ Distribution│   Ratio     │   Time-based   │   │
│  │  Charts     │   Charts    │   Charts    │    Charts      │   │
│  ├─────────────┼─────────────┼─────────────┼────────────────┤   │
│  │ mae vs mfe  │ mae dist    │ mfe/mae     │ timeline       │   │
│  │ pnl vs mae  │ mfe dist    │ histogram   │ box by holding │   │
│  │ pnl vs mfe  │ comparison  │             │ rolling stats  │   │
│  └─────────────┴─────────────┴─────────────┴────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Statistics & Dashboard                                  │   │
│  │  • MAEMFEStatistics dataclass                            │   │
│  │  • Dashboard (combined subplot view)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
mae_mfe/
├── __init__.py      # Public exports
├── types.py         # Type definitions (MetricType, NormalizeMode, etc.)
├── config.py        # ChartConfig, DashboardConfig
├── analyzer.py      # MAEMFEAnalyzer class
├── charts.py        # Chart creation functions
├── statistics.py    # Statistics calculation
├── rolling.py       # Rolling window analysis
└── SPEC.md          # This file
```

## API Reference

### Initialization

```python
from tradepose_client.analysis import MAEMFEAnalyzer

analyzer = MAEMFEAnalyzer(
    trades,                    # Polars DataFrame
    config=ChartConfig(...),   # Optional chart config
    pnl_column="pnl",          # "pnl" or "pnl_pct"
)
```

### Filtering (Fluent API)

```python
# All filters return a new analyzer instance (chainable)
filtered = analyzer.filter(
    direction=1,               # 1=Long, -1=Short
    strategy="my_strategy",    # Strategy name(s)
    blueprint="my_blueprint",  # Blueprint name(s)
    profitable=True,           # Winners only
    min_holding_bars=5,        # Minimum holding period
    max_holding_bars=100,      # Maximum holding period
)

# Chain multiple operations
analyzer.filter(direction=1).filter(profitable=True).scatter_mae_mfe()

# Reset all filters
original = filtered.reset_filters()
```

### Chart Methods

#### Scatter Charts

```
┌─────────────────────────────────────────────────────────────────┐
│  scatter_mae_mfe()                                              │
│  ─────────────────                                              │
│       MFE                                                       │
│        ▲                                                        │
│        │      ·  ·                                              │
│        │   · · ·  · ·    Good trades                            │
│        │  ·  · ·   ·  ·  (high MFE, low MAE)                    │
│        │───────────────────────────                             │
│        │  ·  · ·   ·                                            │
│        │   ·   ·     Bad trades                                 │
│        │    ·        (high MAE, low MFE)                        │
│        └────────────────────────────────▶ MAE                   │
│                                                                 │
│  Options: color_by, normalize, show_quadrants, show_diagonal   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  scatter_pnl_mae() / scatter_pnl_mfe()                          │
│  ─────────────────────────────────────                          │
│      MAE/MFE                                                    │
│        ▲                                                        │
│        │         ·                                              │
│        │       · · ·                                            │
│        │     ·   ·   ·                                          │
│        │   ·   ·   ·   ·                                        │
│ ───────┼───────────────────▶ PnL                                │
│        │ · ·   ·   ·                                            │
│        │   · ·   ·                                              │
│        │     ·                                                  │
│                                                                 │
│  Options: show_regression, color_by, normalize                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Distribution Charts

```
┌─────────────────────────────────────────────────────────────────┐
│  distribution_mae() / distribution_mfe()                        │
│  ───────────────────────────────────────                        │
│                                                                 │
│   Count                                                         │
│     ▲                                                           │
│     │       ╭───╮                                               │
│     │      ╱     ╲                                              │
│     │     ╱       ╲                                             │
│     │   ╱           ╲                                           │
│     │  ╱             ╲                                          │
│     │ ╱               ╲                                         │
│     └─────────────────────────▶ Value                           │
│                                                                 │
│  Options: by_outcome (split winners/losers), bins, normalize    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  distribution_comparison()                                      │
│  ─────────────────────────                                      │
│                                                                 │
│     ▲      MAE     MFE     PnL                                  │
│     │      ╭─╮     ╭─╮     ╭─╮                                  │
│     │     ╱   ╲   ╱   ╲   ╱   ╲                                 │
│     │    ╱     ╲ ╱     ╲ ╱     ╲                                │
│     │   ╱       X       X       ╲                               │
│     │  ╱       ╱ ╲     ╱ ╲       ╲                              │
│     └─────────────────────────────▶                             │
│                                                                 │
│  Overlays multiple metric distributions for comparison          │
└─────────────────────────────────────────────────────────────────┘
```

#### Ratio & Relationship Charts

```
┌─────────────────────────────────────────────────────────────────┐
│  ratio_mfe_mae()                                                │
│  ───────────────                                                │
│                                                                 │
│     Count                                                       │
│       ▲                                                         │
│       │    ╭──╮                                                 │
│       │   ╱    ╲     Ratio > 1: More profit potential           │
│       │  ╱      ╲    Ratio < 1: More drawdown risk              │
│       │ ╱        ╲                                              │
│       └─────┬─────────────▶ MFE/MAE Ratio                       │
│             1.0                                                 │
│                                                                 │
│  Options: by_outcome, bins                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  heatmap_mae_mfe()                                              │
│  ─────────────────                                              │
│                                                                 │
│      MFE ▲                                                      │
│          │  ░░▒▒▓▓██                                            │
│          │  ░░▒▒▓▓██     Density heatmap showing                │
│          │  ░░▒▒▓▓██     trade concentration                    │
│          │  ░░▒▒▓▓██                                            │
│          │  ░░▒▒▓▓██                                            │
│          └────────────▶ MAE                                     │
│                                                                 │
│  Options: show_pnl_overlay, bins                                │
└─────────────────────────────────────────────────────────────────┘
```

#### Time-Based Charts

```
┌─────────────────────────────────────────────────────────────────┐
│  timeline_excursion()                                           │
│  ────────────────────                                           │
│                                                                 │
│     Value                                                       │
│       ▲                                                         │
│       │  ╭─╮   ╭───╮     ╭──╮                                   │
│       │ ╱   ╲ ╱     ╲   ╱    ╲     MAE/MFE/PnL over             │
│   ────┼──────X───────╲─X──────╲──▶ trade sequence               │
│       │       ╲       X        ╲                                │
│       │        ╲     ╱                                          │
│       │         ╰───╯                                           │
│                                                                 │
│  Options: show_mae, show_mfe, show_pnl                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  box_by_holding_period()                                        │
│  ───────────────────────                                        │
│                                                                 │
│     MAE/MFE                                                     │
│       ▲                                                         │
│       │   ┌─┐   ┌─┐   ┌─┐   ┌─┐                                 │
│       │   │ │   │ │   │ │   │ │   Box plots by                  │
│       │  ─┼─┼─ ─┼─┼─ ─┼─┼─ ─┼─┼─  holding period                │
│       │   │ │   │ │   │ │   │ │   buckets                       │
│       │   └─┘   └─┘   └─┘   └─┘                                 │
│       └────────────────────────────▶ Holding Bars               │
│           1-10  11-20 21-50  51+                                │
└─────────────────────────────────────────────────────────────────┘
```

#### Rolling Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│  rolling_statistics(window=50)                                  │
│  ─────────────────────────────                                  │
│                                                                 │
│     Rolling Mean                                                │
│       ▲      ╭────────────────────╮                             │
│       │   ╭─╱  Confidence band    ╲─────╮                       │
│       │  ╱╱                          ╲╲                         │
│       │ ╱╱ ─────────────────────────  ╲╲ Mean line              │
│       │ ╲╲                           ╱╱                         │
│       │  ╲╲─────────────────────────╱╱                          │
│       └─────────────────────────────────▶ Trade #               │
│                                                                 │
│  Tracks metric stability over trade sequence                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  rolling_distribution(window=50, step=25)                       │
│  ────────────────────────────────────────                       │
│                                                                 │
│     Density                                                     │
│       ▲   Window 1    Window 2    Window 3                      │
│       │    ╭─╮         ╭─╮          ╭─╮                         │
│       │   ╱   ╲       ╱   ╲        ╱   ╲                        │
│       │  ╱     ╲     ╱     ╲      ╱     ╲                       │
│       │ ╱       ╲───╱       ╲────╱       ╲                      │
│       └─────────────────────────────────────▶ Value             │
│                                                                 │
│  Shows how distribution evolves over time                       │
└─────────────────────────────────────────────────────────────────┘
```

### Statistics

```python
stats = analyzer.statistics()

# Key metrics
stats.n_trades       # Total trades
stats.win_rate       # Win rate (0-1)
stats.mae_mean       # Mean MAE
stats.mfe_mean       # Mean MFE
stats.correlation_mae_pnl   # MAE-PnL correlation
stats.correlation_mfe_pnl   # MFE-PnL correlation

# Suggested levels
stats.optimal_stop_loss_p75   # 75th percentile MAE
stats.optimal_take_profit_p75 # 75th percentile MFE

# Output formats
print(stats.summary())   # Text summary
stats.summary_df         # Polars DataFrame
stats._repr_html_()      # Jupyter HTML display
```

### Dashboard

```python
# Full dashboard with all charts
analyzer.dashboard().show()

# Custom chart selection
analyzer.dashboard(charts=[
    "scatter_mae_mfe",
    "distribution_mae",
    "ratio_mfe_mae"
]).show()
```

## Color Coding Options

```
┌─────────────────────────────────────────────────────────────────┐
│  color_by Options                                               │
├─────────────┬───────────────────────────────────────────────────┤
│ "direction" │ Long=Blue, Short=Purple                           │
│ "pnl"       │ Winner=Green, Loser=Red                           │
│ "holding"   │ Color gradient by holding period                  │
│ "strategy"  │ Different color per strategy                      │
│ "blueprint" │ Different color per blueprint                     │
└─────────────┴───────────────────────────────────────────────────┘
```

## Required DataFrame Columns

| Column | Required | Description |
|--------|----------|-------------|
| `direction` | Yes | Trade direction (1=Long, -1=Short) |
| `pnl` or `pnl_pct` | Yes | Profit/Loss value |
| `mae` or `mae_lv1` | One required | MAE metric(s) |
| `mfe` or `g_mfe` or `mhl` | One required | MFE metric(s) |
| `holding_bars` | Optional | For holding period analysis |
| `entry_price` | Optional | For percentage normalization |
| `*_volatility` | Optional | For volatility normalization |
| `strategy_name` | Optional | For strategy filtering/coloring |
| `blueprint_name` | Optional | For blueprint filtering/coloring |

## Usage Examples

### Basic Analysis

```python
from tradepose_client.analysis import MAEMFEAnalyzer

# Create analyzer from batch results
analyzer = MAEMFEAnalyzer(batch.all_trades())

# Quick visualization
analyzer.scatter_mae_mfe().show()

# Get statistics
stats = analyzer.statistics()
print(f"Win Rate: {stats.win_rate:.1%}")
print(f"Suggested Stop Loss (P75): {stats.optimal_stop_loss_p75:.4f}")
```

### Filtered Analysis

```python
# Analyze only long winning trades
long_winners = analyzer.filter(direction=1, profitable=True)

# Compare distributions
fig = long_winners.distribution_comparison()
fig.show()

# Statistics for filtered subset
stats = long_winners.statistics()
```

### Strategy Comparison

```python
# Compare MAE distributions across strategies
for strategy in ["momentum", "mean_reversion"]:
    filtered = analyzer.filter(strategy=strategy)
    print(f"{strategy}: MAE mean = {filtered.statistics().mae_mean:.4f}")
```

### Percentage-Based Analysis

```python
# Use percentage PnL for position-size-independent analysis
analyzer = MAEMFEAnalyzer(trades, pnl_column="pnl_pct")
analyzer.scatter_mae_mfe(normalize="pct").show()
```

## Error Handling

The module raises `ValueError` in these cases:

1. **Missing required columns**: Direction or PnL column not found
2. **No metric columns**: Neither MAE nor MFE columns present
3. **Empty filtered data**: Filter results in zero trades
4. **Invalid normalization**: Required columns for normalization missing

```python
# Empty data handling
try:
    analyzer.filter(direction=1, profitable=True).scatter_mae_mfe()
except ValueError as e:
    print(f"No trades match filter: {e}")
```
