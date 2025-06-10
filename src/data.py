import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from src.schemas import dict_schema
from pandera import check_output

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
    df.sort_values(by=["ticker", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
