"""MAE/MFE Statistics calculations and data classes."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from .types import MetricType, PnLColumn


@dataclass
class MAEMFEStatistics:
    """Comprehensive MAE/MFE statistics container.

    This dataclass holds all computed statistics for MAE/MFE analysis,
    including basic counts, distribution metrics, correlations, and
    suggested optimal levels.

    Attributes:
        n_trades: Total number of trades.
        n_winners: Number of profitable trades.
        n_losers: Number of losing trades.
        win_rate: Win rate as a decimal (0-1).

        mae_mean: Mean MAE value.
        mae_median: Median MAE value.
        mae_std: Standard deviation of MAE.
        mae_percentiles: Dict of percentiles {5, 25, 50, 75, 95}.

        mfe_mean: Mean MFE value.
        mfe_median: Median MFE value.
        mfe_std: Standard deviation of MFE.
        mfe_percentiles: Dict of percentiles {5, 25, 50, 75, 95}.

        pnl_mean: Mean PnL.
        pnl_median: Median PnL.
        pnl_std: Standard deviation of PnL.

        mae_winners_mean: Mean MAE for winning trades.
        mae_losers_mean: Mean MAE for losing trades.
        mfe_winners_mean: Mean MFE for winning trades.
        mfe_losers_mean: Mean MFE for losing trades.

        correlation_mae_pnl: Correlation between MAE and PnL.
        correlation_mfe_pnl: Correlation between MFE and PnL.
        correlation_mae_mfe: Correlation between MAE and MFE.

        optimal_stop_loss_p50: Suggested stop loss at 50th percentile MAE.
        optimal_stop_loss_p75: Suggested stop loss at 75th percentile MAE.
        optimal_take_profit_p50: Suggested take profit at 50th percentile MFE.
        optimal_take_profit_p75: Suggested take profit at 75th percentile MFE.

        mae_metric: MAE metric column used for calculations.
        mfe_metric: MFE metric column used for calculations.
    """

    # Core counts
    n_trades: int
    n_winners: int
    n_losers: int
    win_rate: float

    # MAE statistics
    mae_mean: float
    mae_median: float
    mae_std: float
    mae_percentiles: dict[int, float]

    # MFE statistics
    mfe_mean: float
    mfe_median: float
    mfe_std: float
    mfe_percentiles: dict[int, float]

    # PnL statistics
    pnl_mean: float
    pnl_median: float
    pnl_std: float

    # By outcome
    mae_winners_mean: float
    mae_losers_mean: float
    mfe_winners_mean: float
    mfe_losers_mean: float

    # Correlations
    correlation_mae_pnl: float
    correlation_mfe_pnl: float
    correlation_mae_mfe: float

    # Optimal levels
    optimal_stop_loss_p50: float
    optimal_stop_loss_p75: float
    optimal_take_profit_p50: float
    optimal_take_profit_p75: float

    # Metadata
    mae_metric: str
    mfe_metric: str

    def summary(self) -> str:
        """Return formatted summary string.

        Returns:
            Multi-line string with key statistics.
        """
        return f"""
MAE/MFE Analysis Summary
========================
Total Trades: {self.n_trades:,}
Win Rate: {self.win_rate:.1%} ({self.n_winners:,} winners, {self.n_losers:,} losers)

{self.mae_metric.upper()} Statistics:
  Mean: {self.mae_mean:.4f}  Median: {self.mae_median:.4f}  Std: {self.mae_std:.4f}
  Percentiles: P5={self.mae_percentiles[5]:.4f}  P25={self.mae_percentiles[25]:.4f}  P75={self.mae_percentiles[75]:.4f}  P95={self.mae_percentiles[95]:.4f}
  Winners Mean: {self.mae_winners_mean:.4f}  Losers Mean: {self.mae_losers_mean:.4f}

{self.mfe_metric.upper()} Statistics:
  Mean: {self.mfe_mean:.4f}  Median: {self.mfe_median:.4f}  Std: {self.mfe_std:.4f}
  Percentiles: P5={self.mfe_percentiles[5]:.4f}  P25={self.mfe_percentiles[25]:.4f}  P75={self.mfe_percentiles[75]:.4f}  P95={self.mfe_percentiles[95]:.4f}
  Winners Mean: {self.mfe_winners_mean:.4f}  Losers Mean: {self.mfe_losers_mean:.4f}

PnL Statistics:
  Mean: {self.pnl_mean:.4f}  Median: {self.pnl_median:.4f}  Std: {self.pnl_std:.4f}

Correlations:
  {self.mae_metric.upper()}-PnL: {self.correlation_mae_pnl:+.3f}
  {self.mfe_metric.upper()}-PnL: {self.correlation_mfe_pnl:+.3f}
  {self.mae_metric.upper()}-{self.mfe_metric.upper()}: {self.correlation_mae_mfe:+.3f}

Suggested Levels:
  Stop Loss (P50/P75 {self.mae_metric.upper()}): {self.optimal_stop_loss_p50:.4f} / {self.optimal_stop_loss_p75:.4f}
  Take Profit (P50/P75 {self.mfe_metric.upper()}): {self.optimal_take_profit_p50:.4f} / {self.optimal_take_profit_p75:.4f}
"""

    @property
    def summary_df(self) -> pl.DataFrame:
        """Return statistics as Polars DataFrame.

        Returns:
            DataFrame with metric names and values.
        """
        return pl.DataFrame(
            {
                "metric": [
                    "n_trades",
                    "n_winners",
                    "n_losers",
                    "win_rate",
                    f"{self.mae_metric}_mean",
                    f"{self.mae_metric}_median",
                    f"{self.mae_metric}_std",
                    f"{self.mae_metric}_p25",
                    f"{self.mae_metric}_p75",
                    f"{self.mfe_metric}_mean",
                    f"{self.mfe_metric}_median",
                    f"{self.mfe_metric}_std",
                    f"{self.mfe_metric}_p25",
                    f"{self.mfe_metric}_p75",
                    "pnl_mean",
                    "pnl_median",
                    "pnl_std",
                    f"corr_{self.mae_metric}_pnl",
                    f"corr_{self.mfe_metric}_pnl",
                    f"corr_{self.mae_metric}_{self.mfe_metric}",
                ],
                "value": [
                    float(self.n_trades),
                    float(self.n_winners),
                    float(self.n_losers),
                    self.win_rate,
                    self.mae_mean,
                    self.mae_median,
                    self.mae_std,
                    self.mae_percentiles[25],
                    self.mae_percentiles[75],
                    self.mfe_mean,
                    self.mfe_median,
                    self.mfe_std,
                    self.mfe_percentiles[25],
                    self.mfe_percentiles[75],
                    self.pnl_mean,
                    self.pnl_median,
                    self.pnl_std,
                    self.correlation_mae_pnl,
                    self.correlation_mfe_pnl,
                    self.correlation_mae_mfe,
                ],
            }
        )

    def _repr_html_(self) -> str:
        """Jupyter HTML representation.

        Returns:
            HTML string for Jupyter display.
        """

        # Determine correlation colors
        def corr_color(val: float) -> str:
            if val > 0.3:
                return "#4CAF50"  # Green for positive
            elif val < -0.3:
                return "#F44336"  # Red for negative
            return "#9E9E9E"  # Grey for neutral

        mae_pnl_color = corr_color(self.correlation_mae_pnl)
        mfe_pnl_color = corr_color(self.correlation_mfe_pnl)

        return f"""
        <div style="border: 2px solid #1976D2; padding: 15px; border-radius: 8px;
                    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
                    max-width: 800px;">
            <h3 style="margin-top: 0; color: #1565C0;">
                MAE/MFE Statistics
                <span style="font-size: 0.7em; color: #666;">
                    ({self.mae_metric.upper()}/{self.mfe_metric.upper()})
                </span>
            </h3>

            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <!-- Overview -->
                <div style="flex: 1; min-width: 200px; background: white; padding: 10px;
                            border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0 0 10px 0; color: #333;">Overview</h4>
                    <table style="width: 100%; font-size: 0.9em;">
                        <tr>
                            <td>Trades:</td>
                            <td style="text-align: right;"><b>{self.n_trades:,}</b></td>
                        </tr>
                        <tr>
                            <td>Win Rate:</td>
                            <td style="text-align: right;"><b>{self.win_rate:.1%}</b></td>
                        </tr>
                        <tr>
                            <td>Winners/Losers:</td>
                            <td style="text-align: right;">
                                <span style="color: #4CAF50;">{self.n_winners:,}</span> /
                                <span style="color: #F44336;">{self.n_losers:,}</span>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- MAE Stats -->
                <div style="flex: 1; min-width: 200px; background: white; padding: 10px;
                            border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0 0 10px 0; color: #F44336;">
                        {self.mae_metric.upper()} (Adverse)
                    </h4>
                    <table style="width: 100%; font-size: 0.9em;">
                        <tr>
                            <td>Mean:</td>
                            <td style="text-align: right;">{self.mae_mean:.4f}</td>
                        </tr>
                        <tr>
                            <td>Median:</td>
                            <td style="text-align: right;">{self.mae_median:.4f}</td>
                        </tr>
                        <tr>
                            <td>P75:</td>
                            <td style="text-align: right;">{self.mae_percentiles[75]:.4f}</td>
                        </tr>
                    </table>
                </div>

                <!-- MFE Stats -->
                <div style="flex: 1; min-width: 200px; background: white; padding: 10px;
                            border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0 0 10px 0; color: #4CAF50;">
                        {self.mfe_metric.upper()} (Favorable)
                    </h4>
                    <table style="width: 100%; font-size: 0.9em;">
                        <tr>
                            <td>Mean:</td>
                            <td style="text-align: right;">{self.mfe_mean:.4f}</td>
                        </tr>
                        <tr>
                            <td>Median:</td>
                            <td style="text-align: right;">{self.mfe_median:.4f}</td>
                        </tr>
                        <tr>
                            <td>P75:</td>
                            <td style="text-align: right;">{self.mfe_percentiles[75]:.4f}</td>
                        </tr>
                    </table>
                </div>
            </div>

            <!-- Correlations -->
            <div style="margin-top: 15px; background: white; padding: 10px;
                        border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 10px 0; color: #333;">Correlations</h4>
                <div style="display: flex; gap: 30px; font-size: 0.9em;">
                    <span>
                        {self.mae_metric.upper()}-PnL:
                        <b style="color: {mae_pnl_color};">{self.correlation_mae_pnl:+.3f}</b>
                    </span>
                    <span>
                        {self.mfe_metric.upper()}-PnL:
                        <b style="color: {mfe_pnl_color};">{self.correlation_mfe_pnl:+.3f}</b>
                    </span>
                    <span>
                        {self.mae_metric.upper()}-{self.mfe_metric.upper()}:
                        <b>{self.correlation_mae_mfe:+.3f}</b>
                    </span>
                </div>
            </div>

            <!-- Suggested Levels -->
            <div style="margin-top: 15px; background: #FFF9C4; padding: 10px;
                        border-radius: 4px; border-left: 4px solid #FBC02D;">
                <h4 style="margin: 0 0 5px 0; color: #F57F17;">Suggested Levels</h4>
                <div style="font-size: 0.9em;">
                    Stop Loss (P50/P75): <b>{self.optimal_stop_loss_p50:.4f}</b> /
                    <b>{self.optimal_stop_loss_p75:.4f}</b>
                    &nbsp;|&nbsp;
                    Take Profit (P50/P75): <b>{self.optimal_take_profit_p50:.4f}</b> /
                    <b>{self.optimal_take_profit_p75:.4f}</b>
                </div>
            </div>
        </div>
        """


def calculate_statistics(
    trades: pl.DataFrame,
    *,
    mae_metric: MetricType = "mae",
    mfe_metric: MetricType = "mfe",
    pnl_column: PnLColumn = "pnl",
) -> MAEMFEStatistics:
    """Calculate comprehensive MAE/MFE statistics from trades DataFrame.

    Args:
        trades: Polars DataFrame with required columns.
        mae_metric: MAE metric column to use.
        mfe_metric: MFE metric column to use.
        pnl_column: PnL column to use ('pnl' or 'pnl_pct').

    Returns:
        MAEMFEStatistics instance with computed metrics.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate columns
    required = {pnl_column, mae_metric, mfe_metric}
    missing = required - set(trades.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Handle empty DataFrame
    if len(trades) == 0:
        return MAEMFEStatistics(
            n_trades=0,
            n_winners=0,
            n_losers=0,
            win_rate=0.0,
            mae_mean=0.0,
            mae_median=0.0,
            mae_std=0.0,
            mae_percentiles={5: 0.0, 25: 0.0, 50: 0.0, 75: 0.0, 95: 0.0},
            mfe_mean=0.0,
            mfe_median=0.0,
            mfe_std=0.0,
            mfe_percentiles={5: 0.0, 25: 0.0, 50: 0.0, 75: 0.0, 95: 0.0},
            pnl_mean=0.0,
            pnl_median=0.0,
            pnl_std=0.0,
            mae_winners_mean=0.0,
            mae_losers_mean=0.0,
            mfe_winners_mean=0.0,
            mfe_losers_mean=0.0,
            correlation_mae_pnl=0.0,
            correlation_mfe_pnl=0.0,
            correlation_mae_mfe=0.0,
            optimal_stop_loss_p50=0.0,
            optimal_stop_loss_p75=0.0,
            optimal_take_profit_p50=0.0,
            optimal_take_profit_p75=0.0,
            mae_metric=mae_metric,
            mfe_metric=mfe_metric,
        )

    # Basic counts
    n_trades = len(trades)
    winners = trades.filter(pl.col(pnl_column) > 0)
    losers = trades.filter(pl.col(pnl_column) <= 0)
    n_winners = len(winners)
    n_losers = len(losers)
    win_rate = n_winners / n_trades if n_trades > 0 else 0.0

    # MAE statistics
    mae_stats = trades.select(
        [
            pl.col(mae_metric).mean().alias("mean"),
            pl.col(mae_metric).median().alias("median"),
            pl.col(mae_metric).std().alias("std"),
            pl.col(mae_metric).quantile(0.05).alias("p5"),
            pl.col(mae_metric).quantile(0.25).alias("p25"),
            pl.col(mae_metric).quantile(0.50).alias("p50"),
            pl.col(mae_metric).quantile(0.75).alias("p75"),
            pl.col(mae_metric).quantile(0.95).alias("p95"),
        ]
    ).row(0)

    # MFE statistics
    mfe_stats = trades.select(
        [
            pl.col(mfe_metric).mean().alias("mean"),
            pl.col(mfe_metric).median().alias("median"),
            pl.col(mfe_metric).std().alias("std"),
            pl.col(mfe_metric).quantile(0.05).alias("p5"),
            pl.col(mfe_metric).quantile(0.25).alias("p25"),
            pl.col(mfe_metric).quantile(0.50).alias("p50"),
            pl.col(mfe_metric).quantile(0.75).alias("p75"),
            pl.col(mfe_metric).quantile(0.95).alias("p95"),
        ]
    ).row(0)

    # PnL statistics
    pnl_stats = trades.select(
        [
            pl.col(pnl_column).mean().alias("mean"),
            pl.col(pnl_column).median().alias("median"),
            pl.col(pnl_column).std().alias("std"),
        ]
    ).row(0)

    # By outcome statistics
    mae_winners_mean = winners.select(pl.col(mae_metric).mean()).item() if n_winners > 0 else 0.0
    mae_losers_mean = losers.select(pl.col(mae_metric).mean()).item() if n_losers > 0 else 0.0
    mfe_winners_mean = winners.select(pl.col(mfe_metric).mean()).item() if n_winners > 0 else 0.0
    mfe_losers_mean = losers.select(pl.col(mfe_metric).mean()).item() if n_losers > 0 else 0.0

    # Correlations
    correlations = trades.select(
        [
            pl.corr(mae_metric, pnl_column).alias("mae_pnl"),
            pl.corr(mfe_metric, pnl_column).alias("mfe_pnl"),
            pl.corr(mae_metric, mfe_metric).alias("mae_mfe"),
        ]
    ).row(0)

    # Handle NaN correlations (can happen with constant values)
    corr_mae_pnl = correlations[0] if correlations[0] is not None else 0.0
    corr_mfe_pnl = correlations[1] if correlations[1] is not None else 0.0
    corr_mae_mfe = correlations[2] if correlations[2] is not None else 0.0

    return MAEMFEStatistics(
        n_trades=n_trades,
        n_winners=n_winners,
        n_losers=n_losers,
        win_rate=win_rate,
        mae_mean=mae_stats[0] or 0.0,
        mae_median=mae_stats[1] or 0.0,
        mae_std=mae_stats[2] or 0.0,
        mae_percentiles={
            5: mae_stats[3] or 0.0,
            25: mae_stats[4] or 0.0,
            50: mae_stats[5] or 0.0,
            75: mae_stats[6] or 0.0,
            95: mae_stats[7] or 0.0,
        },
        mfe_mean=mfe_stats[0] or 0.0,
        mfe_median=mfe_stats[1] or 0.0,
        mfe_std=mfe_stats[2] or 0.0,
        mfe_percentiles={
            5: mfe_stats[3] or 0.0,
            25: mfe_stats[4] or 0.0,
            50: mfe_stats[5] or 0.0,
            75: mfe_stats[6] or 0.0,
            95: mfe_stats[7] or 0.0,
        },
        pnl_mean=pnl_stats[0] or 0.0,
        pnl_median=pnl_stats[1] or 0.0,
        pnl_std=pnl_stats[2] or 0.0,
        mae_winners_mean=mae_winners_mean or 0.0,
        mae_losers_mean=mae_losers_mean or 0.0,
        mfe_winners_mean=mfe_winners_mean or 0.0,
        mfe_losers_mean=mfe_losers_mean or 0.0,
        correlation_mae_pnl=corr_mae_pnl,
        correlation_mfe_pnl=corr_mfe_pnl,
        correlation_mae_mfe=corr_mae_mfe,
        optimal_stop_loss_p50=mae_stats[5] or 0.0,
        optimal_stop_loss_p75=mae_stats[6] or 0.0,
        optimal_take_profit_p50=mfe_stats[5] or 0.0,
        optimal_take_profit_p75=mfe_stats[6] or 0.0,
        mae_metric=mae_metric,
        mfe_metric=mfe_metric,
    )
