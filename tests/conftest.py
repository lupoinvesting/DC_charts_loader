"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
import pandas as pd
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock

from tests.fixtures.sample_data import (
    create_sample_stock_data,
    create_sample_config_data,
    create_sample_charts_data,
    create_sample_indicator_data,
    SAMPLE_STOCK_DATA,
    SAMPLE_CONFIG_DATA,
    SAMPLE_CHARTS_DATA
)


@pytest.fixture
def sample_stock_data():
    """Fixture providing sample stock data."""
    return SAMPLE_STOCK_DATA.copy()


@pytest.fixture
def sample_config_data():
    """Fixture providing sample configuration data."""
    return SAMPLE_CONFIG_DATA.copy()


@pytest.fixture
def sample_charts_data():
    """Fixture providing sample charts metadata."""
    return SAMPLE_CHARTS_DATA.copy()


@pytest.fixture
def sample_stock_data_with_indicators():
    """Fixture providing sample stock data with technical indicators."""
    base_data = create_sample_stock_data()
    return create_sample_indicator_data(base_data)


@pytest.fixture
def temp_feather_file():
    """Fixture providing a temporary feather file with sample data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create sample data that matches the expected schema
        data = create_sample_stock_data(periods=10)
        # Ensure only the required columns for the schema
        schema_data = data[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']].copy()
        schema_data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_feather_file_with_duplicates():
    """Fixture providing a temporary feather file with duplicate data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create data with duplicates
        data = pd.DataFrame({
            'ticker': ['AAPL', 'AAPL', 'MSFT'],
            'date': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'open': pd.array([100.0, 100.0, 200.0], dtype='float32'),
            'high': pd.array([110.0, 110.0, 210.0], dtype='float32'),
            'low': pd.array([90.0, 90.0, 190.0], dtype='float32'),
            'close': pd.array([105.0, 105.0, 205.0], dtype='float32'),
            'volume': [1000, 1000, 2000]
        })
        data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_feather_file_unsorted():
    """Fixture providing a temporary feather file with unsorted data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create unsorted data
        data = pd.DataFrame({
            'ticker': ['MSFT', 'AAPL', 'MSFT', 'AAPL'],
            'date': pd.to_datetime(['2023-01-02', '2023-01-02', '2023-01-01', '2023-01-01']),
            'open': pd.array([200.0, 101.0, 199.0, 100.0], dtype='float32'),
            'high': pd.array([210.0, 111.0, 209.0, 110.0], dtype='float32'),
            'low': pd.array([190.0, 91.0, 189.0, 90.0], dtype='float32'),
            'close': pd.array([205.0, 106.0, 204.0, 105.0], dtype='float32'),
            'volume': [2000, 1100, 1900, 1000]
        })
        data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_config_file():
    """Fixture providing a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        config_data = create_sample_config_data()
        json.dump(config_data, tmp_file, indent=2)
        tmp_file.flush()
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def mock_chart():
    """Fixture providing a mock chart object."""
    chart = Mock()
    chart.id = "test_chart"
    chart.set = Mock()
    chart.watermark = Mock()
    chart.legend = Mock()
    chart.hotkey = Mock()
    chart.screenshot = Mock(return_value=b'fake_image_data')
    chart.create_line = Mock()
    chart.run_script = Mock()
    return chart


@pytest.fixture
def mock_chart_data():
    """Fixture providing a mock chart data object."""
    chart_data = Mock()
    chart_data.current_index = 0
    chart_data.charts = create_sample_charts_data()
    chart_data.data = create_sample_stock_data()
    
    # Mock methods
    chart_data.get_metadata = Mock(return_value={
        'ticker': 'AAPL',
        'date_str': '2023-01-15',
        'date': pd.Timestamp('2023-01-15'),
        'timeframe': '1D',
        'index': 0
    })
    
    chart_data.load_chart = Mock(return_value=(
        create_sample_stock_data(periods=30),
        {
            'ticker': 'AAPL',
            'date_str': '2023-01-15',
            'date': pd.Timestamp('2023-01-15'),
            'timeframe': '1D',
            'index': 0
        }
    ))
    
    chart_data.next_chart = Mock(return_value=(
        create_sample_stock_data(periods=30),
        {
            'ticker': 'MSFT',
            'date_str': '2023-01-16',
            'date': pd.Timestamp('2023-01-16'),
            'timeframe': '1D',
            'index': 1
        }
    ))
    
    chart_data.previous_chart = Mock(return_value=(
        create_sample_stock_data(periods=30),
        {
            'ticker': 'GOOGL',
            'date_str': '2023-01-14',
            'date': pd.Timestamp('2023-01-14'),
            'timeframe': '1D',
            'index': 2
        }
    ))
    
    return chart_data


@pytest.fixture
def mock_indicator():
    """Fixture providing a mock indicator configuration."""
    indicator = Mock()
    indicator.name = "SMA"
    indicator.parameters = {"period": 20, "source": "close"}
    return indicator


@pytest.fixture(scope="session")
def disable_warnings():
    """Fixture to disable specific warnings during testing."""
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning, module="pandera")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="multiprocessing")


# Auto-use the disable_warnings fixture
@pytest.fixture(autouse=True)
def _disable_warnings(disable_warnings):
    """Auto-apply warning suppression to all tests."""
    pass