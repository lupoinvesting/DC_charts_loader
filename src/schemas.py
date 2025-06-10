from pandera import Column, DataFrameSchema, Check
from numpy import datetime64, float32

dict_schema = DataFrameSchema(
    {
        "ticker": Column(str, nullable=False),
        "date": Column(datetime64, nullable=False),
        "open": Column(float32, Check.greater_than_or_equal_to(0.0), nullable=False),
        "high": Column(float32, Check.greater_than_or_equal_to(0.0), nullable=False),
        "low": Column(float32, Check.greater_than_or_equal_to(0.0), nullable=False),
        "close": Column(float32, Check.greater_than_or_equal_to(0.0), nullable=False),
        "volume": Column(int, Check.greater_than_or_equal_to(0), nullable=False),
    },
    strict="filter",
)
