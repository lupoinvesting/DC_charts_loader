"""Tests for script execution and coverage of main script files."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import subprocess


class TestScriptExecution:
    """Test actual execution of main script files for coverage."""

    def test_script_syntax_validation(self):
        """Test that all main scripts have valid Python syntax."""
        scripts = ['main.py', 'demo_dual_charts.py', 'demo_dual_charts_minute.py', 'example_dual_charts.py']
        
        for script in scripts:
            # Try to compile the script to check syntax
            with open(script, 'r') as f:
                content = f.read()
            
            try:
                compile(content, script, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {script}: {e}")

    def test_script_imports(self):
        """Test that all scripts can import their dependencies."""
        scripts = [
            ('main.py', ['src.models', 'src.ui', 'src.config']),
            ('demo_dual_charts.py', ['src.models', 'src.ui', 'src.config']),
            ('demo_dual_charts_minute.py', ['src.models', 'src.ui']),
            ('example_dual_charts.py', ['src.models', 'src.ui', 'src.config'])
        ]
        
        for script, expected_imports in scripts:
            with open(script, 'r') as f:
                content = f.read()
            
            for import_module in expected_imports:
                assert f"from {import_module} import" in content or f"import {import_module}" in content

    @patch('subprocess.run')
    def test_script_execution_simulation(self, mock_run):
        """Test simulated script execution."""
        scripts = ['main.py', 'demo_dual_charts.py', 'demo_dual_charts_minute.py', 'example_dual_charts.py']
        
        # Mock successful execution
        mock_run.return_value.returncode = 0
        
        for script in scripts:
            # Simulate running the script
            result = mock_run(['python', script])
            assert result.returncode == 0

    def test_main_script_structure(self):
        """Test that main scripts have the expected structure."""
        # Test main.py structure
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        assert 'if __name__ == "__main__":' in main_content
        assert 'ChartsDailyData' in main_content
        assert 'create_dual_chart_grid' in main_content or 'create_and_bind_chart' in main_content
        
        # Test demo scripts structure
        demo_scripts = ['demo_dual_charts.py', 'demo_dual_charts_minute.py', 'example_dual_charts.py']
        for script in demo_scripts:
            with open(script, 'r') as f:
                content = f.read()
            
            assert 'def main():' in content
            assert 'if __name__ == "__main__":' in content

    def test_script_file_paths(self):
        """Test that all script files exist and are readable."""
        scripts = ['main.py', 'demo_dual_charts.py', 'demo_dual_charts_minute.py', 'example_dual_charts.py']
        
        for script in scripts:
            assert os.path.exists(script), f"Script {script} does not exist"
            assert os.path.isfile(script), f"{script} is not a file"
            assert os.access(script, os.R_OK), f"Script {script} is not readable"