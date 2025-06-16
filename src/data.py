import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from pandera import check_output
from typing import Optional

from src.schemas import dict_schema, min_schema, min_chart_schema
from src.config import config

N_DAYS = 30  # Number of days to load for each chart


def load_daily_data(ticker: str, date: datetime, data: pd.DataFrame) -> pd.DataFrame:
    """
    Loads a subset of daily data for a given ticker and date range.
    Parameters:
        ticker (str): The ticker symbol to filter the data.
        date (datetime): The reference date around which to load data.
        data (pd.DataFrame): The DataFrame containing at least 'ticker' and 'date' columns.
    Returns:
        pd.DataFrame: A DataFrame containing rows for the specified ticker,
        with 'date' within ±N_DAYS of the given date, sorted by date and with reset index.

    """

    n_days = timedelta(days=N_DAYS)

    conditions = [
        (data["ticker"] == ticker),
        (data["date"] >= date - n_days),
        (data["date"] <= date + n_days),
    ]

    # Merge or process as needed, here we just return the data
    result = data.loc[np.logical_and.reduce(conditions)].copy()
    result.sort_values(by="date", inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result


@check_output(dict_schema)
def load_daily_df(dict_filename: str) -> pd.DataFrame:
    """
    Reads and validates dictionary data from a Feather file.
    Args:
        dict_filename (str): Path to the Feather file.
    Returns:
        pd.DataFrame: Validated DataFrame.
    """
    df = pd.read_feather(dict_filename)
    df = df.drop_duplicates(subset=["ticker", "date"])
    df.volume = df.volume.astype("int64")  # Ensure volume is int64
    df.sort_values(by=["ticker", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    indicators_list = config.indicators if config.indicators is not None else []
    df_grouped = df.groupby("ticker", observed=True)
    for indicator in indicators_list:
        if indicator.name == "SMA":
            if indicator.parameters is not None and "period" in indicator.parameters:
                period = indicator.parameters["period"]
                col_name = f"SMA_{period}"
                df[col_name] = df_grouped["close"].transform(
                    lambda x: x.rolling(window=period).mean()
                )

    return df


@check_output(min_schema)
def load_min_data(data_filename: str) -> pd.DataFrame:
    """
    Reads and validates minute data from a Feather file.
    Args:
        data_filename (str): Path to the Feather file.
    Returns:
        pd.DataFrame: Validated DataFrame with 'datetime' as index.
    """
    df = pd.read_feather(data_filename)
    df["datetime_u"] = df["datetime"].dt.tz_localize(None)
    df.drop(columns=["datetime"], inplace=True)
    df.rename(columns={"datetime_u": "datetime", "date": "_date"}, inplace=True)
    df.sort_values(by=["ticker", "datetime"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def load_min_chart(ticker: str, date, data: pd.DataFrame, n_days=None) -> pd.DataFrame:
    """
    Loads a subset of daily data for a given ticker and date range.
    Parameters:
        ticker (str): The ticker symbol to filter the data.
        date (datetime): The reference date around which to load data.
        data (pd.DataFrame): The DataFrame containing at least 'ticker' and 'date' columns.
    Returns:
        pd.DataFrame: A DataFrame containing rows for the specified ticker,
        with 'date' within ±N_DAYS of the given date, sorted by date and with reset index.

    """
    n_days = n_days if n_days is not None else config.chart.n_days_intraday
    n_days = pd.Timedelta(days=n_days)

    conditions = [
        (data["ticker"] == ticker),
        (data["datetime"] >= date - n_days),
        (data["datetime"] <= date + n_days),
    ]

    # Merge or process as needed, here we just return the data
    result = data.loc[np.logical_and.reduce(conditions)].copy()
    # result["time"] = result["datetime"].astype(str)
    # # result["_date"] = result["_date"].astype(str)
    # result.drop(columns=["_date", "datetime"], inplace=True)
    return format_min_chart_data(result)


@check_output(min_chart_schema)
def format_min_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats the minute chart data for display.
    Args:
        df (pd.DataFrame): The DataFrame containing minute chart data.
    Returns:
        pd.DataFrame: Formatted DataFrame with 'time' as string and 'datetime' as index.
    """
    df["time"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    columns_to_drop = ["datetime"]
    if "_date" in df.columns:
        columns_to_drop.append("_date")
    df.drop(columns=columns_to_drop, inplace=True)
    return df
