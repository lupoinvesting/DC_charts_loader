import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open

from src.ui import (
    plot_chart, plot_line, on_up, on_down, plot_indicators,
    on_maximize, on_timeframe_change, on_up_dual, on_down_dual,
    save_screenshot_dual, create_dual_chart_grid, save_screenshot,
    create_and_bind_chart
)
from src.models import ChartsMinuteData


class TestPlotChart:
    """Test cases for the plot_chart function."""

    def test_plot_chart_success(self):
        """Test successful chart plotting."""
        # Create mock chart and data
        mock_chart = Mock()
        mock_chart.watermark = Mock()
        mock_chart.legend = Mock()
        
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        metadata = {
            'ticker': 'AAPL',
            'timeframe': '1D',
            'date_str': '2023-01-15'
        }
        
        plot_chart(df, metadata, mock_chart)
        
        # Verify chart methods were called
        mock_chart.set.assert_called_once_with(df)
        mock_chart.watermark.assert_called_once_with(
            'AAPL 1D 2023-01-15',
            vert_align='top'
        )
        mock_chart.legend.assert_called_once_with(
            visible=True,
            ohlc=True,
            lines=True,
            font_family='arial',
            font_size=12,
            percent=False
        )

    def test_plot_chart_watermark_attribute_error(self):
        """Test chart plotting when watermark raises AttributeError."""
        # Create mock chart that raises AttributeError on first call, succeeds on second
        mock_chart = Mock()
        mock_chart.watermark = Mock(side_effect=[
            TypeError("Custom watermark not available"), 
            None
        ])
        mock_chart.legend = Mock()
        
        df = pd.DataFrame({'close': [100, 101, 102]})
        metadata = {
            'ticker': 'AAPL',
            'timeframe': '1D',
            'date_str': '2023-01-15'
        }
        
        plot_chart(df, metadata, mock_chart)
        
        # Should call watermark twice: once with vert_align (fails), once without
        assert mock_chart.watermark.call_count == 2
        mock_chart.watermark.assert_any_call('AAPL 1D 2023-01-15', vert_align='top')
        mock_chart.watermark.assert_any_call('AAPL 1D 2023-01-15')


class TestPlotLine:
    """Test cases for the plot_line function."""

    def test_plot_line(self):
        """Test plotting a line on the chart."""
        mock_chart = Mock()
        mock_line = Mock()
        mock_chart.create_line.return_value = mock_line
        
        data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'SMA_20': [100, 101, 102]
        })
        
        plot_line(data, mock_chart, 'SMA_20')
        
        # Verify line creation and data setting
        mock_chart.create_line.assert_called_once_with(name='SMA_20')
        mock_line.set.assert_called_once_with(data)


class TestNavigationFunctions:
    """Test cases for navigation functions."""

    def test_on_up(self):
        """Test on_up function."""
        mock_chart = Mock()
        mock_chart_data = Mock()
        
        # Mock the next_chart method
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data.next_chart.return_value = (mock_df, mock_metadata)
        
        with patch('src.ui.plot_chart') as mock_plot_chart:
            on_up(mock_chart, mock_chart_data)
        
        # Verify next_chart was called and plot_chart was called with results
        mock_chart_data.next_chart.assert_called_once()
        mock_plot_chart.assert_called_once_with(mock_df, mock_metadata, mock_chart)

    def test_on_down(self):
        """Test on_down function."""
        mock_chart = Mock()
        mock_chart_data = Mock()
        
        # Mock the previous_chart method
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'MSFT', 'timeframe': '1D', 'date_str': '2023-01-10'}
        mock_chart_data.previous_chart.return_value = (mock_df, mock_metadata)
        
        with patch('src.ui.plot_chart') as mock_plot_chart:
            on_down(mock_chart, mock_chart_data)
        
        # Verify previous_chart was called and plot_chart was called with results
        mock_chart_data.previous_chart.assert_called_once()
        mock_plot_chart.assert_called_once_with(mock_df, mock_metadata, mock_chart)


class TestPlotIndicators:
    """Test cases for the plot_indicators function."""

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_sma(self, mock_plot_line, mock_config):
        """Test plotting SMA indicator."""
        # Mock configuration
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = {"period": 20}
        mock_config.indicators = [mock_indicator]
        
        # Create DataFrame with SMA column
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102],
            'SMA_20': [99, 100, 101]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # Verify plot_line was called for SMA
        mock_plot_line.assert_called_once()
        call_args = mock_plot_line.call_args
        called_data, called_chart, called_name = call_args[0]
        
        # Check the arguments separately
        pd.testing.assert_frame_equal(called_data, df[['date', 'SMA_20']])
        assert called_chart is mock_chart
        assert called_name == 'SMA_20'

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_sma_missing_column(self, mock_plot_line, mock_config):
        """Test plotting SMA indicator when column is missing."""
        # Mock configuration
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = {"period": 20}
        mock_config.indicators = [mock_indicator]
        
        # Create DataFrame without SMA column
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # plot_line should not be called since SMA_20 column doesn't exist
        mock_plot_line.assert_not_called()

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_no_parameters(self, mock_plot_line, mock_config):
        """Test plotting indicator with no parameters."""
        # Mock configuration
        mock_indicator = MagicMock()
        mock_indicator.name = "SMA"
        mock_indicator.parameters = None
        mock_config.indicators = [mock_indicator]
        
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # plot_line should not be called since no period is specified
        mock_plot_line.assert_not_called()

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_no_indicators(self, mock_plot_line, mock_config):
        """Test plotting when no indicators are configured."""
        mock_config.indicators = None
        
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # plot_line should not be called
        mock_plot_line.assert_not_called()

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_empty_list(self, mock_plot_line, mock_config):
        """Test plotting with empty indicators list."""
        mock_config.indicators = []
        
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # plot_line should not be called
        mock_plot_line.assert_not_called()

    @patch('src.ui.config')
    @patch('src.ui.plot_line')
    def test_plot_indicators_non_sma(self, mock_plot_line, mock_config):
        """Test plotting non-SMA indicator (should be ignored)."""
        # Mock configuration with non-SMA indicator
        mock_indicator = MagicMock()
        mock_indicator.name = "RSI"
        mock_indicator.parameters = {"period": 14}
        mock_config.indicators = [mock_indicator]
        
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'close': [100, 101, 102]
        })
        
        mock_chart = Mock()
        
        plot_indicators(df, mock_chart)
        
        # plot_line should not be called since only SMA is implemented
        mock_plot_line.assert_not_called()


class TestSaveScreenshot:
    """Test cases for the save_screenshot function."""

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_screenshot(self, mock_makedirs, mock_file_open):
        """Test save_screenshot function."""
        from src.ui import save_screenshot
        
        # Create mock chart and chart_data
        mock_chart = Mock()
        mock_chart.screenshot.return_value = b'fake_image_data'
        
        mock_chart_data = Mock()
        mock_chart_data.current_index = 0
        mock_chart_data.get_metadata.return_value = {
            'ticker': 'AAPL',
            'date_str': '2023-01-15'
        }
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            save_screenshot(mock_chart, mock_chart_data, "test_folder")
        
        # Verify screenshot was taken
        mock_chart.screenshot.assert_called_once()
        
        # Verify metadata was retrieved
        mock_chart_data.get_metadata.assert_called_once_with(0)
        
        # Verify file was written
        expected_filename = "test_folder/AAPL_2023-01-15_screenshot.png"
        mock_file_open.assert_called_once_with(expected_filename, "wb")
        mock_file_open().write.assert_called_once_with(b'fake_image_data')
        
        # Verify print message
        mock_print.assert_called_once_with(f"Screenshot saved to {expected_filename}")


class TestCreateAndBindChart:
    """Test cases for the create_and_bind_chart function."""

    @patch('src.ui.Chart')
    @patch('src.ui.plot_chart')
    @patch('src.ui.plot_indicators')
    def test_create_and_bind_chart(self, mock_plot_indicators, mock_plot_chart, mock_chart_class):
        """Test create_and_bind_chart function."""
        from src.ui import create_and_bind_chart
        
        # Create mock chart instance
        mock_chart = Mock()
        mock_chart_class.return_value = mock_chart
        
        # Create mock chart_data
        mock_chart_data = Mock()
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'AAPL', 'date_str': '2023-01-15'}
        mock_chart_data.load_chart.return_value = (mock_df, mock_metadata)
        
        result = create_and_bind_chart(mock_chart_data)
        
        # Verify chart was created
        mock_chart_class.assert_called_once()
        
        # Verify data was loaded
        mock_chart_data.load_chart.assert_called_once_with(0)
        
        # Verify plotting functions were called
        mock_plot_chart.assert_called_once_with(mock_df, mock_metadata, mock_chart)
        mock_plot_indicators.assert_called_once_with(mock_df, mock_chart)
        
        # Verify hotkeys were bound
        assert mock_chart.hotkey.call_count == 3
        
        # Check hotkey bindings
        hotkey_calls = mock_chart.hotkey.call_args_list
        assert hotkey_calls[0][0][:3] == ("shift", 1)  # on_up
        assert hotkey_calls[1][0][:3] == ("shift", 2)  # on_down
        assert hotkey_calls[2][0][:3] == ("shift", "S")  # save_screenshot
        
        # Verify the chart is returned
        assert result is mock_chart


class TestOnMaximize:
    """Test cases for the on_maximize function."""

    def test_on_maximize_to_fullscreen(self):
        """Test maximizing a chart to fullscreen."""
        from src.ui import FULLSCREEN, CLOSE
        
        # Create mock charts
        target_chart = Mock()
        other_chart = Mock()
        charts = [target_chart, other_chart]
        
        # Mock the topbar button
        mock_button = Mock()
        mock_button.value = FULLSCREEN
        target_chart.topbar = {"max": mock_button}
        
        on_maximize(target_chart, charts)
        
        # Verify target chart is maximized (width=1.0)
        target_chart.resize.assert_called_once_with(1.0, 1.0)
        # Verify other chart is hidden (width=0.0)
        other_chart.resize.assert_called_once_with(0.0, 1.0)
        # Verify button changed to close symbol
        mock_button.set.assert_called_once_with(CLOSE)

    def test_on_maximize_restore_side_by_side(self):
        """Test restoring charts to side-by-side view."""
        from src.ui import FULLSCREEN, CLOSE
        
        # Create mock charts
        target_chart = Mock()
        other_chart = Mock()
        charts = [target_chart, other_chart]
        
        # Mock the topbar button (currently showing close)
        mock_button = Mock()
        mock_button.value = CLOSE
        target_chart.topbar = {"max": mock_button}
        
        on_maximize(target_chart, charts)
        
        # Verify both charts are restored to 50% width
        target_chart.resize.assert_called_once_with(0.5, 1.0)
        other_chart.resize.assert_called_once_with(0.5, 1.0)
        # Verify button changed to fullscreen symbol
        mock_button.set.assert_called_once_with(FULLSCREEN)


class TestOnTimeframeChange:
    """Test cases for the on_timeframe_change function."""

    @patch('src.ui.plot_chart')
    def test_on_timeframe_change_regular_chart_data(self, mock_plot_chart):
        """Test timeframe change with regular ChartsData."""
        mock_chart = Mock()
        mock_chart_data = Mock()
        mock_chart_data.current_index = 0
        # Explicitly remove set_timeframe attribute to simulate regular ChartsData
        del mock_chart_data.set_timeframe
        
        # Mock load_chart return - use a function to return fresh metadata each time
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        def mock_load_chart_func(index):
            return mock_df, {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data.load_chart.side_effect = mock_load_chart_func
        
        on_timeframe_change(mock_chart, mock_chart_data, "4H")
        
        # Verify timeframe is stored on chart
        assert mock_chart._timeframe == "4H"
        
        # Verify chart data was reloaded
        mock_chart_data.load_chart.assert_called_once_with(0)
        
        # Verify plot_chart was called (metadata should be modified in place)
        mock_plot_chart.assert_called_once()
        call_args = mock_plot_chart.call_args[0]
        assert call_args[1]['timeframe'] == "4H"  # timeframe should be updated
        assert call_args[1]['ticker'] == 'AAPL'
        assert call_args[2] == mock_chart
        pd.testing.assert_frame_equal(call_args[0], mock_df)

    @patch('src.ui.plot_chart')
    def test_on_timeframe_change_minute_chart_data(self, mock_plot_chart):
        """Test timeframe change with ChartsMinuteData."""
        mock_chart = Mock()
        mock_chart_data = Mock()
        mock_chart_data.current_index = 0
        mock_chart_data.set_timeframe = Mock()
        
        # Mock load_chart return
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'AAPL', 'timeframe': '1M', 'date_str': '2023-01-15'}
        mock_chart_data.load_chart.return_value = (mock_df, mock_metadata)
        
        on_timeframe_change(mock_chart, mock_chart_data, "5M")
        
        # Verify timeframe is stored on chart
        assert mock_chart._timeframe == "5M"
        
        # Verify set_timeframe was called on ChartsMinuteData
        mock_chart_data.set_timeframe.assert_called_once_with("5M")
        
        # Verify chart data was reloaded
        mock_chart_data.load_chart.assert_called_once_with(0)
        
        # Verify plot_chart was called (metadata should not be modified for ChartsMinuteData)
        mock_plot_chart.assert_called_once_with(mock_df, mock_metadata, mock_chart)

    @patch('src.ui.plot_chart')
    def test_on_timeframe_change_chart_without_timeframe_attribute(self, mock_plot_chart):
        """Test timeframe change when chart doesn't have _timeframe attribute."""
        mock_chart = Mock()
        # Remove _timeframe attribute if it exists
        if hasattr(mock_chart, '_timeframe'):
            delattr(mock_chart, '_timeframe')
        
        mock_chart_data = Mock()
        mock_chart_data.current_index = 0
        
        # Mock load_chart return
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data.load_chart.return_value = (mock_df, mock_metadata)
        
        on_timeframe_change(mock_chart, mock_chart_data, "1H")
        
        # Verify timeframe is set on chart
        assert mock_chart._timeframe == "1H"


class TestDualChartFunctions:
    """Test cases for dual chart functions."""

    @patch('src.ui.plot_chart')
    def test_on_up_dual(self, mock_plot_chart):
        """Test on_up_dual function."""
        mock_chart1 = Mock()
        mock_chart2 = Mock()
        mock_chart_data1 = Mock()
        mock_chart_data2 = Mock()
        
        # Mock next_chart returns
        mock_df1 = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata1 = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.next_chart.return_value = (mock_df1, mock_metadata1)
        
        mock_df2 = pd.DataFrame({'close': [200, 201, 202]})
        mock_metadata2 = {'ticker': 'MSFT', 'timeframe': '1M', 'date_str': '2023-01-15'}
        mock_chart_data2.next_chart.return_value = (mock_df2, mock_metadata2)
        
        on_up_dual(mock_chart1, mock_chart2, mock_chart_data1, mock_chart_data2)
        
        # Verify next_chart was called on both data sources
        mock_chart_data1.next_chart.assert_called_once()
        mock_chart_data2.next_chart.assert_called_once()
        
        # Verify plot_chart was called for both charts
        assert mock_plot_chart.call_count == 2
        
        # Check the calls manually to avoid DataFrame comparison issues
        calls = mock_plot_chart.call_args_list
        assert len(calls) == 2
        
        # First call should be for chart1
        call1_args = calls[0][0]
        assert call1_args[1] == mock_metadata1  # metadata
        assert call1_args[2] == mock_chart1     # chart
        pd.testing.assert_frame_equal(call1_args[0], mock_df1)  # dataframe
        
        # Second call should be for chart2
        call2_args = calls[1][0]
        assert call2_args[1] == mock_metadata2  # metadata
        assert call2_args[2] == mock_chart2     # chart
        pd.testing.assert_frame_equal(call2_args[0], mock_df2)  # dataframe

    @patch('src.ui.plot_chart')
    def test_on_down_dual(self, mock_plot_chart):
        """Test on_down_dual function."""
        mock_chart1 = Mock()
        mock_chart2 = Mock()
        mock_chart_data1 = Mock()
        mock_chart_data2 = Mock()
        
        # Mock previous_chart returns
        mock_df1 = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata1 = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.previous_chart.return_value = (mock_df1, mock_metadata1)
        
        mock_df2 = pd.DataFrame({'close': [200, 201, 202]})
        mock_metadata2 = {'ticker': 'MSFT', 'timeframe': '1M', 'date_str': '2023-01-15'}
        mock_chart_data2.previous_chart.return_value = (mock_df2, mock_metadata2)
        
        on_down_dual(mock_chart1, mock_chart2, mock_chart_data1, mock_chart_data2)
        
        # Verify previous_chart was called on both data sources
        mock_chart_data1.previous_chart.assert_called_once()
        mock_chart_data2.previous_chart.assert_called_once()
        
        # Verify plot_chart was called for both charts
        assert mock_plot_chart.call_count == 2
        
        # Check the calls manually to avoid DataFrame comparison issues
        calls = mock_plot_chart.call_args_list
        assert len(calls) == 2
        
        # First call should be for chart1
        call1_args = calls[0][0]
        assert call1_args[1] == mock_metadata1  # metadata
        assert call1_args[2] == mock_chart1     # chart
        pd.testing.assert_frame_equal(call1_args[0], mock_df1)  # dataframe
        
        # Second call should be for chart2
        call2_args = calls[1][0]
        assert call2_args[1] == mock_metadata2  # metadata
        assert call2_args[2] == mock_chart2     # chart
        pd.testing.assert_frame_equal(call2_args[0], mock_df2)  # dataframe

    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_save_screenshot_dual(self, mock_print, mock_file_open):
        """Test save_screenshot_dual function."""
        mock_chart1 = Mock()
        mock_chart2 = Mock()
        mock_chart_data1 = Mock()
        mock_chart_data2 = Mock()
        
        # Mock screenshot returns
        mock_chart1.screenshot.return_value = b'fake_image_data1'
        mock_chart2.screenshot.return_value = b'fake_image_data2'
        
        # Mock metadata returns
        mock_chart_data1.current_index = 0
        mock_chart_data1.get_metadata.return_value = {
            'ticker': 'AAPL',
            'date_str': '2023-01-15'
        }
        
        mock_chart_data2.current_index = 1
        mock_chart_data2.get_metadata.return_value = {
            'ticker': 'MSFT',
            'date_str': '2023-01-16'
        }
        
        save_screenshot_dual(mock_chart1, mock_chart2, mock_chart_data1, mock_chart_data2, "test_folder")
        
        # Verify screenshots were taken
        mock_chart1.screenshot.assert_called_once()
        mock_chart2.screenshot.assert_called_once()
        
        # Verify metadata was retrieved
        mock_chart_data1.get_metadata.assert_called_once_with(0)
        mock_chart_data2.get_metadata.assert_called_once_with(1)
        
        # Verify files were written
        expected_filename1 = "test_folder/AAPL_2023-01-15_chart1_screenshot.png"
        expected_filename2 = "test_folder/MSFT_2023-01-16_chart2_screenshot.png"
        
        assert mock_file_open.call_count == 2
        mock_file_open.assert_any_call(expected_filename1, "wb")
        mock_file_open.assert_any_call(expected_filename2, "wb")
        
        # Verify print message
        mock_print.assert_called_once_with(f"Screenshots saved to {expected_filename1} and {expected_filename2}")


class TestCreateDualChartGrid:
    """Test cases for the create_dual_chart_grid function."""

    @patch('src.ui.ChartsMinuteData')
    @patch('src.ui.Chart')
    @patch('src.ui.plot_chart')
    @patch('src.ui.plot_indicators')
    @patch('os.path.exists')
    def test_create_dual_chart_grid_with_minute_data(self, mock_exists, mock_plot_indicators, mock_plot_chart, mock_chart_class, mock_minute_data_class):
        """Test create_dual_chart_grid with automatic minute data creation."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Create mock chart_data1
        mock_chart_data1 = Mock()
        mock_chart_data1.dict_filename = "data/default.feather"
        mock_chart_data1.data_filename = "data/default_data.feather"
        mock_chart_data1.current_index = 0
        
        # Mock load_chart return for chart_data1
        mock_df1 = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata1 = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.load_chart.return_value = (mock_df1, mock_metadata1)
        
        # Create mock minute data instance
        mock_minute_data = Mock()
        mock_minute_data.current_index = 0
        mock_minute_data.current_timeframe = "1M"  # Add this attribute to make hasattr work
        mock_df2 = pd.DataFrame({'close': [200, 201, 202]})
        mock_metadata2 = {'ticker': 'AAPL', 'timeframe': '1M', 'date_str': '2023-01-15'}
        mock_minute_data.load_chart.return_value = (mock_df2, mock_metadata2)
        mock_minute_data_class.return_value = mock_minute_data
        
        # Create mock charts
        mock_main_chart = Mock()
        mock_right_chart = Mock()
        mock_main_chart.create_subchart.return_value = mock_right_chart
        mock_chart_class.return_value = mock_main_chart
        
        # Mock topbar components
        mock_main_chart.topbar = Mock()
        mock_right_chart.topbar = Mock()
        
        result = create_dual_chart_grid(mock_chart_data1)
        
        # Verify ChartsMinuteData was created with correct parameters
        mock_minute_data_class.assert_called_once_with(
            "data/default.feather", 
            "data/default_data_min.feather"
        )
        
        # Verify main chart was created
        mock_chart_class.assert_called_once_with(inner_width=0.5, inner_height=1.0)
        
        # Verify subchart was created
        mock_main_chart.create_subchart.assert_called_once_with(position="right", width=0.5, height=1.0)
        
        # Verify data was loaded for both charts
        mock_chart_data1.load_chart.assert_called_once_with(0)
        mock_minute_data.load_chart.assert_called_once_with(0)
        
        # Verify plotting functions were called
        assert mock_plot_chart.call_count == 2
        assert mock_plot_indicators.call_count == 2
        
        # Verify hotkeys were bound
        assert mock_main_chart.hotkey.call_count == 3
        
        # Verify the main chart is returned
        assert result is mock_main_chart

    @patch('src.ui.Chart')
    @patch('src.ui.plot_chart')
    @patch('src.ui.plot_indicators')
    def test_create_dual_chart_grid_with_provided_chart_data2(self, mock_plot_indicators, mock_plot_chart, mock_chart_class):
        """Test create_dual_chart_grid with provided chart_data2."""
        # Create mock chart data
        mock_chart_data1 = Mock()
        mock_chart_data1.current_index = 0
        mock_df1 = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata1 = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.load_chart.return_value = (mock_df1, mock_metadata1)
        
        mock_chart_data2 = Mock()
        mock_chart_data2.current_index = 0
        mock_df2 = pd.DataFrame({'close': [200, 201, 202]})
        mock_metadata2 = {'ticker': 'MSFT', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data2.load_chart.return_value = (mock_df2, mock_metadata2)
        
        # Create mock charts
        mock_main_chart = Mock()
        mock_right_chart = Mock()
        mock_main_chart.create_subchart.return_value = mock_right_chart
        mock_chart_class.return_value = mock_main_chart
        
        # Mock topbar components
        mock_main_chart.topbar = Mock()
        mock_right_chart.topbar = Mock()
        
        result = create_dual_chart_grid(mock_chart_data1, mock_chart_data2)
        
        # Verify both chart data sources were used
        mock_chart_data1.load_chart.assert_called_once_with(0)
        mock_chart_data2.load_chart.assert_called_once_with(0)
        
        # Verify the main chart is returned
        assert result is mock_main_chart

    @patch('src.ui.Chart')
    @patch('src.ui.plot_chart')
    @patch('src.ui.plot_indicators')
    def test_create_dual_chart_grid_fallback_no_data_filename(self, mock_plot_indicators, mock_plot_chart, mock_chart_class):
        """Test create_dual_chart_grid fallback when chart_data1 has no data_filename."""
        # Create mock chart data without data_filename attribute
        mock_chart_data1 = Mock()
        mock_chart_data1.current_index = 0
        # Remove data_filename attribute
        if hasattr(mock_chart_data1, 'data_filename'):
            delattr(mock_chart_data1, 'data_filename')
        
        mock_df = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.load_chart.return_value = (mock_df, mock_metadata)
        
        # Create mock charts
        mock_main_chart = Mock()
        mock_right_chart = Mock()
        mock_main_chart.create_subchart.return_value = mock_right_chart
        mock_chart_class.return_value = mock_main_chart
        
        # Mock topbar components
        mock_main_chart.topbar = Mock()
        mock_right_chart.topbar = Mock()
        
        result = create_dual_chart_grid(mock_chart_data1)
        
        # Verify same chart data was used for both charts (fallback behavior)
        assert mock_chart_data1.load_chart.call_count == 2
        
        # Verify the main chart is returned
        assert result is mock_main_chart

    @patch('src.ui.ChartsMinuteData')
    @patch('src.ui.Chart')
    @patch('src.ui.plot_chart')
    @patch('src.ui.plot_indicators')
    @patch('os.path.exists')
    def test_create_dual_chart_grid_non_feather_filename(self, mock_exists, mock_plot_indicators, mock_plot_chart, mock_chart_class, mock_minute_data_class):
        """Test create_dual_chart_grid with non-.feather filename."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Create mock chart_data1 with non-.feather filename
        mock_chart_data1 = Mock()
        mock_chart_data1.dict_filename = "data/default.feather"
        mock_chart_data1.data_filename = "data/default_data"  # No .feather extension
        mock_chart_data1.current_index = 0
        
        # Mock load_chart return for chart_data1
        mock_df1 = pd.DataFrame({'close': [100, 101, 102]})
        mock_metadata1 = {'ticker': 'AAPL', 'timeframe': '1D', 'date_str': '2023-01-15'}
        mock_chart_data1.load_chart.return_value = (mock_df1, mock_metadata1)
        
        # Create mock minute data instance
        mock_minute_data = Mock()
        mock_minute_data.current_index = 0
        mock_minute_data.current_timeframe = "1M"
        mock_df2 = pd.DataFrame({'close': [200, 201, 202]})
        mock_metadata2 = {'ticker': 'AAPL', 'timeframe': '1M', 'date_str': '2023-01-15'}
        mock_minute_data.load_chart.return_value = (mock_df2, mock_metadata2)
        mock_minute_data_class.return_value = mock_minute_data
        
        # Create mock charts
        mock_main_chart = Mock()
        mock_right_chart = Mock()
        mock_main_chart.create_subchart.return_value = mock_right_chart
        mock_chart_class.return_value = mock_main_chart
        
        # Mock topbar components
        mock_main_chart.topbar = Mock()
        mock_right_chart.topbar = Mock()
        
        result = create_dual_chart_grid(mock_chart_data1)
        
        # Verify ChartsMinuteData was created with correct parameters (should append _min.feather)
        mock_minute_data_class.assert_called_once_with(
            "data/default.feather", 
            "data/default_data_min.feather"
        )
        
        # Verify the main chart is returned
        assert result is mock_main_chart


class TestPlotChartWatermarkFallback:
    """Test cases for plot_chart watermark fallback scenarios."""

    def test_plot_chart_watermark_complete_failure(self):
        """Test chart plotting when all watermark attempts fail."""
        # Create mock chart that raises exceptions on all watermark calls
        mock_chart = Mock()
        mock_chart.watermark = Mock(side_effect=[
            TypeError("Custom watermark not available"),
            Exception("Standard watermark failed"),
            None  # Third call succeeds with "na"
        ])
        mock_chart.legend = Mock()
        
        df = pd.DataFrame({'close': [100, 101, 102]})
        metadata = {
            'ticker': 'AAPL',
            'timeframe': '1D',
            'date_str': '2023-01-15'
        }
        
        # Should not raise an exception
        plot_chart(df, metadata, mock_chart)
        
        # Should call watermark three times
        assert mock_chart.watermark.call_count == 3
        # The last call should be with "na"
        mock_chart.watermark.assert_called_with("na")