"""Unit tests for batch testing models."""

from datetime import date, datetime

import pytest
from tradepose_client.batch.models import BacktestRequest, Period


class TestPeriod:
    """Test Period model."""

    def test_period_from_strings(self):
        """Test period creation from ISO strings."""
        period = Period(start="2021-01-01", end="2021-12-31")

        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)
        assert period.start.year == 2021
        assert period.end.year == 2021

    def test_period_from_dates(self):
        """Test period creation from date objects."""
        period = Period(start=date(2021, 1, 1), end=date(2021, 12, 31))

        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_period_from_datetimes(self):
        """Test period creation from datetime objects."""
        start = datetime(2021, 1, 1, 0, 0, 0)
        end = datetime(2021, 12, 31, 23, 59, 59)
        period = Period(start=start, end=end)

        assert period.start == start
        assert period.end == end

    def test_period_to_iso(self):
        """Test ISO string conversion."""
        period = Period(start="2021-01-01", end="2021-12-31")
        start_iso, end_iso = period.to_iso()

        assert isinstance(start_iso, str)
        assert isinstance(end_iso, str)
        assert "2021-01-01" in start_iso
        assert "2021-12-31" in end_iso

    def test_period_to_key(self):
        """Test period key generation."""
        period = Period(start="2021-01-01", end="2021-12-31")
        key = period.to_key()

        assert key == "2021-01-01_2021-12-31"

    def test_period_mixed_formats(self):
        """Test period with mixed input formats."""
        period = Period(start=date(2021, 1, 1), end="2021-12-31T23:59:59")

        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_period_validation_start_after_end(self):
        """Test validation fails when start >= end."""
        with pytest.raises(ValueError, match="must be before"):
            Period(start="2021-12-31", end="2021-01-01")

    def test_period_validation_start_equals_end(self):
        """Test validation fails when start == end."""
        with pytest.raises(ValueError, match="must be before"):
            Period(start="2021-01-01", end="2021-01-01")

    def test_period_q1_constructor(self):
        """Test Q1 convenience constructor."""
        period = Period.Q1(2024)

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 3
        assert period.end.day == 31

    def test_period_q2_constructor(self):
        """Test Q2 convenience constructor."""
        period = Period.Q2(2024)

        assert period.start.month == 4
        assert period.start.day == 1
        assert period.end.month == 6
        assert period.end.day == 30

    def test_period_q3_constructor(self):
        """Test Q3 convenience constructor."""
        period = Period.Q3(2024)

        assert period.start.month == 7
        assert period.start.day == 1
        assert period.end.month == 9
        assert period.end.day == 30

    def test_period_q4_constructor(self):
        """Test Q4 convenience constructor."""
        period = Period.Q4(2024)

        assert period.start.month == 10
        assert period.start.day == 1
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_year(self):
        """Test from_year convenience constructor."""
        period = Period.from_year(2024)

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_year_multi_forward(self):
        """Test from_year with multiple years forward."""
        period = Period.from_year(2024, n_years=3)  # 2024-2026

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2026
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_year_backward(self):
        """Test from_year with backward years."""
        period = Period.from_year(2024, n_years=-2)  # 2023-2024

        assert period.start.year == 2023
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_year_five_year_trend(self):
        """Test from_year for long-term analysis."""
        period = Period.from_year(2020, n_years=5)  # 2020-2024

        assert period.start.year == 2020
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_year_zero_fails(self):
        """Test from_year fails with n_years=0."""
        with pytest.raises(ValueError, match="n_years cannot be 0"):
            Period.from_year(2024, n_years=0)

    def test_period_from_month_regular(self):
        """Test from_month for regular month."""
        period = Period.from_month(2024, 3)  # March

        assert period.start.month == 3
        assert period.start.day == 1
        assert period.end.month == 3
        assert period.end.day == 31

    def test_period_from_month_february_leap_year(self):
        """Test from_month for February in leap year."""
        period = Period.from_month(2024, 2)  # 2024 is leap year

        assert period.start.day == 1
        assert period.end.day == 29  # Leap year

    def test_period_from_month_february_non_leap_year(self):
        """Test from_month for February in non-leap year."""
        period = Period.from_month(2023, 2)  # 2023 is not leap year

        assert period.start.day == 1
        assert period.end.day == 28

    def test_period_from_month_invalid_month(self):
        """Test from_month fails with invalid month."""
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            Period.from_month(2024, 13)

        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            Period.from_month(2024, 0)

    def test_period_from_month_with_n_months_three(self):
        """Test from_month with n_months=3 (quarter)."""
        period = Period.from_month(2024, 3, n_months=3)  # March to May

        assert period.start.year == 2024
        assert period.start.month == 3
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 5
        assert period.end.day == 31

    def test_period_from_month_with_n_months_six(self):
        """Test from_month with n_months=6 (half year)."""
        period = Period.from_month(2024, 1, n_months=6)  # Jan to Jun

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 6
        assert period.end.day == 30

    def test_period_from_month_with_n_months_cross_year(self):
        """Test from_month spanning across year boundary."""
        period = Period.from_month(2024, 11, n_months=3)  # Nov 2024 to Jan 2025

        assert period.start.year == 2024
        assert period.start.month == 11
        assert period.start.day == 1
        assert period.end.year == 2025
        assert period.end.month == 1
        assert period.end.day == 31

    def test_period_from_month_with_n_months_february_leap(self):
        """Test from_month ending in February leap year."""
        period = Period.from_month(2023, 12, n_months=3)  # Dec 2023 to Feb 2024 (leap)

        assert period.start.year == 2023
        assert period.start.month == 12
        assert period.end.year == 2024
        assert period.end.month == 2
        assert period.end.day == 29  # Leap year

    def test_period_from_month_with_n_months_zero(self):
        """Test from_month fails with n_months=0."""
        with pytest.raises(ValueError, match="n_months cannot be 0"):
            Period.from_month(2024, 1, n_months=0)

    def test_period_from_month_backward_three_months(self):
        """Test from_month with negative n_months (backward)."""
        period = Period.from_month(2024, 3, n_months=-3)  # Jan-Mar, ending at Mar

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 3
        assert period.end.day == 31

    def test_period_from_month_backward_six_months(self):
        """Test from_month with backward 6 months."""
        period = Period.from_month(2024, 6, n_months=-6)  # Jan-Jun

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 6
        assert period.end.day == 30

    def test_period_from_month_backward_cross_year(self):
        """Test from_month backward spanning year boundary."""
        period = Period.from_month(2024, 2, n_months=-3)  # Nov 2023 - Feb 2024

        assert period.start.year == 2023
        assert period.start.month == 12
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 2
        assert period.end.day == 29  # Leap year

    def test_period_from_month_with_n_years_forward(self):
        """Test from_month with n_years (forward)."""
        period = Period.from_month(2024, 1, n_years=2)  # Jan 2024 - Jan 2026

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2026
        assert period.end.month == 1
        assert period.end.day == 31

    def test_period_from_month_with_n_years_backward(self):
        """Test from_month with negative n_years (backward)."""
        # n_years=-2 with default n_months=1 means: 1 + (-2 * 12) = -23 months
        # From Dec 2024, backward 23 months = Feb 2023 to Dec 2024
        period = Period.from_month(2024, 12, n_years=-2)

        assert period.start.year == 2023
        assert period.start.month == 2
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 12
        assert period.end.day == 31

    def test_period_from_month_with_n_years_only_backward(self):
        """Test from_month with only n_years (no n_months override)."""
        # For exact 2 years back, need to set n_months to cancel the default
        # n_months=-1 + n_years=-2 = -1 + (-24) = -25 months
        # Better: Use n_months that gives clean year boundaries
        period = Period.from_month(2024, 1, n_months=-1, n_years=-2)  # Jan 2022 - Jan 2024

        assert period.start.year == 2022
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2024
        assert period.end.month == 1
        assert period.end.day == 31

    def test_period_from_month_combined_months_years(self):
        """Test from_month with both n_months and n_years."""
        period = Period.from_month(2024, 1, n_months=6, n_years=1)  # Jan 2024 - Jun 2025

        assert period.start.year == 2024
        assert period.start.month == 1
        assert period.start.day == 1
        assert period.end.year == 2025
        assert period.end.month == 6
        assert period.end.day == 30

    def test_period_from_month_combined_backward(self):
        """Test from_month with negative months and years."""
        period = Period.from_month(2024, 6, n_months=-3, n_years=-1)  # Mar 2023 - Jun 2024

        # -1 year = -12 months, -3 months = total -15 months backward from Jun 2024
        # End: Jun 2024, Start: 15 months back = Mar 2023
        assert period.start.year == 2023
        assert period.start.month == 4
        assert period.end.year == 2024
        assert period.end.month == 6

    def test_period_from_month_zero_duration_fails(self):
        """Test from_month fails with zero total duration."""
        with pytest.raises(ValueError, match="Total duration cannot be 0"):
            Period.from_month(2024, 1, n_months=-12, n_years=1)  # -12 + 12 = 0


class TestBacktestRequest:
    """Test BacktestRequest model."""

    @pytest.fixture
    def mock_strategy(self):
        """Create mock strategy config."""
        from tradepose_models.enums import TradeDirection, TrendType
        from tradepose_models.strategy.blueprint import Blueprint
        from tradepose_models.strategy.config import StrategyConfig

        # Create a minimal valid strategy config
        return StrategyConfig(
            name="test_strategy",
            base_instrument="BTCUSDT",
            base_freq="1h",
            note="test strategy",
            base_blueprint=Blueprint(
                name="test_blueprint",
                direction=TradeDirection.LONG,
                trend_type=TrendType.TREND,
                entry_first=True,
                note="test",
                entry_triggers=[],
                exit_triggers=[],
            ),
            volatility_indicator=None,
            advanced_blueprints=[],
            indicators=[],
        )

    def test_backtest_request_creation(self, mock_strategy):
        """Test creating request with Period objects."""
        periods = [
            Period(start="2021-01-01", end="2021-12-31"),
            Period(start="2022-01-01", end="2022-12-31"),
        ]

        request = BacktestRequest(strategies=[mock_strategy], periods=periods, cache=True)

        assert len(request.strategies) == 1
        assert len(request.periods) == 2
        assert request.cache is True
        assert all(isinstance(p, Period) for p in request.periods)

    def test_backtest_request_with_convenience_constructors(self, mock_strategy):
        """Test creating request with Period convenience constructors."""
        periods = [Period.Q1(2024), Period.Q2(2024), Period.Q3(2024)]

        request = BacktestRequest(strategies=[mock_strategy], periods=periods)

        assert len(request.periods) == 3
        assert all(isinstance(p, Period) for p in request.periods)
        assert request.periods[0].start.month == 1
        assert request.periods[1].start.month == 4
        assert request.periods[2].start.month == 7

    def test_backtest_request_validation_empty_strategies(self):
        """Test validation fails with empty strategies."""
        with pytest.raises(ValueError):
            BacktestRequest(strategies=[], periods=[Period(start="2021-01-01", end="2021-12-31")])

    def test_backtest_request_validation_empty_periods(self, mock_strategy):
        """Test validation fails with empty periods."""
        with pytest.raises(ValueError):
            BacktestRequest(strategies=[mock_strategy], periods=[])
