from src.models import ChartsDailyData
import pandas as pd
from lightweight_charts import Chart
from src.ui import on_up, on_down
import numpy as np


if __name__ == "__main__":
    dict_filename = "data/0008_80_pct_hl2_movers_scan_20030919_20250402.feather"
    data_filename = dict_filename.replace(".feather", "_data.feather")

    chart_data = ChartsDailyData(dict_filename, data_filename)
    print("Charts loaded:", len(chart_data.charts))

    df, metadata = chart_data.load_chart(0)

    chart = Chart()
    # chart.set(df)
    # chart.set(pd.concat([df.drop(columns=["ticker"]), df_random], ignore_index=True))
    chart.set(df)
    try:
        chart.watermark(f"{df.ticker.iloc[0]}")
    except AttributeError:
        chart.watermark(f"no data")
    chart.hotkey("shift", 1, func=lambda _: on_up(chart, chart_data))
    chart.hotkey("shift", 2, func=lambda _: on_down(chart, chart_data))
    chart.show(block=True)
