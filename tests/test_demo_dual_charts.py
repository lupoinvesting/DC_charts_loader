"""Tests for demo_dual_charts.py script."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import demo_dual_charts


class TestDemoDualCharts:
    """Test the demo dual charts script functionality."""

    @patch('demo_dual_charts.create_dual_chart_grid')
    @patch('demo_dual_charts.ChartsDailyData')
    @patch('demo_dual_charts.config')
    @patch('builtins.print')
    def test_main_function(self, mock_print, mock_config, mock_charts_data, mock_create_dual):
        """Test the main function of demo_dual_charts."""
        # Setup mocks
        mock_config.general.data_path = "test_path"
        mock_config.general.data_filename = "test_file.feather"
        
        mock_chart_data1 = MagicMock()
        mock_chart_data2 = MagicMock()
        mock_charts_data.side_effect = [mock_chart_data1, mock_chart_data2]
        
        mock_dual_chart = MagicMock()
        mock_create_dual.return_value = mock_dual_chart
        
        # Call the main function
        demo_dual_charts.main()
        
        # Verify calls
        assert mock_charts_data.call_count == 2
        mock_charts_data.assert_any_call(
            "test_path/test_file.feather",
            "test_path/test_file_data.feather"
        )
        mock_create_dual.assert_called_once_with(mock_chart_data1, mock_chart_data2)
        mock_dual_chart.show.assert_called_once_with(block=True)
        
        # Verify print statements
        mock_print.assert_any_call("Loading dual chart grid demo...")
        mock_print.assert_any_call("Dual chart grid created successfully!")
        mock_print.assert_any_call("Use the controls mentioned above to interact with the charts.")

    def test_main_execution_structure(self):
        """Test the if __name__ == '__main__' execution structure."""
        # Read the actual file to verify structure
        with open('demo_dual_charts.py', 'r') as f:
            content = f.read()
        
        # Verify the main execution block exists
        assert 'if __name__ == "__main__":' in content
        assert 'main()' in content

    def test_docstring_content(self):
        """Test that the module docstring contains expected information."""
        docstring = demo_dual_charts.__doc__
        assert "Demo script for dual chart grid functionality" in docstring
        assert "Shift+1: Navigate to next chart" in docstring
        assert "Shift+2: Navigate to previous chart" in docstring
        assert "Shift+S: Save screenshots" in docstring

    @patch('demo_dual_charts.create_dual_chart_grid')
    @patch('demo_dual_charts.ChartsDailyData')
    @patch('demo_dual_charts.config')
    def test_data_loading_logic(self, mock_config, mock_charts_data, mock_create_dual):
        """Test the data loading and filename processing logic."""
        mock_config.general.data_path = "/test/path"
        mock_config.general.data_filename = "sample.feather"
        
        mock_chart_data = MagicMock()
        mock_charts_data.return_value = mock_chart_data
        mock_dual_chart = MagicMock()
        mock_create_dual.return_value = mock_dual_chart
        
        demo_dual_charts.main()
        
        # Verify the filename processing
        expected_dict_filename = "/test/path/sample.feather"
        expected_data_filename = "/test/path/sample_data.feather"
        
        mock_charts_data.assert_any_call(expected_dict_filename, expected_data_filename)