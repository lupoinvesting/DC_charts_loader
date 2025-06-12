from .models import ChartsData
from .models import ChartsWMOverride as Chart
from .config import config
import pandas as pd

# ASCII symbols for maximize/minimize buttons
FULLSCREEN = '⬜'
CLOSE = '×'


def on_up(chart: Chart, chart_data: ChartsData):
    df, metadata = chart_data.next_chart()
    plot_chart(df, metadata, chart)


def on_down(chart: Chart, chart_data: ChartsData):
    df, metadata = chart_data.previous_chart()
    plot_chart(df, metadata, chart)


def plot_chart(df: pd.DataFrame, metadata: dict, chart: Chart) -> None:
    """
    Plots the chart using the provided chart data.
    :param chart: The Chart object to plot data on.
    :param chart_data: The ChartsData object containing the data.
    """
    chart.set(df)
    try:
        # Try to use custom watermark with vert_align (for ChartsWMOverride)
        chart.watermark(
            f"{metadata['ticker']} {metadata['timeframe']} {metadata['date_str']}",
            vert_align="top",
        )
    except (AttributeError, TypeError):
        # Fallback to standard watermark (for regular Chart or subcharts)
        try:
            chart.watermark(f"{metadata['ticker']} {metadata['timeframe']} {metadata['date_str']}")
        except:
            chart.watermark("na")
    chart.legend(
        visible=True,
        ohlc=True,
        lines=True,
        font_family="arial",
        font_size=12,
        percent=False,
    )


def plot_line(data: pd.DataFrame, chart: Chart, name: str) -> None:

    line = chart.create_line(name=name)
    line.set(data)


def save_screenshot(chart: Chart, chart_data: ChartsData, folder="screenshots") -> None:

    img = chart.screenshot()
    metadata = chart_data.get_metadata(chart_data.current_index)
    filename = f"{folder}/{metadata['ticker']}_{metadata['date_str']}_screenshot.png"
    with open(filename, "wb") as f:
        f.write(img)
    print(f"Screenshot saved to {filename}")


def create_and_bind_chart(
    chart_data: ChartsData,
) -> Chart:
    """
    Creates a Chart object, plots data onto it, and binds hotkeys for user interactions.

    Args:
        df (pd.DataFrame): The data to be plotted on the chart.
        metadata (dict): Metadata information used for plotting the chart.
        chart_data (ChartsDailyData): Chart data object used by hotkey callback functions.

    Returns:
        Chart: The configured Chart object with hotkeys bound.

    Hotkeys:
        Shift+1: Triggers the `on_up` callback.
        Shift+2: Triggers the `on_down` callback.
        Shift+S: Triggers the `save_screenshot` callback.
    """
    chart = Chart()
    df, metadata = chart_data.load_chart(0)
    plot_chart(df, metadata, chart)
    plot_indicators(df, chart)

    # bind hotkeys
    chart.hotkey("shift", 1, func=lambda _: on_up(chart, chart_data))
    chart.hotkey("shift", 2, func=lambda _: on_down(chart, chart_data))
    chart.hotkey("shift", "S", func=lambda _: save_screenshot(chart, chart_data))
    return chart


def plot_indicators(df: pd.DataFrame, chart: Chart) -> None:
    """
    Plots indicators on the chart.
    :param df: DataFrame containing the data with indicators.
    :param chart: The Chart object to plot indicators on.
    """
    indicators_list = config.indicators if config.indicators is not None else []
    for indicator in indicators_list:
        if indicator.name == "SMA":
            if indicator.parameters is not None and "period" in indicator.parameters:
                period = indicator.parameters["period"]
                col_name = f"SMA_{period}"
                if col_name in df.columns:
                    plot_line(df[["date", col_name]], chart, col_name)


def on_maximize(target_chart, charts):
    """
    Handles maximize/minimize functionality for charts.
    """
    button = target_chart.topbar['max']
    if button.value == CLOSE:
        # Restore to side-by-side view
        for chart in charts:
            chart.resize(0.5, 1.0)
        button.set(FULLSCREEN)
    else:
        # Maximize target chart
        for chart in charts:
            width = 1.0 if chart == target_chart else 0.0
            chart.resize(width, 1.0)
        button.set(CLOSE)


def on_timeframe_change(chart, chart_data, timeframe):
    """
    Handles timeframe switching for a chart.
    """
    # Store current timeframe in chart metadata
    if not hasattr(chart, '_timeframe'):
        chart._timeframe = '1D'
    
    chart._timeframe = timeframe
    
    # Reload current chart with new timeframe
    df, metadata = chart_data.load_chart(chart_data.current_index)
    metadata['timeframe'] = timeframe
    plot_chart(df, metadata, chart)


def on_up_dual(chart1, chart2, chart_data1, chart_data2):
    """Navigate to next chart for dual chart setup."""
    df1, metadata1 = chart_data1.next_chart()
    plot_chart(df1, metadata1, chart1)
    
    df2, metadata2 = chart_data2.next_chart()
    plot_chart(df2, metadata2, chart2)


def on_down_dual(chart1, chart2, chart_data1, chart_data2):
    """Navigate to previous chart for dual chart setup."""
    df1, metadata1 = chart_data1.previous_chart()
    plot_chart(df1, metadata1, chart1)
    
    df2, metadata2 = chart_data2.previous_chart()
    plot_chart(df2, metadata2, chart2)


def save_screenshot_dual(chart1, chart2, chart_data1, chart_data2, folder="screenshots"):
    """Save screenshots for both charts."""
    # Save screenshot for chart 1
    img1 = chart1.screenshot()
    metadata1 = chart_data1.get_metadata(chart_data1.current_index)
    filename1 = f"{folder}/{metadata1['ticker']}_{metadata1['date_str']}_chart1_screenshot.png"
    with open(filename1, "wb") as f:
        f.write(img1)
    
    # Save screenshot for chart 2
    img2 = chart2.screenshot()
    metadata2 = chart_data2.get_metadata(chart_data2.current_index)
    filename2 = f"{folder}/{metadata2['ticker']}_{metadata2['date_str']}_chart2_screenshot.png"
    with open(filename2, "wb") as f:
        f.write(img2)
    
    print(f"Screenshots saved to {filename1} and {filename2}")


def create_dual_chart_grid(chart_data1: ChartsData, chart_data2: ChartsData = None) -> Chart:
    """
    Creates a grid of 2 charts side by side with timeframe switching and maximize/minimize functionality.
    
    Args:
        chart_data1 (ChartsData): Data for the left chart
        chart_data2 (ChartsData): Data for the right chart (optional, defaults to same as chart_data1)
    
    Returns:
        Chart: The main chart object with dual chart setup
        
    Features:
        - Side-by-side layout (50% width each)
        - Maximize/minimize buttons for each chart
        - Timeframe switching (1D, 4H, 1H, 15M, 5M, 1M)
        - Navigation hotkeys (Shift+1/2 for next/previous)
        - Screenshot functionality (Shift+S)
    """
    # Use same data for both charts if second data source not provided
    if chart_data2 is None:
        chart_data2 = chart_data1
    
    # Create main chart (left side) using custom Chart class
    main_chart = Chart(inner_width=0.5, inner_height=1.0)
    
    # Create subchart (right side)
    right_chart = main_chart.create_subchart(position='right', width=0.5, height=1.0)
    
    charts = [main_chart, right_chart]
    chart_data_list = [chart_data1, chart_data2]
    
    # Available timeframes
    timeframes = ['1D', '4H', '1H', '15M', '5M', '1M']
    
    # Setup each chart
    for i, (chart, chart_data) in enumerate(zip(charts, chart_data_list)):
        chart_number = str(i + 1)
        
        # Load initial data
        df, metadata = chart_data.load_chart(0)
        plot_chart(df, metadata, chart)
        plot_indicators(df, chart)
        
        # Add chart identifier
        chart.topbar.textbox('number', f'Chart {chart_number}')
        
        # Add maximize/minimize button
        chart.topbar.button(
            'max', 
            FULLSCREEN, 
            False, 
            align='right', 
            func=lambda target_chart=chart: on_maximize(target_chart, charts)
        )
        
        # Add timeframe selector
        chart.topbar.switcher(
            'timeframe',
            options=timeframes,
            default='1D',
            align='right',
            func=lambda timeframe, target_chart=chart, target_data=chart_data: 
                on_timeframe_change(target_chart, target_data, timeframe)
        )
        
        # Add separator
        chart.topbar.textbox('sep', ' | ', align='right')
    
    # Bind global hotkeys to main chart
    main_chart.hotkey(
        "shift", 1, 
        func=lambda _: on_up_dual(main_chart, right_chart, chart_data1, chart_data2)
    )
    main_chart.hotkey(
        "shift", 2, 
        func=lambda _: on_down_dual(main_chart, right_chart, chart_data1, chart_data2)
    )
    main_chart.hotkey(
        "shift", "S", 
        func=lambda _: save_screenshot_dual(main_chart, right_chart, chart_data1, chart_data2)
    )
    
    return main_chart
