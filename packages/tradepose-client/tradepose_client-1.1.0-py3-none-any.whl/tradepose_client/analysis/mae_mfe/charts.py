"""Chart generation functions for MAE/MFE analysis."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import polars as pl

from .config import DEFAULT_CONFIG, ChartConfig, DashboardConfig
from .types import (
    METRIC_VOLATILITY_MAP,
    ColorByOption,
    MetricType,
    NormalizeMode,
    PnLColumn,
)

if TYPE_CHECKING:
    import plotly.graph_objects as go

    from .analyzer import MAEMFEAnalyzer


def _validate_non_empty(df: pl.DataFrame, context: str) -> None:
    """Validate DataFrame is not empty.

    Args:
        df: DataFrame to validate.
        context: Description of the operation for error message.

    Raises:
        ValueError: If DataFrame is empty.
    """
    if len(df) == 0:
        raise ValueError(
            f"Cannot create {context}: no trades in filtered dataset. "
            "Check your filter criteria or use analyzer.n_trades to verify data exists."
        )


def _import_plotly():
    """Lazy import Plotly."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return go, make_subplots


def _get_color_values(
    df: pl.DataFrame,
    color_by: ColorByOption,
    config: ChartConfig,
    pnl_column: PnLColumn = "pnl",
) -> tuple[list, str | None, dict | None]:
    """Get color values and colorscale for scatter plots.

    Returns:
        Tuple of (color_values, colorscale_name, discrete_color_map).
    """
    if color_by == "pnl":
        # Discrete: winner/loser (uses configured pnl_column)
        colors = [
            config.color_winner if pnl > 0 else config.color_loser
            for pnl in df[pnl_column].to_list()
        ]
        return colors, None, None

    elif color_by == "direction":
        # Discrete: long/short
        dir_colors = config.get_direction_colors()
        colors = [dir_colors.get(d, config.color_neutral) for d in df["direction"].to_list()]
        return colors, None, None

    elif color_by == "holding_bars":
        # Continuous
        if "holding_bars" in df.columns:
            return df["holding_bars"].to_list(), "Viridis", None
        return [config.color_neutral] * len(df), None, None

    elif color_by == "strategy":
        # Discrete by strategy name
        if "strategy_name" in df.columns:
            strategies = df["strategy_name"].unique().to_list()
            colors_palette = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
            ]
            strategy_colors = {
                s: colors_palette[i % len(colors_palette)] for i, s in enumerate(strategies)
            }
            colors = [strategy_colors[s] for s in df["strategy_name"].to_list()]
            return colors, None, strategy_colors
        return [config.color_neutral] * len(df), None, None

    elif color_by == "blueprint":
        if "blueprint_name" in df.columns:
            blueprints = df["blueprint_name"].unique().to_list()
            colors_palette = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
            ]
            bp_colors = {
                b: colors_palette[i % len(colors_palette)] for i, b in enumerate(blueprints)
            }
            colors = [bp_colors[b] for b in df["blueprint_name"].to_list()]
            return colors, None, bp_colors
        return [config.color_neutral] * len(df), None, None

    return [config.color_neutral] * len(df), None, None


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
            # Avoid division by zero
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


# =============================================================================
# Scatter Charts
# =============================================================================


def create_scatter_mae_mfe(
    df: pl.DataFrame,
    *,
    mae_metric: MetricType = "mae",
    mfe_metric: MetricType = "mfe",
    color_by: ColorByOption = "pnl",
    normalize: NormalizeMode = "raw",
    show_quadrants: bool = True,
    show_diagonal: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
    pnl_column: PnLColumn = "pnl",
) -> "go.Figure":
    """Create MAE vs MFE scatter plot."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "MAE vs MFE scatter plot")

    mae_values = _normalize_values(df, mae_metric, normalize)
    mfe_values = _normalize_values(df, mfe_metric, normalize)
    colors, colorscale, _ = _get_color_values(df, color_by, config, pnl_column)

    # Build hover text
    pnl_label = "PnL%" if pnl_column == "pnl_pct" else "PnL"
    hover_texts = []
    for i in range(len(df)):
        text = (
            f"MAE: {mae_values[i]:.4f}<br>"
            f"MFE: {mfe_values[i]:.4f}<br>"
            f"{pnl_label}: {df[pnl_column][i]:.4f}"
        )
        if "holding_bars" in df.columns:
            text += f"<br>Holding: {df['holding_bars'][i]} bars"
        if "direction" in df.columns:
            direction = "Long" if df["direction"][i] == 1 else "Short"
            text += f"<br>Direction: {direction}"
        hover_texts.append(text)

    fig = go.Figure()

    # Main scatter
    marker_dict = dict(
        size=config.marker_size,
        opacity=config.marker_opacity,
    )
    if colorscale:
        marker_dict["color"] = colors
        marker_dict["colorscale"] = colorscale
        marker_dict["showscale"] = True
        marker_dict["colorbar"] = dict(title=color_by.replace("_", " ").title())
    else:
        marker_dict["color"] = colors

    fig.add_trace(
        go.Scatter(
            x=mae_values,
            y=mfe_values,
            mode="markers",
            marker=marker_dict,
            hovertext=hover_texts,
            hoverinfo="text",
            name="Trades",
        )
    )

    # Quadrant lines
    if show_quadrants:
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Diagonal line (MFE = MAE)
    if show_diagonal:
        max_val = max(np.nanmax(mae_values), np.nanmax(mfe_values))
        min_val = min(np.nanmin(mae_values), np.nanmin(mfe_values))
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode="lines",
                line=dict(dash="dot", color="blue", width=1),
                name="MFE = MAE",
                hoverinfo="skip",
            )
        )

    mae_label = _get_axis_label(mae_metric, normalize)
    mfe_label = _get_axis_label(mfe_metric, normalize)

    fig.update_layout(
        title=f"{mae_metric.upper()} vs {mfe_metric.upper()} Analysis",
        xaxis_title=mae_label,
        yaxis_title=mfe_label,
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_scatter_pnl_metric(
    df: pl.DataFrame,
    *,
    metric: MetricType,
    metric_label: str,
    color_by: ColorByOption = "direction",
    normalize: NormalizeMode = "raw",
    show_regression: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
    pnl_column: PnLColumn = "pnl",
) -> "go.Figure":
    """Create PnL vs Metric scatter plot (PnL on X-axis)."""
    go, _ = _import_plotly()

    _validate_non_empty(df, f"PnL vs {metric_label} scatter plot")

    pnl_values = df[pnl_column].to_numpy()
    metric_values = _normalize_values(df, metric, normalize)
    colors, colorscale, _ = _get_color_values(df, color_by, config, pnl_column)

    pnl_label = "PnL%" if pnl_column == "pnl_pct" else "PnL"

    fig = go.Figure()

    # Main scatter
    marker_dict = dict(
        size=config.marker_size,
        opacity=config.marker_opacity,
    )
    if colorscale:
        marker_dict["color"] = colors
        marker_dict["colorscale"] = colorscale
        marker_dict["showscale"] = True
    else:
        marker_dict["color"] = colors

    fig.add_trace(
        go.Scatter(
            x=pnl_values,
            y=metric_values,
            mode="markers",
            marker=marker_dict,
            name="Trades",
            hovertemplate=(f"{pnl_label}: %{{x:.4f}}<br>{metric_label}: %{{y:.4f}}<extra></extra>"),
        )
    )

    # Zero lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Regression line
    if show_regression and len(df) > 2:
        # Simple linear regression
        valid_mask = ~(np.isnan(pnl_values) | np.isnan(metric_values))
        if np.sum(valid_mask) > 2:
            x_valid = pnl_values[valid_mask]
            y_valid = metric_values[valid_mask]
            coeffs = np.polyfit(x_valid, y_valid, 1)
            x_line = np.array([x_valid.min(), x_valid.max()])
            y_line = np.polyval(coeffs, x_line)
            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    line=dict(dash="dash", color="red", width=2),
                    name=f"Regression (slope={coeffs[0]:.3f})",
                    hoverinfo="skip",
                )
            )

    y_label = _get_axis_label(metric, normalize)

    fig.update_layout(
        title=f"{pnl_label} vs {metric_label} Analysis",
        xaxis_title=pnl_label,
        yaxis_title=y_label,
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


# =============================================================================
# Distribution Charts
# =============================================================================


def create_distribution(
    df: pl.DataFrame,
    *,
    metric: MetricType,
    metric_label: str,
    normalize: NormalizeMode = "raw",
    bins: int = 50,
    pnl_column: PnLColumn = "pnl",
    show_kde: bool = True,
    by_outcome: bool = False,
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create distribution histogram for a metric."""
    go, _ = _import_plotly()

    _validate_non_empty(df, f"{metric_label} distribution")

    fig = go.Figure()

    if by_outcome:
        # Split by winner/loser (uses configured pnl_column)
        winners = df.filter(pl.col(pnl_column) > 0)
        losers = df.filter(pl.col(pnl_column) <= 0)

        if len(winners) > 0:
            win_values = _normalize_values(winners, metric, normalize)
            fig.add_trace(
                go.Histogram(
                    x=win_values,
                    nbinsx=bins,
                    name="Winners",
                    marker_color=config.color_winner,
                    opacity=0.6,
                    histnorm="probability density" if show_kde else None,
                )
            )

        if len(losers) > 0:
            lose_values = _normalize_values(losers, metric, normalize)
            fig.add_trace(
                go.Histogram(
                    x=lose_values,
                    nbinsx=bins,
                    name="Losers",
                    marker_color=config.color_loser,
                    opacity=0.6,
                    histnorm="probability density" if show_kde else None,
                )
            )

        fig.update_layout(barmode="overlay")
    else:
        # Single distribution
        values = _normalize_values(df, metric, normalize)
        fig.add_trace(
            go.Histogram(
                x=values,
                nbinsx=bins,
                name=metric_label,
                marker_color=config.color_neutral,
                opacity=0.7,
                histnorm="probability density" if show_kde else None,
            )
        )

        # KDE overlay
        if show_kde and len(values) > 10:
            try:
                from scipy import stats as scipy_stats

                kde = scipy_stats.gaussian_kde(values[~np.isnan(values)])
                x_range = np.linspace(np.nanmin(values), np.nanmax(values), 200)
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=kde(x_range),
                        mode="lines",
                        name="KDE",
                        line=dict(color="#1976D2", width=2),
                    )
                )
            except (ImportError, np.linalg.LinAlgError):
                pass  # Skip KDE if scipy not available or singular matrix

    x_label = _get_axis_label(metric, normalize)

    fig.update_layout(
        title=f"{metric_label} Distribution",
        xaxis_title=x_label,
        yaxis_title="Density" if show_kde else "Count",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_distribution_comparison(
    df: pl.DataFrame,
    *,
    metrics: list[str],
    normalize: NormalizeMode = "raw",
    bins: int = 50,
    show_kde: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create overlaid distribution comparison for multiple metrics."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "distribution comparison")

    fig = go.Figure()

    colors = {
        "mae": "#F44336",  # Red
        "mfe": "#4CAF50",  # Green
        "pnl": "#2196F3",  # Blue
        "pnl_pct": "#2196F3",  # Blue (same as pnl)
        "g_mfe": "#8BC34A",  # Light green
        "mae_lv1": "#FF9800",  # Orange
        "mhl": "#9C27B0",  # Purple
    }

    for metric in metrics:
        if metric not in df.columns:
            continue

        if normalize == "raw":
            # For comparison, normalize to z-scores
            values = df[metric].to_numpy()
            mean_val = np.nanmean(values)
            std_val = np.nanstd(values)
            if std_val > 0:
                values = (values - mean_val) / std_val
        else:
            values = _normalize_values(df, metric, normalize)

        color = colors.get(metric, config.color_neutral)

        fig.add_trace(
            go.Histogram(
                x=values,
                nbinsx=bins,
                name=metric.upper(),
                marker_color=color,
                opacity=0.5,
                histnorm="probability density",
            )
        )

        # KDE overlay
        if show_kde and len(values) > 10:
            try:
                from scipy import stats as scipy_stats

                valid_values = values[~np.isnan(values)]
                if len(valid_values) > 2:
                    kde = scipy_stats.gaussian_kde(valid_values)
                    x_range = np.linspace(valid_values.min(), valid_values.max(), 200)
                    fig.add_trace(
                        go.Scatter(
                            x=x_range,
                            y=kde(x_range),
                            mode="lines",
                            name=f"{metric.upper()} KDE",
                            line=dict(color=color, width=2),
                        )
                    )
            except (ImportError, np.linalg.LinAlgError):
                pass

    fig.update_layout(
        barmode="overlay",
        title="Distribution Comparison (Z-Score Normalized)",
        xaxis_title="Normalized Value",
        yaxis_title="Density",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


# =============================================================================
# Ratio and Relationship Charts
# =============================================================================


def create_ratio_distribution(
    df: pl.DataFrame,
    *,
    mae_metric: MetricType = "mae",
    mfe_metric: MetricType = "mfe",
    bins: int = 50,
    by_outcome: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
    pnl_column: PnLColumn = "pnl",
) -> "go.Figure":
    """Create MFE/MAE ratio distribution."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "ratio distribution")

    # Calculate ratio (avoid division by zero)
    mae_values = df[mae_metric].to_numpy()
    mfe_values = df[mfe_metric].to_numpy()

    # Avoid division by zero - use small epsilon
    mae_safe = np.where(mae_values == 0, 0.0001, mae_values)
    ratios = mfe_values / mae_safe

    # Clip extreme ratios for visualization
    ratios = np.clip(ratios, -10, 10)

    fig = go.Figure()

    if by_outcome:
        pnl_values = df[pnl_column].to_numpy()
        winner_mask = pnl_values > 0

        fig.add_trace(
            go.Histogram(
                x=ratios[winner_mask],
                nbinsx=bins,
                name="Winners",
                marker_color=config.color_winner,
                opacity=0.6,
                histnorm="probability density",
            )
        )

        fig.add_trace(
            go.Histogram(
                x=ratios[~winner_mask],
                nbinsx=bins,
                name="Losers",
                marker_color=config.color_loser,
                opacity=0.6,
                histnorm="probability density",
            )
        )

        fig.update_layout(barmode="overlay")
    else:
        fig.add_trace(
            go.Histogram(
                x=ratios,
                nbinsx=bins,
                name="Ratio",
                marker_color=config.color_neutral,
                opacity=0.7,
            )
        )

    # Add vertical line at ratio = 1
    fig.add_vline(x=1, line_dash="dash", line_color="blue", opacity=0.7)

    fig.update_layout(
        title=f"{mfe_metric.upper()}/{mae_metric.upper()} Ratio Distribution",
        xaxis_title=f"{mfe_metric.upper()}/{mae_metric.upper()} Ratio",
        yaxis_title="Density",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_heatmap_mae_mfe(
    df: pl.DataFrame,
    *,
    mae_metric: MetricType = "mae",
    mfe_metric: MetricType = "mfe",
    normalize: NormalizeMode = "raw",
    bins: int = 20,
    show_pnl_overlay: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
    pnl_column: PnLColumn = "pnl",
) -> "go.Figure":
    """Create 2D heatmap of MAE vs MFE."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "MAE vs MFE heatmap")

    mae_values = _normalize_values(df, mae_metric, normalize)
    mfe_values = _normalize_values(df, mfe_metric, normalize)
    pnl_values = df[pnl_column].to_numpy()

    # Create 2D histogram
    mae_edges = np.linspace(np.nanmin(mae_values), np.nanmax(mae_values), bins + 1)
    mfe_edges = np.linspace(np.nanmin(mfe_values), np.nanmax(mfe_values), bins + 1)

    if show_pnl_overlay:
        # Calculate average PnL per bin
        z_values = np.zeros((bins, bins))
        counts = np.zeros((bins, bins))

        mae_idx = np.digitize(mae_values, mae_edges) - 1
        mfe_idx = np.digitize(mfe_values, mfe_edges) - 1

        # Clip indices
        mae_idx = np.clip(mae_idx, 0, bins - 1)
        mfe_idx = np.clip(mfe_idx, 0, bins - 1)

        for i in range(len(df)):
            if not np.isnan(pnl_values[i]):
                z_values[mfe_idx[i], mae_idx[i]] += pnl_values[i]
                counts[mfe_idx[i], mae_idx[i]] += 1

        # Average PnL
        with np.errstate(invalid="ignore"):
            z_values = np.where(counts > 0, z_values / counts, np.nan)

        colorscale = "RdYlGn"
        colorbar_title = "Avg PnL%" if pnl_column == "pnl_pct" else "Avg PnL"
    else:
        # Density heatmap
        z_values, _, _ = np.histogram2d(mae_values, mfe_values, bins=[mae_edges, mfe_edges])
        z_values = z_values.T
        colorscale = "Viridis"
        colorbar_title = "Count"

    mae_centers = (mae_edges[:-1] + mae_edges[1:]) / 2
    mfe_centers = (mfe_edges[:-1] + mfe_edges[1:]) / 2

    fig = go.Figure(
        go.Heatmap(
            x=mae_centers,
            y=mfe_centers,
            z=z_values,
            colorscale=colorscale,
            colorbar=dict(title=colorbar_title),
            hovertemplate=(
                f"{mae_metric.upper()}: %{{x:.3f}}<br>"
                f"{mfe_metric.upper()}: %{{y:.3f}}<br>"
                f"{colorbar_title}: %{{z:.3f}}<extra></extra>"
            ),
        )
    )

    mae_label = _get_axis_label(mae_metric, normalize)
    mfe_label = _get_axis_label(mfe_metric, normalize)

    fig.update_layout(
        title=f"{mae_metric.upper()} vs {mfe_metric.upper()} Heatmap",
        xaxis_title=mae_label,
        yaxis_title=mfe_label,
        width=config.width,
        height=config.height,
        template=config.theme,
    )

    return fig


# =============================================================================
# Time-Based Charts
# =============================================================================


def create_timeline_excursion(
    df: pl.DataFrame,
    *,
    mae_metric: MetricType = "mae",
    mfe_metric: MetricType = "mfe",
    normalize: NormalizeMode = "raw",
    show_mae: bool = True,
    show_mfe: bool = True,
    show_pnl: bool = True,
    config: ChartConfig = DEFAULT_CONFIG,
    pnl_column: PnLColumn = "pnl",
) -> "go.Figure":
    """Create timeline of MAE/MFE/PnL evolution."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "excursion timeline")

    fig = go.Figure()
    x = list(range(len(df)))

    if show_mae:
        mae_values = _normalize_values(df, mae_metric, normalize)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=mae_values,
                mode="lines",
                name=mae_metric.upper(),
                line=dict(color="#F44336", width=config.line_width),
            )
        )

    if show_mfe:
        mfe_values = _normalize_values(df, mfe_metric, normalize)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=mfe_values,
                mode="lines",
                name=mfe_metric.upper(),
                line=dict(color="#4CAF50", width=config.line_width),
            )
        )

    if show_pnl:
        pnl_values = df[pnl_column].to_numpy()
        pnl_label = "PnL%" if pnl_column == "pnl_pct" else "PnL"
        fig.add_trace(
            go.Scatter(
                x=x,
                y=pnl_values,
                mode="lines",
                name=pnl_label,
                line=dict(color="#2196F3", width=config.line_width),
            )
        )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Excursion Timeline",
        xaxis_title="Trade #",
        yaxis_title="Value",
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=config.show_legend,
    )

    return fig


def create_box_by_holding_period(
    df: pl.DataFrame,
    *,
    metric: str = "mae",
    normalize: NormalizeMode = "raw",
    n_groups: int = 5,
    config: ChartConfig = DEFAULT_CONFIG,
) -> "go.Figure":
    """Create box plot grouped by holding period."""
    go, _ = _import_plotly()

    _validate_non_empty(df, "holding period box plot")

    if "holding_bars" not in df.columns:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="holding_bars column not available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Create holding period groups
    holding_bars = df["holding_bars"].to_numpy()
    metric_values = _normalize_values(df, metric, normalize)

    # Calculate quantile edges for groups
    edges = np.percentile(holding_bars, np.linspace(0, 100, n_groups + 1))
    edges = np.unique(edges)  # Remove duplicates

    fig = go.Figure()

    for i in range(len(edges) - 1):
        mask = (holding_bars >= edges[i]) & (holding_bars < edges[i + 1])
        if i == len(edges) - 2:  # Last group includes upper bound
            mask = (holding_bars >= edges[i]) & (holding_bars <= edges[i + 1])

        if np.sum(mask) > 0:
            group_values = metric_values[mask]
            label = f"{int(edges[i])}-{int(edges[i + 1])} bars"

            fig.add_trace(
                go.Box(
                    y=group_values,
                    name=label,
                    boxpoints="outliers",
                )
            )

    y_label = _get_axis_label(metric, normalize)

    fig.update_layout(
        title=f"{metric.upper()} by Holding Period",
        xaxis_title="Holding Period",
        yaxis_title=y_label,
        width=config.width,
        height=config.height,
        template=config.theme,
        showlegend=False,
    )

    return fig


# =============================================================================
# Dashboard
# =============================================================================


def create_dashboard(
    analyzer: "MAEMFEAnalyzer",
    charts: list[str],
    config: DashboardConfig,
    chart_config: ChartConfig,
) -> "go.Figure":
    """Create dashboard with multiple charts."""
    go, make_subplots = _import_plotly()

    n_charts = len(charts)
    rows = config.rows
    cols = config.cols

    # Adjust grid if needed
    while rows * cols < n_charts:
        if cols <= rows:
            cols += 1
        else:
            rows += 1

    # Create subplot titles
    titles = [c.replace("_", " ").title() for c in charts]

    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=titles[:n_charts],
        horizontal_spacing=config.horizontal_spacing,
        vertical_spacing=config.vertical_spacing,
    )

    # Chart method mapping
    chart_methods = {
        "scatter_mae_mfe": analyzer.scatter_mae_mfe,
        "scatter_pnl_mae": analyzer.scatter_pnl_mae,
        "scatter_pnl_mfe": analyzer.scatter_pnl_mfe,
        "distribution_mae": analyzer.distribution_mae,
        "distribution_mfe": analyzer.distribution_mfe,
        "distribution_comparison": analyzer.distribution_comparison,
        "ratio_mfe_mae": analyzer.ratio_mfe_mae,
        "heatmap_mae_mfe": analyzer.heatmap_mae_mfe,
        "timeline_excursion": analyzer.timeline_excursion,
    }

    for idx, chart_name in enumerate(charts):
        if chart_name not in chart_methods:
            continue

        row = idx // cols + 1
        col = idx % cols + 1

        try:
            # Get individual chart
            chart_fig = chart_methods[chart_name]()

            # Add traces to subplot
            for trace in chart_fig.data:
                trace.showlegend = False
                fig.add_trace(trace, row=row, col=col)
        except ValueError as e:
            # Add error annotation to this subplot
            fig.add_annotation(
                text=str(e),
                xref="paper",
                yref="paper",
                x=(col - 0.5) / cols,
                y=1 - (row - 0.5) / rows,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(size=10, color="red"),
            )

    fig.update_layout(
        height=config.height_per_row * rows,
        width=chart_config.width,
        title_text="MAE/MFE Analysis Dashboard",
        showlegend=False,
        template=chart_config.theme,
    )

    return fig
