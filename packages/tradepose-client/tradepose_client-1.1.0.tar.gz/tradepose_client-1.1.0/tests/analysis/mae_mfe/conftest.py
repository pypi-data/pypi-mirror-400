"""Test fixtures for MAE/MFE analysis tests."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest


@pytest.fixture
def sample_trades_df() -> pl.DataFrame:
    """Generate sample trades DataFrame with MAE/MFE data.

    Creates 100 trades with realistic MAE/MFE patterns:
    - Winners tend to have higher MFE than MAE
    - Losers tend to have higher MAE than MFE
    """
    np.random.seed(42)
    n_trades = 100

    # Generate trade parameters
    directions = np.random.choice([1, -1], size=n_trades)
    entry_prices = np.random.uniform(100, 110, size=n_trades)

    # Generate MAE/MFE with some realistic correlation to PnL
    # MAE is typically positive (adverse movement)
    mae = np.abs(np.random.exponential(2.0, size=n_trades))
    # MFE is typically positive (favorable movement)
    mfe = np.abs(np.random.exponential(3.0, size=n_trades))

    # Calculate PnL based on direction and excursions
    # Simplified: PnL ~ MFE - MAE + noise
    pnl = (mfe - mae) * directions + np.random.normal(0, 0.5, size=n_trades)
    pnl_pct = pnl / entry_prices * 100

    # Additional metrics
    g_mfe = mfe * np.random.uniform(1.0, 1.2, size=n_trades)
    mae_lv1 = mae * np.random.uniform(0.3, 0.7, size=n_trades)
    mhl = mfe + mae  # Max high/low range

    # Index columns (trade number where excursion occurred)
    mae_idx = np.random.randint(1, 50, size=n_trades).astype(np.uint32)
    mfe_idx = np.random.randint(1, 50, size=n_trades).astype(np.uint32)
    g_mfe_idx = np.random.randint(1, 50, size=n_trades).astype(np.uint32)

    # Volatility columns
    base_vol = np.random.uniform(0.5, 2.0, size=n_trades)
    entry_volatility = base_vol
    exit_volatility = base_vol * np.random.uniform(0.9, 1.1, size=n_trades)
    mae_volatility = base_vol * np.random.uniform(0.9, 1.1, size=n_trades)
    mfe_volatility = base_vol * np.random.uniform(0.9, 1.1, size=n_trades)
    g_mfe_volatility = base_vol * np.random.uniform(0.9, 1.1, size=n_trades)

    # Holding period
    holding_bars = np.random.randint(5, 200, size=n_trades).astype(np.uint32)
    holding_seconds = holding_bars * 60 * 15  # Assume 15-min bars

    # Strategy/Blueprint names
    strategies = np.random.choice(["Strategy_A", "Strategy_B"], size=n_trades)
    blueprints = np.random.choice(["Blueprint_1", "Blueprint_2", "Blueprint_3"], size=n_trades)

    return pl.DataFrame(
        {
            "final_position_id": np.arange(n_trades, dtype=np.uint32),
            "direction": directions.astype(np.int32),
            "entry_price": entry_prices,
            "exit_price": entry_prices + pnl,
            # MAE/MFE metrics
            "mae": mae,
            "mfe": mfe,
            "g_mfe": g_mfe,
            "mae_lv1": mae_lv1,
            "mhl": mhl,
            # Index columns
            "mae_idx": mae_idx,
            "mfe_idx": mfe_idx,
            "g_mfe_idx": g_mfe_idx,
            # PnL
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            # Holding period
            "holding_bars": holding_bars,
            "holding_seconds": holding_seconds.astype(np.int64),
            # Volatility
            "entry_volatility": entry_volatility,
            "exit_volatility": exit_volatility,
            "mae_volatility": mae_volatility,
            "mfe_volatility": mfe_volatility,
            "g_mfe_volatility": g_mfe_volatility,
            # Strategy info
            "strategy_name": strategies,
            "blueprint_name": blueprints,
        }
    )


@pytest.fixture
def minimal_trades_df() -> pl.DataFrame:
    """Minimal trades DataFrame for edge case testing.

    Contains only the required columns with 5 trades.
    """
    return pl.DataFrame(
        {
            "direction": [1, -1, 1, -1, 1],
            "mae": [1.0, 2.0, 1.5, 3.0, 0.5],
            "mfe": [2.0, 1.0, 2.5, 1.0, 3.0],
            "pnl": [1.0, -1.0, 1.0, -2.0, 2.5],
        }
    )


@pytest.fixture
def empty_trades_df() -> pl.DataFrame:
    """Empty trades DataFrame for edge case testing."""
    return pl.DataFrame(
        {
            "direction": pl.Series([], dtype=pl.Int32),
            "mae": pl.Series([], dtype=pl.Float64),
            "mfe": pl.Series([], dtype=pl.Float64),
            "pnl": pl.Series([], dtype=pl.Float64),
        }
    )


@pytest.fixture
def single_trade_df() -> pl.DataFrame:
    """Single trade DataFrame for edge case testing."""
    return pl.DataFrame(
        {
            "direction": [1],
            "mae": [1.0],
            "mfe": [2.0],
            "pnl": [1.0],
        }
    )


@pytest.fixture
def trades_all_winners() -> pl.DataFrame:
    """Trades DataFrame with all winning trades."""
    np.random.seed(123)
    n = 20
    return pl.DataFrame(
        {
            "direction": np.random.choice([1, -1], size=n),
            "mae": np.random.uniform(0.5, 2.0, size=n),
            "mfe": np.random.uniform(2.0, 5.0, size=n),
            "pnl": np.random.uniform(0.1, 3.0, size=n),  # All positive
        }
    )


@pytest.fixture
def trades_all_losers() -> pl.DataFrame:
    """Trades DataFrame with all losing trades."""
    np.random.seed(456)
    n = 20
    return pl.DataFrame(
        {
            "direction": np.random.choice([1, -1], size=n),
            "mae": np.random.uniform(2.0, 5.0, size=n),
            "mfe": np.random.uniform(0.5, 2.0, size=n),
            "pnl": np.random.uniform(-3.0, -0.1, size=n),  # All negative
        }
    )
