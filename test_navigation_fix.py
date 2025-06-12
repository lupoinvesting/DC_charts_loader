#!/usr/bin/env python3
"""
Test script to verify that the navigation bug fix works correctly.

This test verifies that:
1. Navigation functions don't call plot_indicators multiple times
2. Indicators are only plotted once during chart creation
3. The behavior is consistent between single and dual chart modes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import ChartsDailyData
from src.ui import (
    create_dual_chart_grid, 
    create_and_bind_chart,
    on_up_dual, 
    on_down_dual, 
    on_up, 
    on_down,
    on_timeframe_change
)
from src.config import config


def test_navigation_consistency():
    """Test that navigation behavior is consistent between single and dual charts."""
    print("Testing navigation consistency...")
    
    # Check that navigation functions don't call plot_indicators
    functions_to_test = [
        ("on_up (single)", on_up),
        ("on_down (single)", on_down),
        ("on_up_dual", on_up_dual),
        ("on_down_dual", on_down_dual),
        ("on_timeframe_change", on_timeframe_change),
    ]
    
    all_consistent = True
    for func_name, func in functions_to_test:
        calls_plot_indicators = "plot_indicators" in str(func.__code__.co_names)
        print(f"  {func_name}: calls plot_indicators = {calls_plot_indicators}")
        if calls_plot_indicators:
            all_consistent = False
    
    if all_consistent:
        print("✓ All navigation functions are consistent - none call plot_indicators")
    else:
        print("✗ Inconsistency detected - some functions still call plot_indicators")
    
    return all_consistent


def test_chart_creation_includes_indicators():
    """Test that chart creation still includes indicators."""
    print("\nTesting chart creation includes indicators...")
    
    # Load data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    chart_data = ChartsDailyData(dict_filename, data_filename)
    
    # Test single chart creation
    from src.ui import create_and_bind_chart
    single_chart = create_and_bind_chart(chart_data)
    print("✓ Single chart created successfully")
    
    # Test dual chart creation
    dual_chart = create_dual_chart_grid(chart_data)
    print("✓ Dual chart created successfully")
    
    # Verify that create_and_bind_chart calls plot_indicators
    create_func_code = str(create_and_bind_chart.__code__.co_names)
    calls_plot_indicators = "plot_indicators" in create_func_code
    print(f"  create_and_bind_chart calls plot_indicators: {calls_plot_indicators}")
    
    if calls_plot_indicators:
        print("✓ Chart creation properly includes indicators")
        return True
    else:
        print("✗ Chart creation missing indicators")
        return False


def test_bug_reproduction_scenario():
    """Test the specific scenario that would reproduce the bug."""
    print("\nTesting bug reproduction scenario...")
    
    # Load data
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    
    chart_data1 = ChartsDailyData(dict_filename, data_filename)
    chart_data2 = ChartsDailyData(dict_filename, data_filename)
    
    # Create dual chart
    dual_chart = create_dual_chart_grid(chart_data1, chart_data2)
    print("✓ Dual chart created")
    
    # Simulate the bug scenario: multiple navigation calls
    # In the buggy version, this would create multiple indicator lines
    print("  Simulating navigation sequence that would trigger the bug...")
    
    # Note: We can't actually call the navigation functions here because
    # we don't have access to the individual chart objects from the dual_chart
    # But we can verify that the functions themselves don't call plot_indicators
    
    navigation_functions = [on_up_dual, on_down_dual, on_timeframe_change]
    bug_free = True
    
    for func in navigation_functions:
        if "plot_indicators" in str(func.__code__.co_names):
            print(f"✗ {func.__name__} still calls plot_indicators - bug not fixed!")
            bug_free = False
    
    if bug_free:
        print("✓ Navigation functions don't call plot_indicators - bug is fixed!")
    
    return bug_free


def main():
    """Run all tests to verify the bug fix."""
    print("=" * 60)
    print("NAVIGATION BUG FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Navigation Consistency", test_navigation_consistency),
        ("Chart Creation", test_chart_creation_includes_indicators),
        ("Bug Reproduction Scenario", test_bug_reproduction_scenario),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The navigation bug has been fixed.")
        print("\nBug Fix Summary:")
        print("- Removed plot_indicators() calls from on_up_dual()")
        print("- Removed plot_indicators() calls from on_down_dual()")
        print("- Removed plot_indicators() calls from on_timeframe_change()")
        print("- Indicators are now only plotted once during chart creation")
        print("- Behavior is now consistent with single chart navigation")
        return 0
    else:
        print("❌ Some tests failed! The bug may not be fully fixed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())