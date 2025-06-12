import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.data import load_daily_data, load_daily_df, apply_indicators


class TestLoadDailyData:
    """Test cases for the load_daily_data function."""

    def test_load_daily_data_basic(self):
        """Test basic functionality of load_daily_data."""
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 50 + ['MSFT'] * 50,
            'date': list(dates[:50]) + list(dates[:50]),
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(200, 300, 100),
            'low': np.random.uniform(50, 100, 100),
            'close': np.random.uniform(100, 200, 100),
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Test loading data for AAPL around a specific date
        target_date = datetime(2023, 1, 15)
        result = load_daily_data('AAPL', target_date, data)
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert all(result['ticker'] == 'AAPL')
        assert result['date'].is_monotonic_increasing
        assert result.index.equals(pd.RangeIndex(len(result)))

    def test_load_daily_data_date_range(self):
        """Test that load_daily_data respects the N_DAYS range."""
        # Create data spanning 100 days
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 100,
            'date': dates,
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(200, 300, 100),
            'low': np.random.uniform(50, 100, 100),
            'close': np.random.uniform(100, 200, 100),
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Test with a date in the middle
        target_date = datetime(2023, 2, 15)  # Day 45
        result = load_daily_data('AAPL', target_date, data)
        
        # Should include dates within ±30 days
        expected_start = target_date - timedelta(days=30)
        expected_end = target_date + timedelta(days=30)
        
        assert result['date'].min() >= expected_start
        assert result['date'].max() <= expected_end

    def test_load_daily_data_no_matching_ticker(self):
        """Test behavior when no matching ticker is found."""
        data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT'],
            'date': [datetime(2023, 1, 1), datetime(2023, 1, 1)],
            'open': [100, 200],
            'high': [110, 210],
            'low': [90, 190],
            'close': [105, 205],
            'volume': [1000, 2000]
        })
        
        result = load_daily_data('GOOGL', datetime(2023, 1, 1), data)
        assert len(result) == 0

    def test_load_daily_data_edge_dates(self):
        """Test behavior at the edges of the date range."""
        # Create data for a limited date range
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 10,
            'date': dates,
            'open': np.random.uniform(100, 200, 10),
            'high': np.random.uniform(200, 300, 10),
            'low': np.random.uniform(50, 100, 10),
            'close': np.random.uniform(100, 200, 10),
            'volume': np.random.randint(1000, 10000, 10)
        })
        
        # Test with a date before the data range
        early_date = datetime(2022, 12, 1)
        result = load_daily_data('AAPL', early_date, data)
        assert len(result) == 0
        
        # Test with a date after the data range
        late_date = datetime(2023, 2, 15)
        result = load_daily_data('AAPL', late_date, data)
        assert len(result) == 0


class TestLoadDailyDf:
    """Test cases for the load_daily_df function."""

    def test_load_daily_df_success(self, tmp_path):
        """Test successful loading and validation of a feather file."""
        # Create sample data that matches the schema
        data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT', 'AAPL'],
            'date': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-02']),
            'open': np.array([100.0, 200.0, 101.0], dtype=np.float32),
            'high': np.array([110.0, 210.0, 111.0], dtype=np.float32),
            'low': np.array([90.0, 190.0, 91.0], dtype=np.float32),
            'close': np.array([105.0, 205.0, 106.0], dtype=np.float32),
            'volume': [1000, 2000, 1100]
        })
        
        # Save to feather file
        test_file = tmp_path / "test_data.feather"
        data.to_feather(test_file)
        
        # Test loading
        result = load_daily_df(str(test_file))
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']

    def test_load_daily_df_removes_duplicates(self, tmp_path):
        """Test that load_daily_df removes duplicate ticker-date combinations."""
        # Create data with duplicates
        data = pd.DataFrame({
            'ticker': ['AAPL', 'AAPL', 'MSFT'],
            'date': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
            'open': np.array([100.0, 100.0, 200.0], dtype=np.float32),
            'high': np.array([110.0, 110.0, 210.0], dtype=np.float32),
            'low': np.array([90.0, 90.0, 190.0], dtype=np.float32),
            'close': np.array([105.0, 105.0, 205.0], dtype=np.float32),
            'volume': [1000, 1000, 2000]
        })
        
        test_file = tmp_path / "test_data.feather"
        data.to_feather(test_file)
        
        result = load_daily_df(str(test_file))
        
        # Should have only 2 rows after removing duplicates
        assert len(result) == 2
        assert result['ticker'].tolist() == ['AAPL', 'MSFT']

    def test_load_daily_df_sorts_data(self, tmp_path):
        """Test that load_daily_df sorts data by ticker and date."""
        # Create unsorted data
        data = pd.DataFrame({
            'ticker': ['MSFT', 'AAPL', 'MSFT', 'AAPL'],
            'date': pd.to_datetime(['2023-01-02', '2023-01-02', '2023-01-01', '2023-01-01']),
            'open': np.array([200.0, 101.0, 199.0, 100.0], dtype=np.float32),
            'high': np.array([210.0, 111.0, 209.0, 110.0], dtype=np.float32),
            'low': np.array([190.0, 91.0, 189.0, 90.0], dtype=np.float32),
            'close': np.array([205.0, 106.0, 204.0, 105.0], dtype=np.float32),
            'volume': [2000, 1100, 1900, 1000]
        })
        
        test_file = tmp_path / "test_data.feather"
        data.to_feather(test_file)
        
        result = load_daily_df(str(test_file))
        
        # Check sorting
        expected_order = ['AAPL', 'AAPL', 'MSFT', 'MSFT']
        expected_dates = ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02']
        
        assert result['ticker'].tolist() == expected_order
        assert result['date'].dt.strftime('%Y-%m-%d').tolist() == expected_dates


class TestApplyIndicators:
    """Test cases for the apply_indicators function."""

    @patch('src.data.config')
    def test_apply_indicators_sma(self, mock_config):
        """Test applying SMA indicator."""
        # Mock configuration
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = {"period": 3}
        mock_config.indicators = [mock_indicator]
        
        # Create sample data
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 5,
            'date': pd.date_range('2023-01-01', periods=5),
            'close': [100.0, 102.0, 104.0, 103.0, 105.0]
        })
        
        result = apply_indicators(data)
        
        # Check that SMA column was added
        assert 'SMA_3' in result.columns
        
        # Check SMA calculation (should be NaN for first 2 rows, then rolling mean)
        expected_sma = [np.nan, np.nan, 102.0, 103.0, 104.0]
        np.testing.assert_array_almost_equal(result['SMA_3'].values, expected_sma, decimal=1)

    @patch('src.data.config')
    def test_apply_indicators_no_indicators(self, mock_config):
        """Test behavior when no indicators are configured."""
        mock_config.indicators = None
        
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 3,
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100.0, 102.0, 104.0]
        })
        
        result = apply_indicators(data)
        
        # Should return the same dataframe
        pd.testing.assert_frame_equal(result, data)

    @patch('src.data.config')
    def test_apply_indicators_empty_list(self, mock_config):
        """Test behavior with empty indicators list."""
        mock_config.indicators = []
        
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 3,
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100.0, 102.0, 104.0]
        })
        
        result = apply_indicators(data)
        
        # Should return the same dataframe
        pd.testing.assert_frame_equal(result, data)

    @patch('src.data.config')
    def test_apply_indicators_multiple_tickers(self, mock_config):
        """Test applying indicators with multiple tickers."""
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = {"period": 2}
        mock_config.indicators = [mock_indicator]
        
        # Create data with multiple tickers
        data = pd.DataFrame({
            'ticker': ['AAPL', 'AAPL', 'MSFT', 'MSFT'],
            'date': pd.date_range('2023-01-01', periods=2).tolist() * 2,
            'close': [100.0, 102.0, 200.0, 204.0]
        })
        
        result = apply_indicators(data)
        
        # Check that SMA is calculated separately for each ticker
        assert 'SMA_2' in result.columns
        
        # For AAPL: [NaN, 101.0], for MSFT: [NaN, 202.0]
        expected_sma = [np.nan, 101.0, np.nan, 202.0]
        np.testing.assert_array_almost_equal(result['SMA_2'].values, expected_sma, decimal=1)

    @patch('src.data.config')
    def test_apply_indicators_missing_parameters(self, mock_config):
        """Test behavior when indicator has no parameters."""
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = None
        mock_config.indicators = [mock_indicator]
        
        data = pd.DataFrame({
            'ticker': ['AAPL'] * 3,
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100.0, 102.0, 104.0]
        })
        
        result = apply_indicators(data)
        
        # Should not add any SMA column
        assert 'SMA_' not in str(result.columns)
        pd.testing.assert_frame_equal(result, data)