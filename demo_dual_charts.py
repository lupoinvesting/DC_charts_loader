#!/usr/bin/env python3
"""
Demo script for dual chart grid functionality.

This script demonstrates the new dual chart grid feature with:
- Side-by-side chart layout
- Maximize/minimize buttons for each chart
- Timeframe switching capabilities
- Navigation hotkeys
- Screenshot functionality

Usage:
    python demo_dual_charts.py

Controls:
    - Shift+1: Navigate to next chart
    - Shift+2: Navigate to previous chart
    - Shift+S: Save screenshots of both charts
    - Click maximize button (⬜) to maximize a chart
    - Click minimize button (×) to restore side-by-side view
    - Use timeframe dropdown to switch between 1D, 4H, 1H, 15M, 5M, 1M
"""

from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid
from src.config import config


def main():
    """Main function to run the dual chart demo."""
    print("Loading dual chart grid demo...")
    print(__doc__)
    
    # Load configuration and data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    # Create chart data instances
    chart_data1 = ChartsDailyData(dict_filename, data_filename)
    chart_data2 = ChartsDailyData(dict_filename, data_filename)
    
    # Create dual chart grid
    # You can pass the same data to both charts or different data sources
    dual_chart = create_dual_chart_grid(chart_data1, chart_data2)
    
    print("Dual chart grid created successfully!")
    print("Use the controls mentioned above to interact with the charts.")
    
    # Show the chart (blocking call)
    dual_chart.show(block=True)


if __name__ == "__main__":
    main()