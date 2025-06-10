from src.models import ChartsDailyData
import pandas as pd
from lightweight_charts import Chart
from src.ui import on_up, on_down, plot_chart, save_screenshot, create_and_bind_chart
import numpy as np


if __name__ == "__main__":
    dict_filename = "data/default.feather"

    data_filename = dict_filename.replace(".feather", "_data.feather")

    chart_data = ChartsDailyData(dict_filename, data_filename)

    chart = create_and_bind_chart(chart_data)
    chart.show(block=True)
