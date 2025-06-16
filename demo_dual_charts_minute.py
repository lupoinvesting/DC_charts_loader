#!/usr/bin/env python3
"""
Demo script showing the dual chart functionality with minute data.

This script demonstrates:
1. Left chart: Daily data from default.feather
2. Right chart: Minute data from default_min.feather (automatically loaded)
3. Timeframe switching functionality
4. Navigation and screenshot capabilities
"""

from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid
import numpy


def main():
    """Main demo function."""
    print("Loading dual chart demo with minute data...")

    # Create daily data for the left chart
    daily_data = ChartsDailyData(
        dict_filename="data/default.feather", data_filename="data/default_data.feather"
    )

    # Create dual chart grid - right chart will automatically load minute data
    chart = create_dual_chart_grid(daily_data)

    print("Dual chart grid created!")
    print("\nFeatures:")
    print("- Left chart: Daily data (1D timeframe)")
    print("- Right chart: Minute data (1M timeframe by default)")
    print("- Timeframe switching: Use dropdown to change display timeframes")
    print("- Navigation: Shift+1 (next), Shift+2 (previous)")
    print("- Screenshots: Shift+S")
    print("- Maximize/Minimize: Click the ⬜ button on each chart")
    print("\nThe right chart loads data from files ending with '_min.feather'")
    print(
        "Timeframe switching on the right chart changes display only, not data source"
    )

    # Show the chart
    chart.show(block=True)


if __name__ == "__main__":
    main()
