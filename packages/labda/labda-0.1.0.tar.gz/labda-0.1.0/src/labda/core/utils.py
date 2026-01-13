from datetime import datetime, time
from typing import Any

import pandas as pd


def check_for_required_data(required_data: list[str] | str, columns: Any) -> None:
    if isinstance(required_data, str):
        required_data = [required_data]

    missing = [col for col in required_data if col not in columns]
    if missing:
        raise ValueError(
            f"Required data '{', '.join(missing)}' not found in the dataframe. Please check the input data and if the column exists, name it accordingly."
        )


def parse_datetime_or_time(value: str | time | datetime) -> datetime | time:
    if isinstance(value, datetime) or isinstance(value, time):
        return value

    try:
        return datetime.strptime(value, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        return datetime.strptime(value, "%H:%M:%S").time()


# def parse_time(time: str | time) -> time:
#     if isinstance(time, str):
#         return pd.to_datetime(time).time()

#     return time


def rle(series: pd.Series) -> pd.Series:
    """
    Run-length encoding for a pandas Series.
    """
    rle = (series != series.shift()).cumsum()
    return rle


def format_seconds(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def format_to_excel(df: pd.DataFrame, index: bool = True) -> pd.DataFrame:
    df = df.copy()
    if index:
        df.reset_index(inplace=True)

    dt_cols = df.select_dtypes(include=["datetime64", "datetimetz"])
    for col in dt_cols:
        df[col] = df[col].dt.tz_localize(None)

    td_cols = df.select_dtypes(include=["timedelta64"])
    for col in td_cols:
        df[col] = df[col].fillna(pd.Timedelta(0))
        df[col] = df[col].dt.total_seconds().apply(format_seconds)

    return df
