from .models import ChartsData
from lightweight_charts import Chart
import pandas as pd


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
        chart.watermark(
            f"{metadata['ticker']} {metadata['timeframe']} {metadata['date_str']}"
        )
    except AttributeError:
        chart.watermark(f"na")


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
    chart.hotkey("shift", 1, func=lambda _: on_up(chart, chart_data))
    chart.hotkey("shift", 2, func=lambda _: on_down(chart, chart_data))
    chart.hotkey("shift", "S", func=lambda _: save_screenshot(chart, chart_data))
    return chart
