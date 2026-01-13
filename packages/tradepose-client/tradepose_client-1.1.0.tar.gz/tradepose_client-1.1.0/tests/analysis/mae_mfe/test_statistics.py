"""Tests for MAEMFEStatistics class and calculate_statistics function."""

from __future__ import annotations

import polars as pl
import pytest
from tradepose_client.analysis.mae_mfe import MAEMFEAnalyzer, MAEMFEStatistics
from tradepose_client.analysis.mae_mfe.statistics import calculate_statistics


class TestCalculateStatistics:
    """Test calculate_statistics function."""

    def test_basic_statistics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test basic statistics calculation."""
        stats = calculate_statistics(sample_trades_df)

        assert stats.n_trades == 100
        assert stats.n_winners >= 0
        assert stats.n_losers >= 0
        assert stats.n_winners + stats.n_losers == stats.n_trades
        assert 0 <= stats.win_rate <= 1

    def test_mae_statistics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test MAE statistics calculation."""
        stats = calculate_statistics(sample_trades_df)

        assert stats.mae_mean >= 0  # MAE should be non-negative
        assert stats.mae_median >= 0
        assert stats.mae_std >= 0
        assert isinstance(stats.mae_percentiles, dict)
        assert 5 in stats.mae_percentiles
        assert 25 in stats.mae_percentiles
        assert 50 in stats.mae_percentiles
        assert 75 in stats.mae_percentiles
        assert 95 in stats.mae_percentiles

    def test_mfe_statistics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test MFE statistics calculation."""
        stats = calculate_statistics(sample_trades_df)

        assert stats.mfe_mean >= 0
        assert stats.mfe_median >= 0
        assert stats.mfe_std >= 0
        assert isinstance(stats.mfe_percentiles, dict)

    def test_pnl_statistics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test PnL statistics calculation."""
        stats = calculate_statistics(sample_trades_df)

        # PnL can be positive or negative
        assert isinstance(stats.pnl_mean, float)
        assert isinstance(stats.pnl_median, float)
        assert stats.pnl_std >= 0

    def test_by_outcome_statistics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test statistics by outcome (winners/losers)."""
        stats = calculate_statistics(sample_trades_df)

        assert isinstance(stats.mae_winners_mean, float)
        assert isinstance(stats.mae_losers_mean, float)
        assert isinstance(stats.mfe_winners_mean, float)
        assert isinstance(stats.mfe_losers_mean, float)

    def test_correlations_valid_range(self, sample_trades_df: pl.DataFrame) -> None:
        """Test correlations are in valid range [-1, 1]."""
        stats = calculate_statistics(sample_trades_df)

        assert -1 <= stats.correlation_mae_pnl <= 1
        assert -1 <= stats.correlation_mfe_pnl <= 1
        assert -1 <= stats.correlation_mae_mfe <= 1

    def test_optimal_levels(self, sample_trades_df: pl.DataFrame) -> None:
        """Test optimal stop loss and take profit levels."""
        stats = calculate_statistics(sample_trades_df)

        # Optimal levels should be based on percentiles
        assert stats.optimal_stop_loss_p50 == stats.mae_percentiles[50]
        assert stats.optimal_stop_loss_p75 == stats.mae_percentiles[75]
        assert stats.optimal_take_profit_p50 == stats.mfe_percentiles[50]
        assert stats.optimal_take_profit_p75 == stats.mfe_percentiles[75]

    def test_empty_dataframe(self, empty_trades_df: pl.DataFrame) -> None:
        """Test statistics with empty DataFrame."""
        stats = calculate_statistics(empty_trades_df)

        assert stats.n_trades == 0
        assert stats.n_winners == 0
        assert stats.n_losers == 0
        assert stats.win_rate == 0.0
        assert stats.mae_mean == 0.0
        assert stats.mfe_mean == 0.0

    def test_single_trade(self, single_trade_df: pl.DataFrame) -> None:
        """Test statistics with single trade."""
        stats = calculate_statistics(single_trade_df)

        assert stats.n_trades == 1
        assert stats.n_winners == 1
        assert stats.n_losers == 0
        assert stats.win_rate == 1.0
        assert stats.mae_mean == 1.0
        assert stats.mfe_mean == 2.0

    def test_all_winners(self, trades_all_winners: pl.DataFrame) -> None:
        """Test statistics with all winning trades."""
        stats = calculate_statistics(trades_all_winners)

        assert stats.n_losers == 0
        assert stats.win_rate == 1.0
        assert stats.mae_losers_mean == 0.0  # No losers

    def test_all_losers(self, trades_all_losers: pl.DataFrame) -> None:
        """Test statistics with all losing trades."""
        stats = calculate_statistics(trades_all_losers)

        assert stats.n_winners == 0
        assert stats.win_rate == 0.0
        assert stats.mae_winners_mean == 0.0  # No winners

    def test_custom_metrics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test statistics with custom metric columns."""
        stats = calculate_statistics(sample_trades_df, mae_metric="mae_lv1", mfe_metric="g_mfe")

        assert stats.mae_metric == "mae_lv1"
        assert stats.mfe_metric == "g_mfe"
        # Values should be different from default metrics
        default_stats = calculate_statistics(sample_trades_df)
        assert stats.mae_mean != default_stats.mae_mean

    def test_missing_column_raises(self) -> None:
        """Test that missing metric column raises error."""
        df = pl.DataFrame(
            {
                "pnl": [1.0, -1.0],
                "mae": [1.0, 2.0],
                # Missing mfe
            }
        )
        with pytest.raises(ValueError, match="Missing required columns"):
            calculate_statistics(df, mae_metric="mae", mfe_metric="mfe")


class TestMAEMFEStatistics:
    """Test MAEMFEStatistics dataclass methods."""

    def test_summary_string(self, sample_trades_df: pl.DataFrame) -> None:
        """Test summary() returns formatted string."""
        stats = calculate_statistics(sample_trades_df)
        summary = stats.summary()

        assert isinstance(summary, str)
        assert "MAE/MFE Analysis Summary" in summary
        assert "Total Trades:" in summary
        assert "Win Rate:" in summary
        assert "Correlations:" in summary
        assert "Suggested Levels:" in summary

    def test_summary_df(self, sample_trades_df: pl.DataFrame) -> None:
        """Test summary_df property returns DataFrame."""
        stats = calculate_statistics(sample_trades_df)
        df = stats.summary_df

        assert isinstance(df, pl.DataFrame)
        assert "metric" in df.columns
        assert "value" in df.columns
        assert len(df) == 20  # Number of metrics in summary

    def test_repr_html(self, sample_trades_df: pl.DataFrame) -> None:
        """Test _repr_html_ returns valid HTML."""
        stats = calculate_statistics(sample_trades_df)
        html = stats._repr_html_()

        assert isinstance(html, str)
        assert "MAE/MFE Statistics" in html
        assert "<div" in html
        assert "<table" in html


class TestMAEMFEAnalyzerStatistics:
    """Test statistics method on MAEMFEAnalyzer."""

    def test_statistics_method(self, sample_trades_df: pl.DataFrame) -> None:
        """Test analyzer.statistics() method."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        stats = analyzer.statistics()

        assert isinstance(stats, MAEMFEStatistics)
        assert stats.n_trades == 100

    def test_statistics_with_filters(self, sample_trades_df: pl.DataFrame) -> None:
        """Test statistics on filtered data."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        filtered = analyzer.filter(direction=1)
        stats = filtered.statistics()

        assert stats.n_trades < 100
        # All trades should be long
        assert stats.n_trades == len(filtered.trades)

    def test_statistics_custom_metrics(self, sample_trades_df: pl.DataFrame) -> None:
        """Test statistics with custom metric parameters."""
        analyzer = MAEMFEAnalyzer(sample_trades_df)
        stats = analyzer.statistics(mae_metric="mae_lv1", mfe_metric="g_mfe")

        assert stats.mae_metric == "mae_lv1"
        assert stats.mfe_metric == "g_mfe"
