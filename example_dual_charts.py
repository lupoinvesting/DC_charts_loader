#!/usr/bin/env python3
"""
Example script demonstrating dual chart grid functionality.

This script creates the dual chart setup and shows how to use it programmatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid
from src.config import config


def main():
    """Example of creating and configuring dual charts."""
    print("Creating dual chart grid example...")
    
    # Load configuration and data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    # Create chart data instances
    chart_data1 = ChartsDailyData(dict_filename, data_filename)
    chart_data2 = ChartsDailyData(dict_filename, data_filename)
    
    print(f"Loaded {len(chart_data1.charts)} charts from data")
    
    # Create dual chart grid
    dual_chart = create_dual_chart_grid(chart_data1, chart_data2)
    
    print("Dual chart grid created successfully!")
    print("\nFeatures available:")
    print("- Side-by-side layout (50% width each)")
    print("- Maximize/minimize buttons (⬜/×)")
    print("- Timeframe switching (1D, 4H, 1H, 15M, 5M, 1M)")
    print("- Keyboard controls:")
    print("  * Shift+1: Next chart")
    print("  * Shift+2: Previous chart")
    print("  * Shift+S: Save screenshots")
    
    # Get some sample data to show what's loaded
    df1, metadata1 = chart_data1.load_chart(0)
    df2, metadata2 = chart_data2.load_chart(1)
    
    print(f"\nSample data loaded:")
    print(f"Chart 1: {metadata1['ticker']} on {metadata1['date_str']}")
    print(f"Chart 2: {metadata2['ticker']} on {metadata2['date_str']}")
    print(f"Data shape: {df1.shape}")
    
    # In a real application, you would call:
    # dual_chart.show(block=True)
    
    print("\nTo run the interactive version, use:")
    print("python demo_dual_charts.py")
    
    return dual_chart


if __name__ == "__main__":
    chart = main()
    print("\nExample completed successfully!")