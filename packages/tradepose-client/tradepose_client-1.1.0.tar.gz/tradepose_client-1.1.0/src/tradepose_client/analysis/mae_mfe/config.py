"""Configuration classes for MAE/MFE analysis charts."""

from __future__ import annotations

from dataclasses import dataclass

from .types import ThemeType


@dataclass
class ChartConfig:
    """Configuration for chart appearance and behavior.

    Attributes:
        width: Chart width in pixels.
        height: Chart height in pixels.
        theme: Plotly theme template name.
        title_font_size: Font size for chart titles.
        show_legend: Whether to display the legend.
        color_winner: Color for winning trades.
        color_loser: Color for losing trades.
        color_long: Color for long trades.
        color_short: Color for short trades.
        marker_size: Default marker size for scatter plots.
        marker_opacity: Default marker opacity.
        line_width: Default line width.
    """

    width: int = 1000
    height: int = 600
    theme: ThemeType = "plotly"
    title_font_size: int = 16
    show_legend: bool = True

    # Color scheme
    color_winner: str = "#26A69A"  # Teal green
    color_loser: str = "#EF5350"  # Red
    color_long: str = "#42A5F5"  # Blue
    color_short: str = "#AB47BC"  # Purple
    color_neutral: str = "#78909C"  # Blue grey

    # Marker settings
    marker_size: int = 8
    marker_opacity: float = 0.6

    # Line settings
    line_width: int = 2

    def get_pnl_colors(self) -> dict[str, str]:
        """Get color mapping for PnL-based coloring."""
        return {
            "winner": self.color_winner,
            "loser": self.color_loser,
        }

    def get_direction_colors(self) -> dict[int, str]:
        """Get color mapping for direction-based coloring."""
        return {
            1: self.color_long,
            -1: self.color_short,
        }


@dataclass
class DashboardConfig:
    """Configuration for dashboard layout.

    Attributes:
        rows: Number of rows in the dashboard grid.
        cols: Number of columns in the dashboard grid.
        horizontal_spacing: Spacing between columns (0-1).
        vertical_spacing: Spacing between rows (0-1).
        height_per_row: Height per row in pixels.
    """

    rows: int = 3
    cols: int = 3
    horizontal_spacing: float = 0.08
    vertical_spacing: float = 0.10
    height_per_row: int = 350


# Default chart configuration
DEFAULT_CONFIG = ChartConfig()

# Dark theme configuration
DARK_CONFIG = ChartConfig(
    theme="plotly_dark",
    color_winner="#4CAF50",
    color_loser="#F44336",
    color_long="#2196F3",
    color_short="#9C27B0",
)
