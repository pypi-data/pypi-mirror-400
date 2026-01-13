from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

import numpy as np
import pandas as pd
from scipy import signal

from .expander import Expander
from .sampling_frequency import SamplingFrequency


@dataclass
class Filter:
    pass

    def iqr(self, series: pd.Series, alpha: int = 3) -> pd.Series:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - alpha * iqr
        upper_bound = q3 + alpha * iqr

        series = series.loc[(series >= lower_bound) & (series <= upper_bound)]

        return series

    def gap_splitter(
        self, timedelta: pd.Series, duration: str | timedelta
    ) -> pd.Series:
        duration = pd.Timedelta(duration)

        diff = timedelta > duration
        gaps = diff.cumsum()
        gaps.name = "gaps"

        return gaps

    def bandpass(
        self,
        df: pd.DataFrame | pd.Series,
        filter_type: Literal["low", "high", "band"],
        cut_off: float | tuple[float, float],
        order: int = 4,
    ) -> pd.DataFrame | pd.Series:
        if isinstance(cut_off, tuple) and filter_type != "band":
            raise ValueError("Parameter 'cut_off' should be a tuple for 'band'.")

        df = df.copy()
        timedeltas = Expander().timedelta(df)
        intervals = Filter().gap_splitter(timedeltas, duration=timedelta(seconds=1))

        sf = SamplingFrequency(round_to_nearest=1).compute_hertz(df)
        nyquist = 0.5 * sf

        if isinstance(cut_off, tuple):
            cut_off = (cut_off[0] / nyquist, cut_off[1] / nyquist)
        else:
            cut_off = cut_off / nyquist

        for _, temp in df.groupby(intervals):
            if temp.index[-1] - temp.index[0] < timedelta(seconds=5):
                continue

            sos = signal.butter(
                order, cut_off, btype=filter_type, analog=False, output="sos"
            )
            filtered = signal.sosfiltfilt(sos, temp.values, axis=0).astype(np.float32)
            df.loc[temp.index, df.columns] = filtered

        return df
