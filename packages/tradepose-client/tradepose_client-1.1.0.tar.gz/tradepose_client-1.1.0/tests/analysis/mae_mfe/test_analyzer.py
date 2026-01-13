"""Tests for MAEMFEAnalyzer class."""

from __future__ import annotations

import polars as pl
import pytest
from tradepose_client.analysis.mae_mfe import ChartConfig, MAEMFEAnalyzer


class TestMAEMFEAnalyzerInit:
    """Test analyzer initialization."""

    def test_init_valid_dataframe(self, sample_trades_df: pl.DataFrame) -> None:
        """Test initialization with valid DataFrame."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        assert analyzer.n_trades == 100
        assert analyzer.trades is not None

    def test_init_minimal_dataframe(self, minimal_trades_df: pl.DataFrame) -> None:
        """Test initialization with minimal DataFrame."""
        analyzer = MAEMFEAnalyzer(minimal_trades_df)
        assert analyzer.n_trades == 5

    def test_init_empty_dataframe(self, empty_trades_df: pl.DataFrame) -> None:
        """Test initialization with empty DataFrame."""
        analyzer = MAEMFEAnalyzer(empty_trades_df)
        assert analyzer.n_trades == 0

    def test_init_missing_required_columns_raises(self) -> None:
        """Test initialization raises error for missing required columns."""
        df = pl.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
        with pytest.raises(ValueError, match="Missing required columns"):
            MAEMFEAnalyzer(df)

    def test_init_missing_pnl_raises(self) -> None:
        """Test initialization raises error when pnl is missing."""
        df = pl.DataFrame(
            {
                "direction": [1, -1],
                "mae": [1.0, 2.0],
                "mfe": [2.0, 1.0],
            }
        )
        with pytest.raises(ValueError, match="pnl"):
            MAEMFEAnalyzer(df)

    def test_init_with_custom_config(self, sample_trades_df: pl.DataFrame) -> None:
        """Test initialization with custom configuration."""
        config = ChartConfig(width=800, height=400, theme="plotly_dark")
        analyzer = MAEMFEAnalyzer(sample_trades_df, config=config)
        assert analyzer.config.width == 800
        assert analyzer.config.height == 400
        assert analyzer.config.theme == "plotly_dark"


class TestMAEMFEAnalyzerFilter:
    """Test filter methods."""

    def test_filter_by_direction_long(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by direction (long)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1)
        assert all(filtered.trades["direction"] == 1)
        assert filtered.n_trades < analyzer.n_trades

    def test_filter_by_direction_short(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by direction (short)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=-1)
        assert all(filtered.trades["direction"] == -1)

    def test_filter_by_profitable_winners(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by profitable trades (winners)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(profitable=True)
        assert all(filtered.trades["pnl"] > 0)

    def test_filter_by_profitable_losers(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by profitable trades (losers)."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(profitable=False)
        assert all(filtered.trades["pnl"] <= 0)

    def test_filter_by_strategy(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by strategy name."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(strategy="Strategy_A")
        assert all(filtered.trades["strategy_name"] == "Strategy_A")

    def test_filter_by_multiple_strategies(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by multiple strategy names."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(strategy=["Strategy_A", "Strategy_B"])
        # Should include all trades (both strategies)
        assert filtered.n_trades == analyzer.n_trades

    def test_filter_by_blueprint(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by blueprint name."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(blueprint="Blueprint_1")
        assert all(filtered.trades["blueprint_name"] == "Blueprint_1")

    def test_filter_by_holding_bars_min(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by minimum holding bars."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(min_holding_bars=100)
        assert all(filtered.trades["holding_bars"] >= 100)

    def test_filter_by_holding_bars_max(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filtering by maximum holding bars."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(max_holding_bars=50)
        assert all(filtered.trades["holding_bars"] <= 50)

    def test_filter_chain(self, sample_trades_df: pl.DataFrame) -> None:
        """Test chained filters."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1).filter(profitable=True)
        assert all(filtered.trades["direction"] == 1)
        assert all(filtered.trades["pnl"] > 0)

    def test_filter_returns_new_instance(self, sample_trades_df: pl.DataFrame) -> None:
        """Test that filter returns a new analyzer instance."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1)
        assert filtered is not analyzer
        # Original should be unchanged
        assert analyzer.n_trades == 100

    def test_reset_filters(self, sample_trades_df: pl.DataFrame) -> None:
        """Test filter reset."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1, profitable=True)
        reset = filtered.reset_filters()
        assert reset.n_trades == 100


class TestMAEMFEAnalyzerProperties:
    """Test analyzer properties."""

    def test_trades_property(self, sample_trades_df: pl.DataFrame) -> None:
        """Test trades property returns DataFrame."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        assert isinstance(analyzer.trades, pl.DataFrame)
        assert len(analyzer.trades) == 100

    def test_n_trades_property(self, sample_trades_df: pl.DataFrame) -> None:
        """Test n_trades property."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        assert analyzer.n_trades == 100

    def test_config_property(self, sample_trades_df: pl.DataFrame) -> None:
        """Test config property."""
        config = ChartConfig(width=1200)
        analyzer = MAEMFEAnalyzer(sample_trades_df, config=config)
        assert analyzer.config.width == 1200

    def test_available_metrics_property(self, sample_trades_df: pl.DataFrame) -> None:
        """Test available_metrics property."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        metrics = analyzer.available_metrics
        assert "mae" in metrics
        assert "mfe" in metrics
        assert "g_mfe" in metrics


class TestMAEMFEAnalyzerJupyter:
    """Test Jupyter integration."""

    def test_repr_html(self, sample_trades_df: pl.DataFrame) -> None:
        """Test _repr_html_ returns valid HTML."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        html = analyzer._repr_html_()
        assert isinstance(html, str)
        assert "MAE/MFE Analyzer" in html
        assert "100" in html  # Trade count

    def test_repr_html_with_filters(self, sample_trades_df: pl.DataFrame) -> None:
        """Test _repr_html_ shows filter info."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1)
        html = filtered._repr_html_()
        assert "Filters applied" in html
