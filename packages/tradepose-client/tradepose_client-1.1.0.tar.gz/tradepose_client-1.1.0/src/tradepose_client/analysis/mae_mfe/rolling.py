"""Rolling window analysis functions for MAE/MFE metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import polars as pl

from .config import DEFAULT_CONFIG, ChartConfig
from .types import METRIC_VOLATILITY_MAP, NormalizeMode, PnLColumn

if TYPE_CHECKING:
    import plotly.graph_objects as go


def _import_plotly():
    """Lazy import Plotly."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return go, make_subplots


def _normalize_values(
    df: pl.DataFrame,
    column: str,
    normalize: NormalizeMode,
) -> np.ndarray:
    """Normalize values according to mode."""
    values = df[column].to_numpy()

    if normalize == "raw":
        return values

    if normalize == "pct":
        if "entry_price" in df.columns:
            entry_prices = df["entry_price"].to_numpy()
            return values / entry_prices * 100
        return values

    if normalize == "volatility":
        vol_col = METRIC_VOLATILITY_MAP.get(column)
        if vol_col and vol_col in df.columns:
            vol_values = df[vol_col].to_numpy()
            vol_values = np.where(vol_values == 0, 1, vol_values)
            return values / vol_values
        return values

    return values


def _get_axis_label(metric: str, normalize: NormalizeMode) -> str:
    """Get axis label with normalization suffix."""
    label = metric.upper()
    if normalize == "pct":
        label += " (%)"
    elif normalize == "volatility":
        label += " (ATR)"
    return label


def create_rolling_statistics(
    df: pl.DataFrame,
    *,
    window: int = 50,
    metrics: list[str],
    normalize: NormalizeMode = "raw",
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create rolling window statistics visualization.

    Calculates rolling mean, std, and percentiles for specified metrics.

    Args:
        df: Trades DataFrame.
        window: Rolling window size in trades.
        metrics: List of metrics to analyze.
        normalize: Normalization mode.
        config: Chart configuration.

    Returns:
        Plotly Figure with rolling statistics.
    """
    go, make_subplots = _import_plotly()

    n_metrics = len(metrics)

    fig = make_subplots(
        rows=n_metrics,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[f"Rolling {m.upper()} (window={window})" for m in metrics],
        vertical_spacing=0.08,
    )

    colors = {
        "mae": "#F44336",
        "mfe": "#4CAF50",
        "pnl": "#2196F3",
        "g_mfe": "#8BC34A",
        "mae_lv1": "#FF9800",
        "mhl": "#9C27B0",
    }

    x = list(range(len(df)))

    for idx, metric in enumerate(metrics, 1):
        if metric not in df.columns:
            continue

        values = _normalize_values(df, metric, normalize)
        color = colors.get(metric, config.color_neutral)

        # Calculate rolling statistics using numpy
        n = len(values)
        rolling_mean = np.full(n, np.nan)
        rolling_p25 = np.full(n, np.nan)
        rolling_p75 = np.full(n, np.nan)

        for i in range(window - 1, n):
            window_data = values[i - window + 1 : i + 1]
            valid_data = window_data[~np.isnan(window_data)]
            if len(valid_data) > 0:
                rolling_mean[i] = np.mean(valid_data)
                rolling_p25[i] = np.percentile(valid_data, 25)
                rolling_p75[i] = np.percentile(valid_data, 75)

        # Add confidence band (25-75 percentile)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=rolling_p75,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=idx,
            col=1,
        )

        # Convert hex to rgba for fill color
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=rolling_p25,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor=f"rgba({r},{g},{b},0.2)",
                showlegend=False,
                hoverinfo="skip",
            ),
            row=idx,
            col=1,
        )

        # Add mean line
        fig.add_trace(
            go.Scatter(
                x=x,
                y=rolling_mean,
                mode="lines",
                name=f"{metric.upper()} Mean",
                line=dict(color=color, width=config.line_width),
                hovertemplate=f"{metric.upper()}: %{{y:.4f}}<extra></extra>",
            ),
            row=idx,
            col=1,
        )

        # Update y-axis label
        y_label = _get_axis_label(metric, normalize)
        fig.update_yaxes(title_text=y_label, row=idx, col=1)

    fig.update_xaxes(title_text="Trade #", row=n_metrics, col=1)

    fig.update_layout(
        height=250 * n_metrics,
        width=config.width,
        title_text=f"Rolling Statistics (window={window})",
        showlegend=config.show_legend,
        template=config.theme,
    )

    return fig


def create_rolling_distribution(
    df: pl.DataFrame,
    *,
    window: int = 50,
    step: int = 25,
    metric: str = "mae",
    normalize: NormalizeMode = "raw",
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create rolling distribution visualization.

    Shows how the distribution of a metric changes over time using
    overlaid density curves from rolling windows.

    Args:
        df: Trades DataFrame.
        window: Window size in trades.
        step: Step size between windows.
        metric: Metric to analyze.
        normalize: Normalization mode.
        config: Chart configuration.

    Returns:
        Plotly Figure with rolling distributions.
    """
    go, _ = _import_plotly()

    if metric not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Metric '{metric}' not found in DataFrame",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    values = _normalize_values(df, metric, normalize)
    n_trades = len(values)

    if n_trades < window:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Not enough trades ({n_trades}) for window size ({window})",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()

    # Generate color scale
    try:
        import plotly.express as px

        colors = px.colors.sequential.Viridis
    except ImportError:
        # Fallback colors
        colors = [
            "#440154",
            "#482878",
            "#3e4989",
            "#31688e",
            "#26828e",
            "#1f9e89",
            "#35b779",
            "#6ece58",
            "#b5de2b",
            "#fde725",
        ]

    # Calculate number of windows
    starts = list(range(0, n_trades - window + 1, step))
    n_windows = len(starts)

    for i, start in enumerate(starts):
        end = start + window
        window_data = values[start:end]
        valid_data = window_data[~np.isnan(window_data)]

        if len(valid_data) < 3:
            continue

        # Calculate KDE
        try:
            from scipy import stats as scipy_stats

            kde = scipy_stats.gaussian_kde(valid_data)
            x_range = np.linspace(valid_data.min(), valid_data.max(), 100)
            y_values = kde(x_range)

            color_idx = int(i / max(n_windows - 1, 1) * (len(colors) - 1))
            color = colors[color_idx]

            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=y_values,
                    mode="lines",
                    name=f"Trades {start + 1}-{end}",
                    line=dict(color=color, width=1.5),
                    opacity=0.7,
                    hovertemplate=(
                        f"Window: {start + 1}-{end}<br>"
                        f"{metric.upper()}: %{{x:.4f}}<br>"
                        f"Density: %{{y:.4f}}<extra></extra>"
                    ),
                )
            )
        except (ImportError, np.linalg.LinAlgError):
            # Fallback to histogram if scipy not available
            fig.add_trace(
                go.Histogram(
                    x=valid_data,
                    name=f"Trades {start + 1}-{end}",
                    opacity=0.3,
                    histnorm="probability density",
                )
            )

    x_label = _get_axis_label(metric, normalize)

    fig.update_layout(
        title=f"Rolling {metric.upper()} Distribution (window={window}, step={step})",
        xaxis_title=x_label,
        yaxis_title="Density",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_rolling_win_rate(
    df: pl.DataFrame,
    *,
    window: int = 50,
    pnl_column: PnLColumn = "pnl",
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create rolling win rate visualization.

    Args:
        df: Trades DataFrame with 'pnl' column.
        window: Rolling window size.
        pnl_column: PnL column to use ('pnl' or 'pnl_pct').
        config: Chart configuration.

    Returns:
        Plotly Figure with rolling win rate.
    """
    go, _ = _import_plotly()

    pnl_values = df[pnl_column].to_numpy()
    n = len(pnl_values)

    rolling_win_rate = np.full(n, np.nan)

    for i in range(window - 1, n):
        window_pnl = pnl_values[i - window + 1 : i + 1]
        valid_pnl = window_pnl[~np.isnan(window_pnl)]
        if len(valid_pnl) > 0:
            rolling_win_rate[i] = np.sum(valid_pnl > 0) / len(valid_pnl)

    x = list(range(n))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=rolling_win_rate,
            mode="lines",
            name="Win Rate",
            line=dict(color="#4CAF50", width=config.line_width),
            hovertemplate="Trade #%{x}<br>Win Rate: %{y:.1%}<extra></extra>",
        )
    )

    # Add 50% reference line
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=f"Rolling Win Rate (window={window})",
        xaxis_title="Trade #",
        yaxis_title="Win Rate",
        yaxis=dict(tickformat=".0%", range=[0, 1]),
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_rolling_pnl_cumulative(
    df: pl.DataFrame,
    *,
    window: int | None = None,
    pnl_column: PnLColumn = "pnl",
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create cumulative PnL with optional rolling average overlay.

    Args:
        df: Trades DataFrame with 'pnl' column.
        window: Optional rolling window for smoothed line.
        pnl_column: PnL column to use ('pnl' or 'pnl_pct').
        config: Chart configuration.

    Returns:
        Plotly Figure with cumulative PnL.
    """
    go, _ = _import_plotly()

    pnl_values = df[pnl_column].to_numpy()
    cumulative_pnl = np.nancumsum(pnl_values)
    x = list(range(len(pnl_values)))

    fig = go.Figure()

    # Cumulative PnL
    fig.add_trace(
        go.Scatter(
            x=x,
            y=cumulative_pnl,
            mode="lines",
            name="Cumulative PnL",
            line=dict(color="#2196F3", width=config.line_width),
            hovertemplate="Trade #%{x}<br>Cumulative PnL: %{y:.4f}<extra></extra>",
        )
    )

    # Rolling average overlay
    if window and len(pnl_values) >= window:
        rolling_mean = np.full(len(pnl_values), np.nan)
        for i in range(window - 1, len(pnl_values)):
            window_data = pnl_values[i - window + 1 : i + 1]
            rolling_mean[i] = np.nanmean(window_data)

        # Scale rolling mean to cumulative PnL range for overlay
        rolling_cumulative = np.nancumsum(rolling_mean)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=rolling_cumulative,
                mode="lines",
                name=f"Rolling Mean (w={window})",
                line=dict(color="#FF9800", width=config.line_width, dash="dot"),
                hovertemplate="Trade #%{x}<br>Rolling Cum: %{y:.4f}<extra></extra>",
            )
        )

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Cumulative PnL",
        xaxis_title="Trade #",
        yaxis_title="Cumulative PnL",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig
