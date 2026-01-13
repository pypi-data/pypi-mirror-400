from dataclasses import dataclass
from datetime import timedelta

import pandas as pd

from .counts import get_counts
from .enmo import get_enmo
from .mad import get_mad


@dataclass
class Metrics:
    output_epoch: timedelta

    def __post_init__(self) -> None:
        self.output_epoch = pd.Timedelta(self.output_epoch).to_pytimedelta()

    def enmo(
        self,
        df: pd.DataFrame,
        absolute: bool = False,
        trim: bool = True,
    ) -> pd.Series:
        return get_enmo(df, epoch=self.output_epoch, absolute=absolute, trim=trim)

    def mad(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        return get_mad(df, epoch=self.output_epoch)

    def counts(
        self,
        df: pd.DataFrame,
        hertz: float,
    ) -> pd.DataFrame:
        return get_counts(df, sampling_frequency=hertz, epoch=self.output_epoch)
