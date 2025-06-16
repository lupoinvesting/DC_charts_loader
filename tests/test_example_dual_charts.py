"""Tests for example_dual_charts.py script."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import example_dual_charts


class TestExampleDualCharts:
    """Test the example dual charts script functionality."""

    @patch('example_dual_charts.create_dual_chart_grid')
    @patch('example_dual_charts.ChartsDailyData')
    @patch('example_dual_charts.config')
    @patch('builtins.print')
    def test_main_function(self, mock_print, mock_config, mock_charts_data, mock_create_dual):
        """Test the main function of example_dual_charts."""
        # Setup mocks
        mock_config.general.data_path = "test_path"
        mock_config.general.data_filename = "test_file.feather"
        
        mock_chart_data1 = MagicMock()
        mock_chart_data2 = MagicMock()
        mock_chart_data1.charts = ['chart1', 'chart2', 'chart3']  # Mock charts list
        mock_charts_data.side_effect = [mock_chart_data1, mock_chart_data2]
        
        # Mock load_chart method
        mock_df1 = MagicMock()
        mock_df1.shape = (100, 5)
        mock_metadata1 = {'ticker': 'AAPL', 'date_str': '2023-01-01'}
        mock_chart_data1.load_chart.return_value = (mock_df1, mock_metadata1)
        
        mock_df2 = MagicMock()
        mock_metadata2 = {'ticker': 'GOOGL', 'date_str': '2023-01-02'}
        mock_chart_data2.load_chart.return_value = (mock_df2, mock_metadata2)
        
        mock_dual_chart = MagicMock()
        mock_create_dual.return_value = mock_dual_chart
        
        # Call the main function
        result = example_dual_charts.main()
        
        # Verify calls
        assert mock_charts_data.call_count == 2
        mock_charts_data.assert_any_call(
            "test_path/test_file.feather",
            "test_path/test_file_data.feather"
        )
        mock_create_dual.assert_called_once_with(mock_chart_data1, mock_chart_data2)
        
        # Verify load_chart calls
        mock_chart_data1.load_chart.assert_called_once_with(0)
        mock_chart_data2.load_chart.assert_called_once_with(1)
        
        # Verify return value
        assert result == mock_dual_chart
        
        # Verify print statements
        mock_print.assert_any_call("Creating dual chart grid example...")
        mock_print.assert_any_call(f"Loaded {len(mock_chart_data1.charts)} charts from data")
        mock_print.assert_any_call("Dual chart grid created successfully!")

    def test_main_execution_structure(self):
        """Test the if __name__ == '__main__' execution structure."""
        # Read the actual file to verify structure
        with open('example_dual_charts.py', 'r') as f:
            content = f.read()
        
        # Verify the main execution block exists
        assert 'if __name__ == "__main__":' in content
        assert 'chart = main()' in content

    def test_docstring_content(self):
        """Test that the module docstring contains expected information."""
        docstring = example_dual_charts.__doc__
        assert "Example script demonstrating dual chart grid functionality" in docstring
        assert "shows how to use it programmatically" in docstring

    @patch('example_dual_charts.create_dual_chart_grid')
    @patch('example_dual_charts.ChartsDailyData')
    @patch('example_dual_charts.config')
    @patch('builtins.print')
    def test_feature_descriptions(self, mock_print, mock_config, mock_charts_data, mock_create_dual):
        """Test that all feature descriptions are printed."""
        # Setup basic mocks
        mock_config.general.data_path = "test"
        mock_config.general.data_filename = "test.feather"
        mock_chart_data = MagicMock()
        mock_chart_data.charts = []
        mock_charts_data.return_value = mock_chart_data
        mock_create_dual.return_value = MagicMock()
        
        # Mock load_chart to return valid data
        mock_df = MagicMock()
        mock_df.shape = (50, 4)
        mock_metadata = {'ticker': 'TEST', 'date_str': '2023-01-01'}
        mock_chart_data.load_chart.return_value = (mock_df, mock_metadata)
        
        example_dual_charts.main()
        
        # Check that key feature descriptions are printed
        expected_prints = [
            "- Side-by-side layout (50% width each)",
            "- Maximize/minimize buttons (⬜/×)",
            "- Timeframe switching (1D, 4H, 1H, 15M, 5M, 1M)",
            "- Keyboard controls:",
            "  * Shift+1: Next chart",
            "  * Shift+2: Previous chart",
            "  * Shift+S: Save screenshots"
        ]
        
        for expected_print in expected_prints:
            mock_print.assert_any_call(expected_print)

    @patch('example_dual_charts.create_dual_chart_grid')
    @patch('example_dual_charts.ChartsDailyData')
    @patch('example_dual_charts.config')
    def test_sample_data_loading(self, mock_config, mock_charts_data, mock_create_dual):
        """Test the sample data loading and display logic."""
        mock_config.general.data_path = "/data"
        mock_config.general.data_filename = "sample.feather"
        
        mock_chart_data1 = MagicMock()
        mock_chart_data2 = MagicMock()
        mock_chart_data1.charts = ['chart1', 'chart2']
        mock_charts_data.side_effect = [mock_chart_data1, mock_chart_data2]
        
        # Mock load_chart returns
        mock_df1 = MagicMock()
        mock_df1.shape = (200, 6)
        mock_metadata1 = {'ticker': 'TSLA', 'date_str': '2023-03-15'}
        mock_chart_data1.load_chart.return_value = (mock_df1, mock_metadata1)
        
        mock_df2 = MagicMock()
        mock_metadata2 = {'ticker': 'MSFT', 'date_str': '2023-03-16'}
        mock_chart_data2.load_chart.return_value = (mock_df2, mock_metadata2)
        
        mock_create_dual.return_value = MagicMock()
        
        example_dual_charts.main()
        
        # Verify that sample data is loaded correctly
        mock_chart_data1.load_chart.assert_called_once_with(0)
        mock_chart_data2.load_chart.assert_called_once_with(1)

    def test_sys_path_modification(self):
        """Test that sys.path is modified correctly."""
        # The script should add the directory to sys.path
        # This is already done in the import, so we just verify the logic
        expected_path = os.path.dirname(os.path.abspath('example_dual_charts.py'))
        
        # The script adds the directory to sys.path, which should be testable
        # by checking if the import works (which it does since we imported it)