from src.models import ChartsDailyData
from src.ui import create_and_bind_chart
from src.config import config


if __name__ == "__main__":
    path = config.general.data_path
    filename = config.general.data_filename
    dict_filename = f"{path}/{filename}"
    # dict_filename =
    data_filename = dict_filename.replace(".feather", "_data.feather")
    chart_data = ChartsDailyData(dict_filename, data_filename)
    chart = create_and_bind_chart(chart_data)
    chart.show(block=True)
