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
    create_sample_min_data,
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


@pytest.fixture
def sample_min_data():
    """Fixture providing sample minute data."""
    return create_sample_min_data()


@pytest.fixture
def sample_min_data_raw():
    """Fixture providing raw sample minute data with datetime and _date columns."""
    data = create_sample_min_data()
    # Add _date column for testing format_min_chart_data
    data['_date'] = pd.to_datetime(data['datetime'].dt.date)
    return data


@pytest.fixture
def temp_min_feather_file():
    """Fixture providing a temporary feather file with minute data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create minute data with timezone-aware datetime
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 5 + ['MSFT'] * 5,
            'datetime': pd.date_range('2023-01-15 09:30:00', periods=10, freq='1min', tz='UTC'),
            'date': pd.date_range('2023-01-15', periods=10, freq='1min'),
            'open': pd.array([150.0, 150.1, 150.2, 150.3, 150.4, 250.0, 250.1, 250.2, 250.3, 250.4], dtype='float32'),
            'high': pd.array([150.5, 150.6, 150.7, 150.8, 150.9, 250.5, 250.6, 250.7, 250.8, 250.9], dtype='float32'),
            'low': pd.array([149.5, 149.6, 149.7, 149.8, 149.9, 249.5, 249.6, 249.7, 249.8, 249.9], dtype='float32'),
            'close': pd.array([150.2, 150.3, 150.4, 150.5, 150.6, 250.2, 250.3, 250.4, 250.5, 250.6], dtype='float32'),
            'volume': pd.array([1000, 1100, 1200, 1300, 1400, 2000, 2100, 2200, 2300, 2400], dtype='int32')
        })
        data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_min_feather_file_with_tz():
    """Fixture providing a temporary feather file with timezone-aware minute data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create minute data with timezone-aware datetime
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 3,
            'datetime': pd.date_range('2023-01-15 09:30:00', periods=3, freq='1min', tz='America/New_York'),
            'date': pd.date_range('2023-01-15', periods=3, freq='1min'),
            'open': pd.array([150.0, 150.1, 150.2], dtype='float32'),
            'high': pd.array([150.5, 150.6, 150.7], dtype='float32'),
            'low': pd.array([149.5, 149.6, 149.7], dtype='float32'),
            'close': pd.array([150.2, 150.3, 150.4], dtype='float32'),
            'volume': pd.array([1000, 1100, 1200], dtype='int32')
        })
        data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def temp_min_feather_file_unsorted_min():
    """Fixture providing a temporary feather file with unsorted minute data."""
    with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as tmp_file:
        # Create unsorted minute data
        data = pd.DataFrame({
            'ticker': ['MSFT', 'AAPL', 'MSFT', 'AAPL'],
            'datetime': pd.to_datetime([
                '2023-01-15 09:32:00',
                '2023-01-15 09:32:00', 
                '2023-01-15 09:30:00',
                '2023-01-15 09:30:00'
            ]),
            'date': pd.to_datetime(['2023-01-15'] * 4),
            'open': pd.array([250.1, 150.1, 250.0, 150.0], dtype='float32'),
            'high': pd.array([250.6, 150.6, 250.5, 150.5], dtype='float32'),
            'low': pd.array([249.6, 149.6, 249.5, 149.5], dtype='float32'),
            'close': pd.array([250.3, 150.3, 250.2, 150.2], dtype='float32'),
            'volume': pd.array([2100, 1100, 2000, 1000], dtype='int32')
        })
        data.to_feather(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)