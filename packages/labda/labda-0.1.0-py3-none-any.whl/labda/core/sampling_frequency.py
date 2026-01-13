from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd


@dataclass
class SamplingFrequency:
    samples: int | None = 10_000
    round_to_nearest: float | None = 0.5

    def _compute(
        self,
        df: pd.DataFrame | pd.Series,
    ) -> float:
        # Use subset of data for efficiency
        time_subset = df.index[: self.samples] if self.samples else df.index

        if len(time_subset) < 2:
            raise ValueError(
                "DataFrame must have at least 2 samples to calculate sampling frequency."
            )

        # Convert to nanoseconds then to seconds for time differences
        time_diffs_seconds = pd.Series(np.diff(time_subset.astype("int64")) / 1e9)

        sf = time_diffs_seconds.mode().values[0]

        if sf <= 0:
            raise ValueError("Invalid time intervals detected in data.")

        return sf

    def compute_hertz(self, df: pd.DataFrame | pd.Series) -> float:
        """Compute sampling frequency in Hertz."""
        sf = self._compute(df)

        sf = 1.0 / sf
        if self.round_to_nearest and self.round_to_nearest > 0:
            sf = round(sf / self.round_to_nearest) * self.round_to_nearest

        return sf

    def compute_epoch(self, df: pd.DataFrame | pd.Series) -> timedelta:
        """Compute sampling frequency in epochs."""
        sf = self._compute(df)

        sf = timedelta(seconds=sf).total_seconds()
        if self.round_to_nearest and self.round_to_nearest > 0:
            sf = round(sf / self.round_to_nearest) * self.round_to_nearest

        sf = timedelta(seconds=sf)

        return sf
