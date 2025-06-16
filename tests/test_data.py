import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.data import load_daily_data, load_daily_df, apply_indicators, load_min_data, load_min_chart, format_min_chart_data


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


class TestLoadMinData:
    """Test cases for the load_min_data function."""

    def test_load_min_data_success(self, temp_min_feather_file):
        """Test successful loading and validation of minute data."""
        result = load_min_data(temp_min_feather_file)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'ticker' in result.columns
        assert 'datetime' in result.columns
        assert '_date' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        
        # Check that datetime column is timezone-naive
        assert result['datetime'].dt.tz is None
        
        # Check that data is sorted by ticker and datetime
        assert result['ticker'].is_monotonic_increasing or len(result['ticker'].unique()) == 1
        
        # Check that index is reset
        assert result.index.equals(pd.RangeIndex(len(result)))

    def test_load_min_data_datetime_conversion(self, temp_min_feather_file_with_tz):
        """Test that timezone-aware datetime is converted to timezone-naive."""
        result = load_min_data(temp_min_feather_file_with_tz)
        
        # Check that datetime column is timezone-naive after conversion
        assert result['datetime'].dt.tz is None
        assert 'datetime' in result.columns
        assert '_date' in result.columns

    def test_load_min_data_column_renaming(self, temp_min_feather_file):
        """Test that columns are renamed correctly."""
        result = load_min_data(temp_min_feather_file)
        
        # Original 'datetime' should be renamed to 'datetime' (after tz conversion)
        # Original 'date' should be renamed to '_date'
        assert 'datetime' in result.columns
        assert '_date' in result.columns
        assert 'date' not in result.columns  # Original 'date' should be renamed

    def test_load_min_data_sorting(self, temp_min_feather_file_unsorted_min):
        """Test that data is sorted by ticker and datetime."""
        result = load_min_data(temp_min_feather_file_unsorted_min)
        
        # Check that data is sorted
        expected_tickers = ['AAPL', 'AAPL', 'MSFT', 'MSFT']
        assert result['ticker'].tolist() == expected_tickers
        
        # Check datetime sorting within each ticker
        for ticker in result['ticker'].unique():
            ticker_data = result[result['ticker'] == ticker]
            assert ticker_data['datetime'].is_monotonic_increasing


class TestLoadMinChart:
    """Test cases for the load_min_chart function."""

    @patch('src.data.config')
    def test_load_min_chart_basic(self, mock_config, sample_min_data):
        """Test basic functionality of load_min_chart."""
        mock_config.chart.n_days_intraday = 2
        
        target_date = datetime(2023, 1, 15, 12, 0, 0)
        result = load_min_chart('AAPL', target_date, sample_min_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert all(result['ticker'] == 'AAPL')
        assert 'time' in result.columns
        assert 'datetime' not in result.columns  # Should be removed by format_min_chart_data
        assert '_date' not in result.columns     # Should be removed by format_min_chart_data

    @patch('src.data.config')
    def test_load_min_chart_date_range(self, mock_config, sample_min_data):
        """Test that load_min_chart respects the n_days range."""
        mock_config.chart.n_days_intraday = 1
        
        target_date = datetime(2023, 1, 15, 12, 0, 0)
        result = load_min_chart('AAPL', target_date, sample_min_data)
        
        # Should include datetimes within ±1 day
        expected_start = target_date - pd.Timedelta(days=1)
        expected_end = target_date + pd.Timedelta(days=1)
        
        # Convert time strings back to datetime for comparison
        result_times = pd.to_datetime(result['time'])
        assert result_times.min() >= expected_start
        assert result_times.max() <= expected_end

    @patch('src.data.config')
    def test_load_min_chart_custom_n_days(self, mock_config, sample_min_data):
        """Test load_min_chart with custom n_days parameter."""
        mock_config.chart.n_days_intraday = 5  # This should be ignored
        
        target_date = datetime(2023, 1, 15, 12, 0, 0)
        custom_n_days = 3
        result = load_min_chart('AAPL', target_date, sample_min_data, n_days=custom_n_days)
        
        # Should use custom n_days (3) instead of config value (5)
        expected_start = target_date - pd.Timedelta(days=custom_n_days)
        expected_end = target_date + pd.Timedelta(days=custom_n_days)
        
        result_times = pd.to_datetime(result['time'])
        assert result_times.min() >= expected_start
        assert result_times.max() <= expected_end

    def test_load_min_chart_no_matching_ticker(self, sample_min_data):
        """Test behavior when no matching ticker is found."""
        target_date = datetime(2023, 1, 15, 12, 0, 0)
        result = load_min_chart('NONEXISTENT', target_date, sample_min_data)
        
        assert len(result) == 0

    def test_load_min_chart_edge_dates(self, sample_min_data):
        """Test behavior at the edges of the date range."""
        # Test with a date before the data range
        early_date = datetime(2022, 1, 1, 12, 0, 0)
        result = load_min_chart('AAPL', early_date, sample_min_data)
        assert len(result) == 0
        
        # Test with a date after the data range
        late_date = datetime(2024, 12, 31, 12, 0, 0)
        result = load_min_chart('AAPL', late_date, sample_min_data)
        assert len(result) == 0


class TestFormatMinChartData:
    """Test cases for the format_min_chart_data function."""

    def test_format_min_chart_data_basic(self, sample_min_data_raw):
        """Test basic formatting of minute chart data."""
        result = format_min_chart_data(sample_min_data_raw.copy())
        
        assert isinstance(result, pd.DataFrame)
        assert 'time' in result.columns
        assert 'datetime' not in result.columns  # Should be removed
        assert '_date' not in result.columns     # Should be removed
        
        # Check that time column contains properly formatted strings
        time_values = result['time'].tolist()
        for time_str in time_values:
            # Should be in format "YYYY-MM-DD HH:MM:SS"
            assert len(time_str) == 19
            assert time_str[4] == '-'
            assert time_str[7] == '-'
            assert time_str[10] == ' '
            assert time_str[13] == ':'
            assert time_str[16] == ':'

    def test_format_min_chart_data_time_format(self, sample_min_data_raw):
        """Test that time column is formatted correctly."""
        test_data = sample_min_data_raw.copy()
        result = format_min_chart_data(test_data)
        
        # Check specific time formatting
        expected_format = "%Y-%m-%d %H:%M:%S"
        for time_str in result['time']:
            # Should be parseable back to datetime
            parsed_time = datetime.strptime(time_str, expected_format)
            assert isinstance(parsed_time, datetime)

    def test_format_min_chart_data_preserves_other_columns(self, sample_min_data_raw):
        """Test that other columns are preserved during formatting."""
        test_data = sample_min_data_raw.copy()
        original_columns = set(test_data.columns) - {'datetime', '_date'}
        
        result = format_min_chart_data(test_data)
        result_columns = set(result.columns) - {'time'}
        
        # All original columns except datetime and _date should be preserved
        assert result_columns == original_columns

    def test_format_min_chart_data_empty_dataframe(self):
        """Test formatting of empty dataframe."""
        empty_df = pd.DataFrame({
            'ticker': pd.Series([], dtype='str'),
            'datetime': pd.Series([], dtype='datetime64[ns]'),
            '_date': pd.Series([], dtype='datetime64[ns]'),
            'open': pd.Series([], dtype='float32'),
            'high': pd.Series([], dtype='float32'),
            'low': pd.Series([], dtype='float32'),
            'close': pd.Series([], dtype='float32'),
            'volume': pd.Series([], dtype='int32')
        })
        
        result = format_min_chart_data(empty_df)
        
        assert len(result) == 0
        assert 'time' in result.columns
        assert 'datetime' not in result.columns
        assert '_date' not in result.columns

    def test_format_min_chart_data_single_row(self):
        """Test formatting of single row dataframe."""
        single_row_df = pd.DataFrame({
            'ticker': ['AAPL'],
            'datetime': [datetime(2023, 1, 15, 14, 30, 0)],
            '_date': [datetime(2023, 1, 15)],
            'open': pd.array([150.0], dtype='float32'),
            'high': pd.array([151.0], dtype='float32'),
            'low': pd.array([149.0], dtype='float32'),
            'close': pd.array([150.5], dtype='float32'),
            'volume': pd.array([1000], dtype='int32')
        })
        
        result = format_min_chart_data(single_row_df)
        
        assert len(result) == 1
        assert result['time'].iloc[0] == "2023-01-15 14:30:00"
        assert result['ticker'].iloc[0] == 'AAPL'
        assert result['close'].iloc[0] == 150.5