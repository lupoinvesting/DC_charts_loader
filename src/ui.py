from .models import ChartsData
from .models import ChartsWMOverride as Chart
from .config import config
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
            f"{metadata['ticker']} {metadata['timeframe']} {metadata['date_str']}",
            vert_align="top",
        )
    except AttributeError:
        chart.watermark(f"na")
    chart.legend(
        visible=True,
        ohlc=True,
        lines=True,
        font_family="arial",
        font_size=12,
        percent=False,
    )
    chart.price_line(line_visible=False)


def plot_line(data: pd.DataFrame, chart: Chart, name: str) -> None:

    line = chart.create_line(name=name, price_line=False)
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
