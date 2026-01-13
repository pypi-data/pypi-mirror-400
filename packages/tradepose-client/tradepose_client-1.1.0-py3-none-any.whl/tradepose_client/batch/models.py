"""Pydantic models for batch testing API."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from tradepose_models.strategy.config import StrategyConfig


class Period(BaseModel):
    """
    Time period definition for backtesting.

    Supports multiple input formats:
    - String: "2021-01-01" or "2021-01-01T00:00:00"
    - date: date(2021, 1, 1)
    - datetime: datetime(2021, 1, 1, 0, 0, 0)

    Validation:
    - Ensures start date is before end date
    - Converts all inputs to datetime objects

    Examples:
        >>> # Direct construction
        >>> period = Period(start="2024-01-01", end="2024-12-31")

        >>> # Convenience constructors
        >>> q1 = Period.Q1(2024)  # 2024-01-01 to 2024-03-31
        >>> year = Period.from_year(2024)  # Full year
        >>> month = Period.from_month(2024, 3)  # March 2024
    """

    start: datetime | date | str = Field(..., description="Period start time")
    end: datetime | date | str = Field(..., description="Period end time")

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Auto-parse string, date, or datetime to datetime object."""
        if isinstance(v, str):
            # Handle both "2021-01-01" and "2021-01-01T00:00:00" formats
            # Remove timezone suffix if present
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        elif isinstance(v, date) and not isinstance(v, datetime):
            # Convert date to datetime (midnight)
            return datetime.combine(v, datetime.min.time())
        elif isinstance(v, datetime):
            return v
        else:
            raise ValueError(f"Cannot parse datetime from type {type(v)}: {v}")

    @model_validator(mode="after")
    def validate_period_order(self) -> "Period":
        """Ensure start date is before end date."""
        # Convert to datetime for comparison
        start_dt = self.start if isinstance(self.start, datetime) else self.start
        end_dt = self.end if isinstance(self.end, datetime) else self.end

        if start_dt >= end_dt:
            raise ValueError(
                f"Period start ({start_dt.date()}) must be before end ({end_dt.date()})"
            )

        return self

    def to_iso(self) -> tuple[str, str]:
        """Convert to ISO format strings for API requests."""
        # Ensure start and end are datetime objects
        start_dt = self.start if isinstance(self.start, datetime) else self.start
        end_dt = self.end if isinstance(self.end, datetime) else self.end

        return (
            start_dt.isoformat(),
            end_dt.isoformat(),
        )

    def to_key(self) -> str:
        """Generate unique key for this period (e.g., '2021-01-01_2021-12-31')."""
        start_dt = self.start if isinstance(self.start, datetime) else self.start
        end_dt = self.end if isinstance(self.end, datetime) else self.end

        return f"{start_dt.date().isoformat()}_{end_dt.date().isoformat()}"

    @classmethod
    def Q1(cls, year: int) -> "Period":
        """
        Create a Period for Q1 (January - March).

        Args:
            year: The year (e.g., 2024)

        Returns:
            Period covering Q1 of the specified year

        Example:
            >>> q1 = Period.Q1(2024)  # 2024-01-01 to 2024-03-31
        """
        return cls(start=f"{year}-01-01", end=f"{year}-03-31")

    @classmethod
    def Q2(cls, year: int) -> "Period":
        """
        Create a Period for Q2 (April - June).

        Args:
            year: The year (e.g., 2024)

        Returns:
            Period covering Q2 of the specified year

        Example:
            >>> q2 = Period.Q2(2024)  # 2024-04-01 to 2024-06-30
        """
        return cls(start=f"{year}-04-01", end=f"{year}-06-30")

    @classmethod
    def Q3(cls, year: int) -> "Period":
        """
        Create a Period for Q3 (July - September).

        Args:
            year: The year (e.g., 2024)

        Returns:
            Period covering Q3 of the specified year

        Example:
            >>> q3 = Period.Q3(2024)  # 2024-07-01 to 2024-09-30
        """
        return cls(start=f"{year}-07-01", end=f"{year}-09-30")

    @classmethod
    def Q4(cls, year: int) -> "Period":
        """
        Create a Period for Q4 (October - December).

        Args:
            year: The year (e.g., 2024)

        Returns:
            Period covering Q4 of the specified year

        Example:
            >>> q4 = Period.Q4(2024)  # 2024-10-01 to 2024-12-31
        """
        return cls(start=f"{year}-10-01", end=f"{year}-12-31")

    @classmethod
    def from_year(cls, year: int, n_years: int = 1) -> "Period":
        """
        Create a Period covering one or more years.

        Args:
            year: The starting year (e.g., 2024)
            n_years: Number of years to span (default: 1). Negative values go backward.

        Returns:
            Period covering n years

        Raises:
            ValueError: If n_years is 0

        Examples:
            >>> # Single year
            >>> year_2024 = Period.from_year(2024)  # 2024-01-01 to 2024-12-31

            >>> # Multiple years forward
            >>> three_years = Period.from_year(2024, n_years=3)  # 2024-01-01 to 2026-12-31

            >>> # Backward (lookback)
            >>> lookback = Period.from_year(2024, n_years=-2)  # 2023-01-01 to 2024-12-31

            >>> # Five year trend
            >>> long_term = Period.from_year(2020, n_years=5)  # 2020-01-01 to 2024-12-31
        """
        if n_years == 0:
            raise ValueError("n_years cannot be 0")

        if n_years > 0:
            # Forward: start from beginning of year, span forward
            start_year = year
            end_year = year + n_years - 1
        else:
            # Backward: end at end of year, span backward
            end_year = year
            start_year = year + n_years + 1

        return cls(start=f"{start_year}-01-01", end=f"{end_year}-12-31")

    @classmethod
    def from_month(cls, year: int, month: int, n_months: int = 1, n_years: int = 0) -> "Period":
        """
        Create a Period starting from a specific month, spanning n months and n years.

        Args:
            year: The year (e.g., 2024)
            month: The starting month (1-12)
            n_months: Number of months to span (default: 1). Negative values go backward.
            n_years: Number of years to add (default: 0). Negative values go backward.

        Returns:
            Period covering the specified time range

        Raises:
            ValueError: If month is not between 1 and 12
            ValueError: If n_months is 0
            ValueError: If both n_months and n_years result in zero duration

        Examples:
            >>> # Single month
            >>> march = Period.from_month(2024, 3)  # 2024-03-01 to 2024-03-31

            >>> # Forward: Three months starting from March
            >>> forward_3m = Period.from_month(2024, 3, n_months=3)  # 2024-03-01 to 2024-05-31

            >>> # Backward: Three months ending at March
            >>> backward_3m = Period.from_month(2024, 3, n_months=-3)  # 2024-01-01 to 2024-03-31

            >>> # Forward with years: 1 year + 6 months
            >>> long_period = Period.from_month(2024, 1, n_months=6, n_years=1)  # 2024-01-01 to 2025-06-30

            >>> # Backward with years: 2 years back
            >>> lookback = Period.from_month(2024, 12, n_years=-2)  # 2022-12-01 to 2024-12-31

            >>> # Complex: 1 year back + 3 months forward from that point
            >>> complex_range = Period.from_month(2024, 6, n_months=3, n_years=-1)  # 2023-06-01 to 2023-08-31
        """
        if not 1 <= month <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {month}")

        if n_months == 0:
            raise ValueError("n_months cannot be 0 (use n_years for year-only ranges)")

        # Calculate total months including years
        total_months = n_months + (n_years * 12)

        if total_months == 0:
            raise ValueError(f"Total duration cannot be 0 (n_months={n_months}, n_years={n_years})")

        # Determine direction
        if total_months > 0:
            # Forward: start from beginning of month, span forward
            start_year = year
            start_month = month

            # Calculate end date
            end_month = start_month + total_months - 1
            end_year = start_year

            # Handle month overflow
            while end_month > 12:
                end_month -= 12
                end_year += 1
            while end_month < 1:
                end_month += 12
                end_year -= 1

            start_date = date(start_year, start_month, 1)

            # Calculate last day of end month
            if end_month in [1, 3, 5, 7, 8, 10, 12]:
                last_day = 31
            elif end_month in [4, 6, 9, 11]:
                last_day = 30
            else:  # February
                is_leap = (end_year % 4 == 0 and end_year % 100 != 0) or (end_year % 400 == 0)
                last_day = 29 if is_leap else 28

            end_date = date(end_year, end_month, last_day)

        else:
            # Backward: end at end of month, span backward
            end_year = year
            end_month = month

            # Calculate start date
            start_month = end_month + total_months + 1  # +1 because backward
            start_year = end_year

            # Handle month underflow
            while start_month < 1:
                start_month += 12
                start_year -= 1
            while start_month > 12:
                start_month -= 12
                start_year += 1

            start_date = date(start_year, start_month, 1)

            # Calculate last day of end month
            if end_month in [1, 3, 5, 7, 8, 10, 12]:
                last_day = 31
            elif end_month in [4, 6, 9, 11]:
                last_day = 30
            else:  # February
                is_leap = (end_year % 4 == 0 and end_year % 100 != 0) or (end_year % 400 == 0)
                last_day = 29 if is_leap else 28

            end_date = date(end_year, end_month, last_day)

        return cls(start=start_date.isoformat(), end=end_date.isoformat())


class BacktestRequest(BaseModel):
    """
    Batch backtest request containing strategies and periods.

    This model validates user input for batch testing operations.
    All periods must be Period objects for type safety.

    Example:
        >>> from tradepose_client.batch import Period
        >>> request = BacktestRequest(
        ...     strategies=[my_strategy],
        ...     periods=[Period.Q1(2024), Period.Q2(2024)]
        ... )
    """

    strategies: list[StrategyConfig] = Field(
        ..., description="List of strategy configurations to backtest", min_length=1
    )
    periods: list[Period] = Field(
        ..., description="List of Period objects defining test ranges", min_length=1
    )
    cache: bool = Field(default=True, description="Enable result caching")
