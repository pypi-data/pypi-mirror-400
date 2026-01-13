"""Tests for chart generation functions."""

from __future__ import annotations

import polars as pl
import pytest
from tradepose_client.analysis.mae_mfe import MAEMFEAnalyzer

# Skip all tests in this module if plotly is not installed
plotly = pytest.importorskip("plotly")


class TestScatterCharts:
    """Test scatter plot chart methods."""

    def test_scatter_mae_mfe_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_mae_mfe returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.scatter_mae_mfe()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_scatter_mae_mfe_with_options(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_mae_mfe with various options."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)

        # Test different color_by options
        for color_by in ["pnl", "direction", "holding_bars", "strategy"]:
            fig = analyzer.scatter_mae_mfe(color_by=color_by)
            assert len(fig.data) > 0

        # Test normalize options
        for normalize in ["raw", "pct", "volatility"]:
            fig = analyzer.scatter_mae_mfe(normalize=normalize)
            assert len(fig.data) > 0

        # Test with/without quadrants and diagonal
        fig = analyzer.scatter_mae_mfe(show_quadrants=False, show_diagonal=False)
        assert len(fig.data) > 0

    def test_scatter_mae_mfe_custom_metrics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_mae_mfe with custom metric columns."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.scatter_mae_mfe(mae_metric="mae_lv1", mfe_metric="g_mfe")

        assert len(fig.data) > 0
        assert "mae_lv1" in fig.layout.xaxis.title.text.lower()

    def test_scatter_pnl_mae_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_pnl_mae returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.scatter_pnl_mae()

        assert isinstance(fig, go.Figure)
        # X-axis should be PnL (per user requirement)
        assert "pnl" in fig.layout.xaxis.title.text.lower()

    def test_scatter_pnl_mfe_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_pnl_mfe returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.scatter_pnl_mfe()

        assert isinstance(fig, go.Figure)
        # X-axis should be PnL
        assert "pnl" in fig.layout.xaxis.title.text.lower()

    def test_scatter_pnl_mae_with_regression(self, sample_trades_df: pl.DataFrame) -> None:
        """Test scatter_pnl_mae with regression line."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)

        # With regression
        fig_with = analyzer.scatter_pnl_mae(show_regression=True)
        # Should have at least scatter + regression traces
        trace_names = [t.name for t in fig_with.data]
        assert any("regression" in str(name).lower() for name in trace_names)

        # Without regression
        fig_without = analyzer.scatter_pnl_mae(show_regression=False)
        trace_names = [t.name for t in fig_without.data]
        assert not any("regression" in str(name).lower() for name in trace_names)


class TestDistributionCharts:
    """Test distribution chart methods."""

    def test_distribution_mae_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_mae returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_mae()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_distribution_mae_by_outcome(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_mae split by outcome."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_mae(by_outcome=True)

        # Should have separate traces for winners and losers
        trace_names = [t.name for t in fig.data if t.name]
        assert any("winner" in str(name).lower() for name in trace_names)

    def test_distribution_mfe_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_mfe returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_mfe()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_distribution_comparison_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_comparison returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_comparison()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_distribution_comparison_includes_pnl(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_comparison includes PnL by default (per user requirement)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_comparison()

        trace_names = [t.name for t in fig.data if t.name]
        # Should include PnL in the comparison
        assert any("pnl" in str(name).lower() for name in trace_names)

    def test_distribution_comparison_custom_metrics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test distribution_comparison with custom metrics."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.distribution_comparison(metrics=["mae", "mfe"])

        trace_names = [t.name for t in fig.data if t.name]
        assert any("mae" in str(name).lower() for name in trace_names)
        assert any("mfe" in str(name).lower() for name in trace_names)


class TestRatioAndRelationshipCharts:
    """Test ratio and relationship chart methods."""

    def test_ratio_mfe_mae_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test ratio_mfe_mae returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.ratio_mfe_mae()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_ratio_mfe_mae_by_outcome(self, sample_trades_df: pl.DataFrame) -> None:
        """Test ratio_mfe_mae split by outcome."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.ratio_mfe_mae(by_outcome=True)

        trace_names = [t.name for t in fig.data if t.name]
        assert len(trace_names) >= 2  # Winners and losers

    def test_heatmap_mae_mfe_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test heatmap_mae_mfe returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.heatmap_mae_mfe()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_heatmap_mae_mfe_density_mode(self, sample_trades_df: pl.DataFrame) -> None:
        """Test heatmap with density (not PnL overlay)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.heatmap_mae_mfe(show_pnl_overlay=False)

        assert len(fig.data) > 0


class TestTimeBasedCharts:
    """Test time-based chart methods."""

    def test_timeline_excursion_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test timeline_excursion returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.timeline_excursion()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_timeline_excursion_selective_lines(self, sample_trades_df: pl.DataFrame) -> None:
        """Test timeline_excursion with selective line display."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)

        # Only MAE
        fig = analyzer.timeline_excursion(show_mae=True, show_mfe=False, show_pnl=False)
        assert len(fig.data) >= 1

        # Only MFE
        fig = analyzer.timeline_excursion(show_mae=False, show_mfe=True, show_pnl=False)
        assert len(fig.data) >= 1

    def test_box_by_holding_period_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test box_by_holding_period returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.box_by_holding_period()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_box_by_holding_period_without_column(self, minimal_trades_df: pl.DataFrame) -> None:
        """Test box_by_holding_period handles missing holding_bars column."""
        analyzer = MAEMFEAnalyzer(minimal_trades_df)
        # Should not raise, but return figure with message
        fig = analyzer.box_by_holding_period()
        assert fig is not None


class TestRollingCharts:
    """Test rolling analysis chart methods."""

    def test_rolling_statistics_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test rolling_statistics returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.rolling_statistics(window=20)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_rolling_statistics_multiple_metrics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test rolling_statistics with multiple metrics."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.rolling_statistics(window=20, metrics=["mae", "mfe", "pnl"])

        assert len(fig.data) > 0

    def test_rolling_distribution_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test rolling_distribution returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.rolling_distribution(window=20, step=10)

        assert isinstance(fig, go.Figure)

    def test_rolling_with_small_window(self, sample_trades_df: pl.DataFrame) -> None:
        """Test rolling with small window size."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.rolling_statistics(window=5)
        assert fig is not None


class TestDashboard:
    """Test dashboard generation."""

    def test_dashboard_returns_figure(self, sample_trades_df: pl.DataFrame) -> None:
        """Test dashboard returns valid Figure."""
        import plotly.graph_objects as go

        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.dashboard()

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_dashboard_custom_charts(self, sample_trades_df: pl.DataFrame) -> None:
        """Test dashboard with custom chart selection."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        fig = analyzer.dashboard(charts=["scatter_mae_mfe", "distribution_mae"])

        # Should have fewer traces than full dashboard
        full_fig = analyzer.dashboard()
        assert len(fig.data) <= len(full_fig.data)

    def test_dashboard_filtered_data(self, sample_trades_df: pl.DataFrame) -> None:
        """Test dashboard with filtered data."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1)
        fig = filtered.dashboard()

        assert len(fig.data) > 0


class TestChartEdgeCases:
    """Test chart generation edge cases."""

    def test_charts_with_empty_data(self, empty_trades_df: pl.DataFrame) -> None:
        """Test charts raise ValueError on empty DataFrame."""
        import pytest

        analyzer = MAEMFEAnalyzer(empty_trades_df)

        # All chart methods should raise ValueError with descriptive message
        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.scatter_mae_mfe()

        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.scatter_pnl_mae()

        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.distribution_mae()

        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.ratio_mfe_mae()

        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.heatmap_mae_mfe()

        with pytest.raises(ValueError, match="no trades in filtered dataset"):
            analyzer.timeline_excursion()

    def test_charts_with_single_trade(self, single_trade_df: pl.DataFrame) -> None:
        """Test charts handle single trade DataFrame."""
        analyzer = MAEMFEAnalyzer(single_trade_df)

        # Scatter should work
        fig = analyzer.scatter_mae_mfe()
        assert len(fig.data) > 0

        # Distribution may have limited usefulness but shouldn't crash
        fig = analyzer.distribution_mae()
        assert fig is not None

    def test_charts_with_minimal_data(self, minimal_trades_df: pl.DataFrame) -> None:
        """Test charts with minimal DataFrame (5 trades)."""
        analyzer = MAEMFEAnalyzer(minimal_trades_df)

        # All chart methods should work
        fig = analyzer.scatter_mae_mfe()
        assert len(fig.data) > 0

        fig = analyzer.scatter_pnl_mae()
        assert len(fig.data) > 0

        fig = analyzer.distribution_mae()
        assert fig is not None

        fig = analyzer.distribution_comparison()
        assert fig is not None
