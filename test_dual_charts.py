#!/usr/bin/env python3
"""
Test script for dual chart grid functionality.

This script tests the dual chart implementation without showing the UI.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid
from src.config import config


def test_dual_chart_creation():
    """Test that dual chart grid can be created successfully."""
    try:
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
        
        print("✓ Dual chart grid created successfully!")
        print(f"✓ Main chart type: {type(dual_chart)}")
        print(f"✓ Chart data 1 loaded: {len(chart_data1.charts)} charts")
        print(f"✓ Chart data 2 loaded: {len(chart_data2.charts)} charts")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating dual chart grid: {e}")
        return False


def test_single_data_source():
    """Test dual chart with single data source."""
    try:
        # Load configuration and data
        path = config.general.data_path
        filename = config.general.data_filename
        dict_filename = f"{path}/{filename}"
        data_filename = dict_filename.replace(".feather", "_data.feather")
        
        # Create chart data instance
        chart_data = ChartsDailyData(dict_filename, data_filename)
        
        # Create dual chart grid with single data source
        dual_chart = create_dual_chart_grid(chart_data)
        
        print("✓ Dual chart grid with single data source created successfully!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating dual chart with single data source: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing dual chart grid functionality...\n")
    
    tests = [
        ("Dual chart creation", test_dual_chart_creation),
        ("Single data source", test_single_data_source),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running test: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())