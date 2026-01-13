from datetime import timedelta

import numpy as np
import pandas as pd

from ...core import SamplingFrequency
from ...core.utils import rle


def get_vilpa(
    vpa: pd.Series,
    epoch: timedelta,
    min_duration: int,
    min_epochs: int,
    max_duration: int,
) -> pd.Series:
    """Input series must be boolean with 1-second epoch and no missing data marking VPA epochs."""

    df = vpa.to_frame("vpa")
    epoch = SamplingFrequency().compute_epoch(df)

    if epoch != timedelta(seconds=1):
        raise ValueError(f"Only 1-second epoch is supported, got {epoch}.")

    if len(df.resample("1s").asfreq()) != len(df):
        raise ValueError("Input series must not have missing data.")

    df["vilpa"] = (
        df["vpa"].rolling(window=min_duration, center=True).sum() >= min_epochs
    )
    df["vilpa"] = df["vilpa"].astype(int).replace(0, np.nan)
    df["vilpa"] = (
        df["vilpa"].bfill(limit=min_duration - 1).replace(np.nan, 0).astype(bool)
    )

    df["rle"] = rle(df["vilpa"])
    bouts_lengths = df.loc[df["vilpa"]].groupby("rle").size()
    long_bouts = bouts_lengths[bouts_lengths >= max_duration].index

    df["bout"] = "other"
    df.loc[df["vilpa"], "bout"] = "vilpa"
    df.loc[df["rle"].isin(long_bouts), "bout"] = "long-vpa"

    categorical = pd.CategoricalDtype(
        categories=["non-wear", "other", "vilpa", "long-vpa"]
    )
    df["bout"] = df["bout"].astype(categorical)

    return df["bout"]
