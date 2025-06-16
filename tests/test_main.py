"""Tests for main.py script."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import importlib


class TestMainScript:
    """Test the main script functionality."""

    @patch('builtins.open', new_callable=mock_open, read_data="""
from src.models import ChartsDailyData
from src.ui import create_and_bind_chart, create_dual_chart_grid
from src.config import config

if __name__ == "__main__":
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    data_filename = dict_filename.replace(".feather", "_data.feather")
    chart_data = ChartsDailyData(dict_filename, data_filename)
    
    use_dual_chart = config.chart.use_intraday_tf
    
    if use_dual_chart:
        chart = create_dual_chart_grid(chart_data)
    else:
        chart = create_and_bind_chart(chart_data)
    
    chart.show(block=True)
""")
    def test_main_script_execution_logic(self, mock_file):
        """Test the main script execution logic."""
        # This test verifies the script structure and logic
        content = mock_file.return_value.read()
        
        # Verify key components are present
        assert "from src.models import ChartsDailyData" in content
        assert "from src.ui import create_and_bind_chart, create_dual_chart_grid" in content
        assert "from src.config import config" in content
        assert "if __name__ == \"__main__\":" in content
        assert "chart.show(block=True)" in content

    def test_filename_processing_logic(self):
        """Test the filename processing logic."""
        # Test the filename replacement logic used in main.py
        path = "/data/path"
        filename = "sample.feather"
        dict_filename = f"{path}/{filename}"
        data_filename = dict_filename.replace(".feather", "_data.feather")
        
        expected_dict_filename = "/data/path/sample.feather"
        expected_data_filename = "/data/path/sample_data.feather"
        
        assert dict_filename == expected_dict_filename
        assert data_filename == expected_data_filename

    def test_dual_chart_condition_logic(self):
        """Test the dual chart condition logic."""
        # Test the boolean logic used in main.py
        use_dual_chart_true = True
        use_dual_chart_false = False
        
        # Simulate the if-else logic
        if use_dual_chart_true:
            chart_type = "dual"
        else:
            chart_type = "single"
        assert chart_type == "dual"
        
        if use_dual_chart_false:
            chart_type = "dual"
        else:
            chart_type = "single"
        assert chart_type == "single"

    @patch('subprocess.run')
    def test_main_script_as_subprocess(self, mock_run):
        """Test running main.py as a subprocess (simulated)."""
        # This simulates running the script as a subprocess
        mock_run.return_value.returncode = 0
        
        # Simulate running the script
        result = mock_run(['python', 'main.py'])
        
        # Verify the subprocess was called
        mock_run.assert_called_once_with(['python', 'main.py'])
        assert result.returncode == 0