import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.data import load_daily_data, load_daily_df, apply_indicators


class TestLoadDailyData:
    """Test cases for the load_daily_data function."""

    def test_load_daily_data_basic(self, sample_stock_data):
        """Test basic functionality of load_daily_data."""
        # Test loading data for AAPL around a specific date
        target_date = datetime(2023, 1, 15)
        result = load_daily_data('AAPL', target_date, sample_stock_data)
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert all(result['ticker'] == 'AAPL')
        assert result['date'].is_monotonic_increasing
        assert result.index.equals(pd.RangeIndex(len(result)))

    def test_load_daily_data_date_range(self, sample_stock_data):
        """Test that load_daily_data respects the N_DAYS range."""
        # Test with a date in the middle of the sample data range
        target_date = datetime(2023, 2, 15)
        result = load_daily_data('AAPL', target_date, sample_stock_data)
        
        # Should include dates within ±30 days
        expected_start = target_date - timedelta(days=30)
        expected_end = target_date + timedelta(days=30)
        
        assert result['date'].min() >= expected_start
        assert result['date'].max() <= expected_end

    def test_load_daily_data_no_matching_ticker(self, sample_stock_data):
        """Test behavior when no matching ticker is found."""
        result = load_daily_data('NONEXISTENT', datetime(2023, 1, 1), sample_stock_data)
        assert len(result) == 0

    def test_load_daily_data_edge_dates(self, sample_stock_data):
        """Test behavior at the edges of the date range."""
        # Test with a date before the data range
        early_date = datetime(2022, 1, 1)
        result = load_daily_data('AAPL', early_date, sample_stock_data)
        assert len(result) == 0
        
        # Test with a date after the data range
        late_date = datetime(2024, 12, 31)
        result = load_daily_data('AAPL', late_date, sample_stock_data)
        assert len(result) == 0


class TestLoadDailyDf:
    """Test cases for the load_daily_df function."""

    def test_load_daily_df_success(self, temp_feather_file):
        """Test successful loading and validation of a feather file."""
        # Test loading
        result = load_daily_df(temp_feather_file)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'ticker' in result.columns
        assert 'date' in result.columns
        assert 'close' in result.columns

    def test_load_daily_df_removes_duplicates(self, temp_feather_file_with_duplicates):
        """Test that load_daily_df removes duplicate ticker-date combinations."""
        result = load_daily_df(temp_feather_file_with_duplicates)
        
        # Should have only 2 rows after removing duplicates
        assert len(result) == 2
        assert result['ticker'].tolist() == ['AAPL', 'MSFT']

    def test_load_daily_df_sorts_data(self, temp_feather_file_unsorted):
        """Test that load_daily_df sorts data by ticker and date."""
        result = load_daily_df(temp_feather_file_unsorted)
        
        # Check sorting
        expected_order = ['AAPL', 'AAPL', 'MSFT', 'MSFT']
        expected_dates = ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02']
        
        assert result['ticker'].tolist() == expected_order
        assert result['date'].dt.strftime('%Y-%m-%d').tolist() == expected_dates


class TestApplyIndicators:
    """Test cases for the apply_indicators function."""

    @patch('src.data.config')
    def test_apply_indicators_sma(self, mock_config, sample_stock_data):
        """Test applying SMA indicator."""
        # Mock configuration
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = {"period": 3}
        mock_config.indicators = [mock_indicator]
        
        # Use a subset of sample data for testing
        test_data = sample_stock_data[sample_stock_data['ticker'] == 'AAPL'].head(5).copy()
        
        result = apply_indicators(test_data)
        
        # Check that SMA column was added
        assert 'SMA_3' in result.columns
        
        # Check SMA calculation (should be NaN for first 2 rows, then rolling mean)
        sma_values = result['SMA_3'].values
        assert np.isnan(sma_values[0])  # First value should be NaN
        assert np.isnan(sma_values[1])  # Second value should be NaN
        assert not np.isnan(sma_values[2])  # Third value should be calculated
        
        # Verify SMA calculation manually for the third value
        expected_third_sma = test_data['close'].iloc[:3].mean()
        np.testing.assert_almost_equal(sma_values[2], expected_third_sma, decimal=2)

    @patch('src.data.config')
    def test_apply_indicators_no_indicators(self, mock_config, sample_stock_data):
        """Test behavior when no indicators are configured."""
        mock_config.indicators = None
        
        test_data = sample_stock_data.head(3).copy()
        
        result = apply_indicators(test_data)
        
        # Should return the same dataframe
        pd.testing.assert_frame_equal(result, test_data)

    @patch('src.data.config')
    def test_apply_indicators_empty_list(self, mock_config, sample_stock_data):
        """Test behavior with empty indicators list."""
        mock_config.indicators = []
        
        test_data = sample_stock_data.head(3).copy()
        
        result = apply_indicators(test_data)
        
        # Should return the same dataframe
        pd.testing.assert_frame_equal(result, test_data)

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