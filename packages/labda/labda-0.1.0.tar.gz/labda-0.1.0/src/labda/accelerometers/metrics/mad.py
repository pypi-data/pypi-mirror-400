from datetime import timedelta

import numpy as np
import pandas as pd


def get_mad(
    df: pd.DataFrame,
    epoch: timedelta,
) -> pd.Series:
    # Calculate vector magnitude
    df = pd.Series(
        np.linalg.norm(df.values, axis=1), name="vm", index=df.index
    ).to_frame("vm")

    # Calculate the epoch mean
    df["epoch_mean"] = df["vm"].groupby(pd.Grouper(freq=epoch)).transform("mean")

    # Calculate the mean absolute deviation
    df["diff"] = np.abs(df["vm"] - df["epoch_mean"])
    mad = df["diff"].resample(epoch).mean().fillna(0)
    mad.name = "mad"

    return mad.astype("float32") * 1000  # Convert to mg units
