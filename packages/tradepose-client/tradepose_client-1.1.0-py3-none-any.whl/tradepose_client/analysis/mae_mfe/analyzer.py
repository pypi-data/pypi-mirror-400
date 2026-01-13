"""MAE/MFE Analyzer - Core analysis class for MAE/MFE visualization."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Self

import polars as pl

from .config import DEFAULT_CONFIG, ChartConfig, DashboardConfig
from .types import (
    ALL_METRIC_COLUMNS,
    MAE_COLUMNS,
    METRIC_VOLATILITY_MAP,
    MFE_COLUMNS,
    REQUIRED_COLUMNS,
    ColorByOption,
    MetricType,
    NormalizeMode,
    PnLColumn,
)

if TYPE_CHECKING:
    import plotly.graph_objects as go

    from .statistics import MAEMFEStatistics


def _import_plotly() -> tuple:
    """Lazy import Plotly with helpful error message."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        return go, make_subplots
    except ImportError as e:
        raise ImportError(
            "Plotly is required for MAE/MFE analysis visualization. "
            "Install with: pip install 'tradepose-client[analysis]' "
            "or: pip install plotly>=6.3.1"
        ) from e


class MAEMFEAnalyzer:
    """MAE/MFE Analysis and Visualization Tool.

    Provides comprehensive analysis of Maximum Adverse Excursion (MAE) and
    Maximum Favorable Excursion (MFE) metrics with interactive visualizations.

    Attributes:
        trades: The trades DataFrame (with applied filters).
        n_trades: Number of trades in current filtered view.
        config: Chart configuration.

    Example:
        >>> from tradepose_client.analysis import MAEMFEAnalyzer
        >>>
        >>> # From BatchResults
        >>> analyzer = MAEMFEAnalyzer(batch.all_trades())
        >>>
        >>> # Chain-style analysis
        >>> analyzer.filter(direction=1).scatter_mae_mfe().show()
        >>>
        >>> # Statistics
        >>> stats = analyzer.statistics()
        >>> print(stats.summary())
        >>>
        >>> # Full dashboard
        >>> analyzer.dashboard().show()
    """

    def __init__(
        self,
        trades: pl.DataFrame,
        *,
        config: ChartConfig | None = None,
        pnl_column: PnLColumn = "pnl",
    ) -> None:
        """Initialize MAE/MFE Analyzer.

        Args:
            trades: Polars DataFrame with trades data (must include MAE/MFE columns).
            config: Optional chart configuration.
            pnl_column: PnL column to use for analysis ("pnl" or "pnl_pct").

        Raises:
            ValueError: If required columns are missing.
        """
        self._pnl_column = pnl_column
        self._validate_columns(trades, pnl_column)
        self._original_trades = trades
        self._trades = trades
        self._config = config or DEFAULT_CONFIG
        self._filters: dict = {}
        self._available_metrics = self._detect_available_metrics(trades)

    @staticmethod
    def _validate_columns(trades: pl.DataFrame, pnl_column: str) -> None:
        """Validate that required columns are present.

        Args:
            trades: DataFrame to validate.
            pnl_column: PnL column name to validate.

        Raises:
            ValueError: If required columns are missing.
        """
        columns = set(trades.columns)

        # Check required columns
        missing_required = REQUIRED_COLUMNS - columns
        if missing_required:
            raise ValueError(
                f"Missing required columns: {missing_required}. "
                f"Required columns are: {REQUIRED_COLUMNS}"
            )

        # Check PnL column exists
        if pnl_column not in columns:
            raise ValueError(
                f"PnL column '{pnl_column}' not found in DataFrame. "
                f"Available columns: {sorted(columns)}"
            )

        # Check that at least one MAE and one MFE column exists
        has_mae = bool(MAE_COLUMNS & columns)
        has_mfe = bool(MFE_COLUMNS & columns)

        if not has_mae and not has_mfe:
            raise ValueError(
                "DataFrame must contain at least one MAE column "
                f"({MAE_COLUMNS}) and one MFE column ({MFE_COLUMNS})"
            )

    @staticmethod
    def _detect_available_metrics(trades: pl.DataFrame) -> set[str]:
        """Detect which metric columns are available in the DataFrame."""
        return ALL_METRIC_COLUMNS & set(trades.columns)

    def _apply_filters(self) -> pl.DataFrame:
        """Apply all current filters to the original trades DataFrame."""
        df = self._original_trades

        if not self._filters:
            return df

        # Direction filter
        if "direction" in self._filters:
            df = df.filter(pl.col("direction") == self._filters["direction"])

        # Strategy filter
        if "strategy" in self._filters:
            strategies = self._filters["strategy"]
            if isinstance(strategies, str):
                strategies = [strategies]
            df = df.filter(pl.col("strategy_name").is_in(strategies))

        # Blueprint filter
        if "blueprint" in self._filters:
            blueprints = self._filters["blueprint"]
            if isinstance(blueprints, str):
                blueprints = [blueprints]
            df = df.filter(pl.col("blueprint_name").is_in(blueprints))

        # Profitable filter (uses configured pnl_column)
        if "profitable" in self._filters:
            if self._filters["profitable"]:
                df = df.filter(pl.col(self._pnl_column) > 0)
            else:
                df = df.filter(pl.col(self._pnl_column) <= 0)

        # Holding bars filter
        if "min_holding_bars" in self._filters:
            df = df.filter(pl.col("holding_bars") >= self._filters["min_holding_bars"])
        if "max_holding_bars" in self._filters:
            df = df.filter(pl.col("holding_bars") <= self._filters["max_holding_bars"])

        return df

    def _get_normalized_values(
        self,
        df: pl.DataFrame,
        metric: str,
        normalize: NormalizeMode,
    ) -> pl.Series:
        """Get metric values with specified normalization.

        Args:
            df: DataFrame containing the data.
            metric: Metric column name.
            normalize: Normalization mode.

        Returns:
            Series with normalized values.
        """
        values = df[metric]

        if normalize == "raw":
            return values

        if normalize == "pct":
            if "entry_price" not in df.columns:
                raise ValueError("Cannot use 'pct' normalization: 'entry_price' column not found")
            return values / df["entry_price"] * 100

        if normalize == "volatility":
            vol_col = METRIC_VOLATILITY_MAP.get(metric)
            if vol_col is None or vol_col not in df.columns:
                raise ValueError(
                    f"Cannot use 'volatility' normalization for '{metric}': "
                    f"volatility column '{vol_col}' not found"
                )
            return values / df[vol_col]

        raise ValueError(f"Unknown normalization mode: {normalize}")

    def _apply_layout(
        self,
        fig: "go.Figure",
        title: str,
        xaxis_title: str | None = None,
        yaxis_title: str | None = None,
    ) -> "go.Figure":
        """Apply standard layout to a figure.

        Args:
            fig: Plotly figure.
            title: Chart title.
            xaxis_title: X-axis title.
            yaxis_title: Y-axis title.

        Returns:
            Figure with updated layout.
        """
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=self._config.title_font_size),
            ),
            width=self._config.width,
            height=self._config.height,
            template=self._config.theme,
            showlegend=self._config.show_legend,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
        return fig

    # =========================================================================
    # Fluent Filter Methods (return Self for chaining)
    # =========================================================================

    def filter(
        self,
        *,
        direction: int | None = None,
        strategy: str | list[str] | None = None,
        blueprint: str | list[str] | None = None,
        profitable: bool | None = None,
        min_holding_bars: int | None = None,
        max_holding_bars: int | None = None,
    ) -> Self:
        """Apply filters to the analysis data.

        All filters are cumulative and return a new analyzer instance.

        Args:
            direction: Trade direction (1 for Long, -1 for Short).
            strategy: Strategy name(s) to include.
            blueprint: Blueprint name(s) to include.
            profitable: True for winners, False for losers.
            min_holding_bars: Minimum holding period in bars.
            max_holding_bars: Maximum holding period in bars.

        Returns:
            New MAEMFEAnalyzer instance with filtered data.

        Example:
            >>> analyzer.filter(direction=1, profitable=True).scatter_mae_mfe()
        """
        new_analyzer = MAEMFEAnalyzer(
            self._original_trades,
            config=self._config,
            pnl_column=self._pnl_column,
        )
        new_analyzer._filters = deepcopy(self._filters)

        if direction is not None:
            new_analyzer._filters["direction"] = direction
        if strategy is not None:
            new_analyzer._filters["strategy"] = strategy
        if blueprint is not None:
            new_analyzer._filters["blueprint"] = blueprint
        if profitable is not None:
            new_analyzer._filters["profitable"] = profitable
        if min_holding_bars is not None:
            new_analyzer._filters["min_holding_bars"] = min_holding_bars
        if max_holding_bars is not None:
            new_analyzer._filters["max_holding_bars"] = max_holding_bars

        new_analyzer._trades = new_analyzer._apply_filters()
        return new_analyzer

    def reset_filters(self) -> Self:
        """Reset all filters and return new analyzer with original data.

        Returns:
            New MAEMFEAnalyzer instance with no filters applied.
        """
        return MAEMFEAnalyzer(
            self._original_trades,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    # =========================================================================
    # Scatter Plot Charts
    # =========================================================================

    def scatter_mae_mfe(
        self,
        *,
        mae_metric: MetricType = "mae",
        mfe_metric: MetricType = "mfe",
        color_by: ColorByOption = "pnl",
        normalize: NormalizeMode = "raw",
        show_quadrants: bool = True,
        show_diagonal: bool = True,
    ) -> "go.Figure":
        """MAE vs MFE scatter plot.

        Core chart showing relationship between adverse and favorable excursions.

        Args:
            mae_metric: MAE metric column to use.
            mfe_metric: MFE metric column to use.
            color_by: Attribute to color points by.
            normalize: Normalization mode for values.
            show_quadrants: Show quadrant lines at zero.
            show_diagonal: Show MFE=MAE diagonal line.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_scatter_mae_mfe

        return create_scatter_mae_mfe(
            self.trades,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
            color_by=color_by,
            normalize=normalize,
            show_quadrants=show_quadrants,
            show_diagonal=show_diagonal,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    def scatter_pnl_mae(
        self,
        *,
        mae_metric: MetricType = "mae",
        color_by: ColorByOption = "direction",
        normalize: NormalizeMode = "raw",
        show_regression: bool = True,
    ) -> "go.Figure":
        """PnL (X-axis) vs MAE (Y-axis) scatter plot.

        Shows how MAE relates to final trade outcome.

        Args:
            mae_metric: MAE metric column to use.
            color_by: Attribute to color points by.
            normalize: Normalization mode for values.
            show_regression: Show regression line.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_scatter_pnl_metric

        return create_scatter_pnl_metric(
            self.trades,
            metric=mae_metric,
            metric_label="MAE",
            color_by=color_by,
            normalize=normalize,
            show_regression=show_regression,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    def scatter_pnl_mfe(
        self,
        *,
        mfe_metric: MetricType = "mfe",
        color_by: ColorByOption = "direction",
        normalize: NormalizeMode = "raw",
        show_regression: bool = True,
    ) -> "go.Figure":
        """PnL (X-axis) vs MFE (Y-axis) scatter plot.

        Shows how MFE relates to final trade outcome.

        Args:
            mfe_metric: MFE metric column to use.
            color_by: Attribute to color points by.
            normalize: Normalization mode for values.
            show_regression: Show regression line.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_scatter_pnl_metric

        return create_scatter_pnl_metric(
            self.trades,
            metric=mfe_metric,
            metric_label="MFE",
            color_by=color_by,
            normalize=normalize,
            show_regression=show_regression,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    # =========================================================================
    # Distribution Charts
    # =========================================================================

    def distribution_mae(
        self,
        *,
        mae_metric: MetricType = "mae",
        normalize: NormalizeMode = "raw",
        bins: int = 50,
        show_kde: bool = True,
        by_outcome: bool = False,
    ) -> "go.Figure":
        """MAE distribution histogram with optional KDE overlay.

        Args:
            mae_metric: MAE metric column to use.
            normalize: Normalization mode for values.
            bins: Number of histogram bins.
            show_kde: Show KDE overlay.
            by_outcome: Split distribution by win/loss outcome.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_distribution

        return create_distribution(
            self.trades,
            metric=mae_metric,
            metric_label="MAE",
            normalize=normalize,
            bins=bins,
            pnl_column=self._pnl_column,
            show_kde=show_kde,
            by_outcome=by_outcome,
            config=self._config,
        )

    def distribution_mfe(
        self,
        *,
        mfe_metric: MetricType = "mfe",
        normalize: NormalizeMode = "raw",
        bins: int = 50,
        show_kde: bool = True,
        by_outcome: bool = False,
    ) -> "go.Figure":
        """MFE distribution histogram with optional KDE overlay.

        Args:
            mfe_metric: MFE metric column to use.
            normalize: Normalization mode for values.
            bins: Number of histogram bins.
            show_kde: Show KDE overlay.
            by_outcome: Split distribution by win/loss outcome.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_distribution

        return create_distribution(
            self.trades,
            metric=mfe_metric,
            metric_label="MFE",
            normalize=normalize,
            bins=bins,
            pnl_column=self._pnl_column,
            show_kde=show_kde,
            by_outcome=by_outcome,
            config=self._config,
        )

    def distribution_comparison(
        self,
        *,
        metrics: list[MetricType | str] | None = None,
        normalize: NormalizeMode = "raw",
        bins: int = 50,
        show_kde: bool = True,
    ) -> "go.Figure":
        """Compare distributions of MAE, MFE, and PnL.

        Args:
            metrics: Metrics to compare (default: ["mae", "mfe", pnl_column]).
            normalize: Normalization mode for values.
            bins: Number of histogram bins.
            show_kde: Show KDE overlay.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_distribution_comparison

        if metrics is None:
            metrics = ["mae", "mfe", self._pnl_column]

        return create_distribution_comparison(
            self.trades,
            metrics=metrics,
            normalize=normalize,
            bins=bins,
            show_kde=show_kde,
            config=self._config,
        )

    # =========================================================================
    # Ratio and Relationship Charts
    # =========================================================================

    def ratio_mfe_mae(
        self,
        *,
        mae_metric: MetricType = "mae",
        mfe_metric: MetricType = "mfe",
        bins: int = 50,
        by_outcome: bool = True,
    ) -> "go.Figure":
        """MFE/MAE ratio distribution (reward-to-risk ratio).

        Shows the distribution of MFE/MAE ratios, grouped by trade outcome.

        Args:
            mae_metric: MAE metric column to use.
            mfe_metric: MFE metric column to use.
            bins: Number of histogram bins.
            by_outcome: Split by win/loss outcome.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_ratio_distribution

        return create_ratio_distribution(
            self.trades,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
            bins=bins,
            by_outcome=by_outcome,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    def heatmap_mae_mfe(
        self,
        *,
        mae_metric: MetricType = "mae",
        mfe_metric: MetricType = "mfe",
        normalize: NormalizeMode = "raw",
        bins: int = 20,
        show_pnl_overlay: bool = True,
    ) -> "go.Figure":
        """2D heatmap of MAE vs MFE with trade density or average PnL.

        Args:
            mae_metric: MAE metric column to use.
            mfe_metric: MFE metric column to use.
            normalize: Normalization mode for values.
            bins: Number of bins per axis.
            show_pnl_overlay: Show average PnL as color instead of density.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_heatmap_mae_mfe

        return create_heatmap_mae_mfe(
            self.trades,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
            normalize=normalize,
            bins=bins,
            show_pnl_overlay=show_pnl_overlay,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    # =========================================================================
    # Time-Based Charts
    # =========================================================================

    def timeline_excursion(
        self,
        *,
        mae_metric: MetricType = "mae",
        mfe_metric: MetricType = "mfe",
        normalize: NormalizeMode = "raw",
        show_mae: bool = True,
        show_mfe: bool = True,
        show_pnl: bool = True,
    ) -> "go.Figure":
        """Timeline showing MAE/MFE/PnL evolution over trade sequence.

        Args:
            mae_metric: MAE metric column to use.
            mfe_metric: MFE metric column to use.
            normalize: Normalization mode for values.
            show_mae: Show MAE line.
            show_mfe: Show MFE line.
            show_pnl: Show PnL line.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_timeline_excursion

        return create_timeline_excursion(
            self.trades,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
            normalize=normalize,
            show_mae=show_mae,
            show_mfe=show_mfe,
            show_pnl=show_pnl,
            config=self._config,
            pnl_column=self._pnl_column,
        )

    def box_by_holding_period(
        self,
        *,
        metric: MetricType | str = "mae",
        normalize: NormalizeMode = "raw",
        n_groups: int = 5,
    ) -> "go.Figure":
        """Box plot of metrics grouped by holding period bins.

        Args:
            metric: Metric to analyze.
            normalize: Normalization mode for values.
            n_groups: Number of holding period groups.

        Returns:
            Plotly Figure object.
        """
        from .charts import create_box_by_holding_period

        return create_box_by_holding_period(
            self.trades,
            metric=metric,
            normalize=normalize,
            n_groups=n_groups,
            config=self._config,
        )

    # =========================================================================
    # Rolling Window Analysis
    # =========================================================================

    def rolling_statistics(
        self,
        *,
        window: int = 50,
        metrics: list[MetricType | str] | None = None,
        normalize: NormalizeMode = "raw",
    ) -> "go.Figure":
        """Rolling window statistics over trade sequence.

        Args:
            window: Rolling window size in trades.
            metrics: Metrics to calculate (default: ["mae", "mfe"]).
            normalize: Normalization mode for values.

        Returns:
            Plotly Figure object.
        """
        from .rolling import create_rolling_statistics

        if metrics is None:
            metrics = ["mae", "mfe"]

        return create_rolling_statistics(
            self.trades,
            window=window,
            metrics=metrics,
            normalize=normalize,
            config=self._config,
        )

    def rolling_distribution(
        self,
        *,
        window: int = 50,
        step: int = 25,
        metric: MetricType | str = "mae",
        normalize: NormalizeMode = "raw",
    ) -> "go.Figure":
        """Rolling distribution comparison across different time windows.

        Args:
            window: Window size in trades.
            step: Step size between windows.
            metric: Metric to analyze.
            normalize: Normalization mode for values.

        Returns:
            Plotly Figure object.
        """
        from .rolling import create_rolling_distribution

        return create_rolling_distribution(
            self.trades,
            window=window,
            step=step,
            metric=metric,
            normalize=normalize,
            config=self._config,
        )

    # =========================================================================
    # Aggregation and Statistics
    # =========================================================================

    def statistics(
        self,
        *,
        mae_metric: MetricType = "mae",
        mfe_metric: MetricType = "mfe",
    ) -> "MAEMFEStatistics":
        """Calculate comprehensive MAE/MFE statistics.

        Args:
            mae_metric: MAE metric column to use.
            mfe_metric: MFE metric column to use.

        Returns:
            MAEMFEStatistics object with computed metrics.
        """
        from .statistics import calculate_statistics

        return calculate_statistics(
            self.trades,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
            pnl_column=self._pnl_column,
        )

    # =========================================================================
    # Dashboard and Export
    # =========================================================================

    def dashboard(
        self,
        *,
        charts: list[str] | None = None,
        config: DashboardConfig | None = None,
    ) -> "go.Figure":
        """Create comprehensive dashboard with multiple charts.

        Args:
            charts: List of chart names to include.
                Available: scatter_mae_mfe, scatter_pnl_mae, scatter_pnl_mfe,
                distribution_mae, distribution_mfe, distribution_comparison,
                ratio_mfe_mae, heatmap_mae_mfe, timeline_excursion.
            config: Dashboard layout configuration.

        Returns:
            Plotly Figure with subplots.
        """
        from .charts import create_dashboard

        if charts is None:
            charts = [
                "scatter_mae_mfe",
                "scatter_pnl_mae",
                "scatter_pnl_mfe",
                "distribution_mae",
                "distribution_mfe",
                "distribution_comparison",
                "ratio_mfe_mae",
                "heatmap_mae_mfe",
                "timeline_excursion",
            ]

        return create_dashboard(
            analyzer=self,
            charts=charts,
            config=config or DashboardConfig(),
            chart_config=self._config,
        )

    def to_html(
        self,
        path: str,
        *,
        include_dashboard: bool = True,
        include_statistics: bool = True,
    ) -> None:
        """Export full analysis report to HTML file.

        Args:
            path: Output file path.
            include_dashboard: Include dashboard visualization.
            include_statistics: Include statistics summary.
        """
        go, _ = _import_plotly()

        html_parts = []

        # Add title and styling
        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <title>MAE/MFE Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stats-table { border-collapse: collapse; margin: 20px 0; }
        .stats-table td, .stats-table th {
            border: 1px solid #ddd; padding: 8px; text-align: left;
        }
        .stats-table th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
<h1>MAE/MFE Analysis Report</h1>
""")

        # Add statistics
        if include_statistics:
            stats = self.statistics()
            html_parts.append("<h2>Statistics Summary</h2>")
            html_parts.append(stats._repr_html_())

        # Add dashboard
        if include_dashboard:
            html_parts.append("<h2>Visualization Dashboard</h2>")
            fig = self.dashboard()
            html_parts.append(fig.to_html(full_html=False, include_plotlyjs="cdn"))

        html_parts.append("</body></html>")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))

    def to_image(
        self,
        path: str,
        *,
        chart: str = "dashboard",
        format: str = "png",
        scale: float = 2.0,
    ) -> None:
        """Export chart to static image.

        Args:
            path: Output file path.
            chart: Chart type to export (default: dashboard).
            format: Image format (png, svg, pdf).
            scale: Image scale factor.

        Note:
            Requires kaleido package for image export.
        """
        chart_methods = {
            "dashboard": self.dashboard,
            "scatter_mae_mfe": self.scatter_mae_mfe,
            "scatter_pnl_mae": self.scatter_pnl_mae,
            "scatter_pnl_mfe": self.scatter_pnl_mfe,
            "distribution_mae": self.distribution_mae,
            "distribution_mfe": self.distribution_mfe,
            "distribution_comparison": self.distribution_comparison,
            "ratio_mfe_mae": self.ratio_mfe_mae,
            "heatmap_mae_mfe": self.heatmap_mae_mfe,
            "timeline_excursion": self.timeline_excursion,
        }

        if chart not in chart_methods:
            raise ValueError(
                f"Unknown chart type: {chart}. Available: {list(chart_methods.keys())}"
            )

        fig = chart_methods[chart]()
        fig.write_image(path, format=format, scale=scale)

    # =========================================================================
    # Jupyter Integration
    # =========================================================================

    def _repr_html_(self) -> str:
        """Jupyter HTML representation showing summary statistics."""
        stats = self.statistics()
        n_filters = len(self._filters)
        filter_info = f"<br><small>Filters applied: {n_filters}</small>" if n_filters > 0 else ""

        return f"""
        <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 8px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);">
            <h3 style="margin-top: 0; color: #2E7D32;">MAE/MFE Analyzer</h3>
            <p><strong>Trades:</strong> {self.n_trades:,}{filter_info}</p>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 5px;"><strong>Win Rate:</strong></td>
                    <td style="padding: 5px;">{stats.win_rate:.1%}</td>
                    <td style="padding: 5px;"><strong>MAE Mean:</strong></td>
                    <td style="padding: 5px;">{stats.mae_mean:.4f}</td>
                    <td style="padding: 5px;"><strong>MFE Mean:</strong></td>
                    <td style="padding: 5px;">{stats.mfe_mean:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Winners:</strong></td>
                    <td style="padding: 5px;">{stats.n_winners:,}</td>
                    <td style="padding: 5px;"><strong>MAE-PnL Corr:</strong></td>
                    <td style="padding: 5px;">{stats.correlation_mae_pnl:.3f}</td>
                    <td style="padding: 5px;"><strong>MFE-PnL Corr:</strong></td>
                    <td style="padding: 5px;">{stats.correlation_mfe_pnl:.3f}</td>
                </tr>
            </table>
            <p style="margin-bottom: 0; font-size: 0.9em; color: #666;">
                Use <code>.scatter_mae_mfe()</code>, <code>.statistics()</code>,
                or <code>.dashboard()</code> to explore further.
            </p>
        </div>
        """

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def trades(self) -> pl.DataFrame:
        """Current filtered trades DataFrame."""
        return self._trades

    @property
    def n_trades(self) -> int:
        """Number of trades in current filter."""
        return len(self._trades)

    @property
    def config(self) -> ChartConfig:
        """Current chart configuration."""
        return self._config

    @property
    def available_metrics(self) -> set[str]:
        """Set of available metric columns in the DataFrame."""
        return self._available_metrics
