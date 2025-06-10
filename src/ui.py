from .models import ChartsData
from lightweight_charts import Chart
import pandas as pd


def on_up(chart: Chart, chart_data: ChartsData):
    print("Next chart")
    print(f"Current index: {chart_data.current_index}")
    df, metadata = chart_data.next_chart()
    plot_chart(df, metadata, chart)


def on_down(chart: Chart, chart_data: ChartsData):
    print("Previous chart")
    print(f"Current index: {chart_data.current_index}")
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
        chart.watermark(f"{metadata['ticker']} {metadata['date']}")
    except AttributeError:
        chart.watermark(f"na")


# def print_chart(df: pd.DataFrame):
#     print("Chart data:")
#     print(df.head())
#     print(f"Ticker: {df.ticker.iloc[0]}")
#     print(f"Date: {df.date.iloc[0]}")
#     print(f"Shape: {df.shape}")
#     print(f"Columns: {df.columns.tolist()}")
#     print(f"Data types:\n{df.dtypes}")
