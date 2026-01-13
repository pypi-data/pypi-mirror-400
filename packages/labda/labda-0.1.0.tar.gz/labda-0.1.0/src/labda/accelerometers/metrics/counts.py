from datetime import timedelta

import numpy as np
import pandas as pd
import resampy
from agcounts import extract

from ...core.expander import Expander
from ...core.filter import Filter

AG_BASE_FREQUENCY = 30  # Hz, ActiGraph base frequency for counts calculation


def _get_1s_epochs(df: pd.DataFrame, sampling_frequency: float) -> pd.DataFrame:
    """Extract 1-second counts from accelerometer data."""

    # Extract and resample accelerometer data efficiently
    time = df.index  # Keep the original time index
    acc_data = [
        resampy.resample(
            df[col].values, sampling_frequency, AG_BASE_FREQUENCY, parallel=True
        )
        for col in df.columns
    ]
    acc_data = np.column_stack(acc_data)
    del df

    # Calculate counts using agcounts with error handling
    counts_array = extract.get_counts(acc_data, freq=AG_BASE_FREQUENCY, epoch=1)

    # Generate time index more efficiently
    n_epochs = len(counts_array)
    epoch_duration = pd.Timedelta(seconds=1)

    # Create index starting from first timestamp, with proper epoch alignment
    start_time = time[0].floor(epoch_duration)
    time = pd.date_range(start=start_time, periods=n_epochs, freq=epoch_duration)
    time.name = "datetime"

    # Create result DataFrame with appropriate dtype for counts (integers)
    return pd.DataFrame(
        counts_array,
        index=time,
        columns=["counts_x", "counts_y", "counts_z"],
        dtype=np.int32,
    )


def _fix_time_alignment_issues(df: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    """Fix time alignment issues in counts DataFrame by interpolating missing epochs."""

    epoch = timedelta(seconds=1)
    # Interpolate to ensure all epochs are represented, fixes time alignment issues
    start = df.index[0].floor(epoch)
    end = df.index[-1].floor(epoch)
    datetimes = pd.date_range(start=start, end=end, freq=epoch)
    datetimes.name = "datetime"
    counts = pd.DataFrame(
        {
            col: np.interp(datetimes, counts.index, counts[col])
            for col in counts.columns
        },
        index=datetimes,
        dtype=np.int32,
    )
    return counts


def get_counts(
    df: pd.DataFrame,
    sampling_frequency: float,
    epoch: timedelta,
) -> pd.DataFrame:
    # Counts are firstly calculated for 1-second epochs, then resampled to the desired epoch length.
    # The reason for this is that interpolation on 1-second epochs doesn't introduce significant errors,
    # while it allows to fix time alignment issues (drift).

    timedeltas = Expander().timedelta(df)
    intervals = Filter().gap_splitter(timedeltas, duration=timedelta(seconds=1))

    counts = []

    for _, temp in df.groupby(intervals):
        if temp.index[-1] - temp.index[0] < timedelta(seconds=5):
            continue

        epochs = _get_1s_epochs(temp, sampling_frequency)
        epochs = _fix_time_alignment_issues(temp, epochs)
        counts.append(epochs)

    counts = pd.concat(counts)
    counts = counts.resample(epoch).sum().fillna(0)
    counts["counts_vm"] = np.linalg.norm(counts, axis=1).astype(np.float32)

    return counts
