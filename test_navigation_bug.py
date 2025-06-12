#!/usr/bin/env python3
"""
Test script to reproduce the navigation bug where extra lines appear.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid, on_up_dual, on_down_dual
from src.config import config


def test_navigation_bug():
    """Test that reproduces the navigation bug."""
    print("Testing navigation bug...")
    
    # Load configuration and data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    # Create chart data instances
    chart_data1 = ChartsDailyData(dict_filename, data_filename)
    chart_data2 = ChartsDailyData(dict_filename, data_filename)
    
    # Create dual chart grid
    dual_chart = create_dual_chart_grid(chart_data1, chart_data2)
    
    # Get the right chart (subchart)
    # In the implementation, right_chart is created as a subchart
    # We need to access it to test the navigation
    
    print("Initial state: Charts created")
    
    # Simulate navigation - this should trigger the bug
    print("Simulating navigation up...")
    on_up_dual(dual_chart, dual_chart, chart_data1, chart_data2)  # This will fail because we don't have access to right_chart
    
    print("Navigation test completed")


def test_single_vs_dual_navigation():
    """Compare single chart vs dual chart navigation behavior."""
    print("Comparing single vs dual chart navigation...")
    
    # Load data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    chart_data = ChartsDailyData(dict_filename, data_filename)
    
    # Test single chart navigation
    from src.ui import create_and_bind_chart, on_up, on_down, on_timeframe_change
    single_chart = create_and_bind_chart(chart_data)
    
    print("Single chart created")
    print("Single chart navigation calls plot_indicators:", "plot_indicators" in str(on_up.__code__.co_names))
    
    # Test dual chart navigation  
    dual_chart = create_dual_chart_grid(chart_data)
    print("Dual chart created")
    print("Dual chart navigation calls plot_indicators:", "plot_indicators" in str(on_up_dual.__code__.co_names))
    print("Timeframe change calls plot_indicators:", "plot_indicators" in str(on_timeframe_change.__code__.co_names))
    
    print("Comparison completed")


if __name__ == "__main__":
    try:
        test_single_vs_dual_navigation()
        print("\n" + "="*50)
        test_navigation_bug()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()