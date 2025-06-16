"""Tests for demo_dual_charts_minute.py script."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import demo_dual_charts_minute


class TestDemoDualChartsMinute:
    """Test the demo dual charts minute script functionality."""

    @patch('demo_dual_charts_minute.create_dual_chart_grid')
    @patch('demo_dual_charts_minute.ChartsDailyData')
    @patch('builtins.print')
    def test_main_function(self, mock_print, mock_charts_data, mock_create_dual):
        """Test the main function of demo_dual_charts_minute."""
        # Setup mocks
        mock_daily_data = MagicMock()
        mock_charts_data.return_value = mock_daily_data
        
        mock_chart = MagicMock()
        mock_create_dual.return_value = mock_chart
        
        # Call the main function
        demo_dual_charts_minute.main()
        
        # Verify calls
        mock_charts_data.assert_called_once_with(
            dict_filename="data/default.feather",
            data_filename="data/default_data.feather"
        )
        mock_create_dual.assert_called_once_with(mock_daily_data)
        mock_chart.show.assert_called_once_with(block=True)
        
        # Verify print statements
        mock_print.assert_any_call("Loading dual chart demo with minute data...")
        mock_print.assert_any_call("Dual chart grid created!")
        mock_print.assert_any_call("\nFeatures:")
        mock_print.assert_any_call("- Left chart: Daily data (1D timeframe)")
        mock_print.assert_any_call("- Right chart: Minute data (1M timeframe by default)")

    def test_main_execution_structure(self):
        """Test the if __name__ == '__main__' execution structure."""
        # Read the actual file to verify structure
        with open('demo_dual_charts_minute.py', 'r') as f:
            content = f.read()
        
        # Verify the main execution block exists
        assert 'if __name__ == "__main__":' in content
        assert 'main()' in content

    def test_docstring_content(self):
        """Test that the module docstring contains expected information."""
        docstring = demo_dual_charts_minute.__doc__
        assert "Demo script showing the dual chart functionality with minute data" in docstring
        assert "Left chart: Daily data from default.feather" in docstring
        assert "Right chart: Minute data from default_min.feather" in docstring

    @patch('demo_dual_charts_minute.create_dual_chart_grid')
    @patch('demo_dual_charts_minute.ChartsDailyData')
    def test_hardcoded_filenames(self, mock_charts_data, mock_create_dual):
        """Test that the script uses hardcoded filenames correctly."""
        mock_daily_data = MagicMock()
        mock_charts_data.return_value = mock_daily_data
        mock_chart = MagicMock()
        mock_create_dual.return_value = mock_chart
        
        demo_dual_charts_minute.main()
        
        # Verify the hardcoded filenames are used
        mock_charts_data.assert_called_once_with(
            dict_filename="data/default.feather",
            data_filename="data/default_data.feather"
        )

    @patch('demo_dual_charts_minute.create_dual_chart_grid')
    @patch('demo_dual_charts_minute.ChartsDailyData')
    @patch('builtins.print')
    def test_feature_descriptions(self, mock_print, mock_charts_data, mock_create_dual):
        """Test that all feature descriptions are printed."""
        mock_charts_data.return_value = MagicMock()
        mock_create_dual.return_value = MagicMock()
        
        demo_dual_charts_minute.main()
        
        # Check that key feature descriptions are printed
        expected_prints = [
            "- Timeframe switching: Use dropdown to change display timeframes",
            "- Navigation: Shift+1 (next), Shift+2 (previous)",
            "- Screenshots: Shift+S",
            "- Maximize/Minimize: Click the ⬜ button on each chart"
        ]
        
        for expected_print in expected_prints:
            mock_print.assert_any_call(expected_print)
        
        # Check for the specific print about min.feather files
        mock_print.assert_any_call("\nThe right chart loads data from files ending with '_min.feather'")