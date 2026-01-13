from dataclasses import dataclass
from datetime import timedelta

import geopandas as gpd
import pandas as pd


@dataclass
class Exposures:
    window: timedelta | str = "1d"

    def __post_init__(self):
        if isinstance(self.window, str):
            self.window = pd.Timedelta(self.window).to_pytimedelta()

    def compute(self, df: pd.DataFrame | gpd.GeoDataFrame, epoch: timedelta):
        window = pd.Grouper(freq=self.window, sort=True)  # type: ignore
        group = [window] + df.columns.to_list()

        exposures = df.groupby(group, observed=False, dropna=False).size() * epoch
        exposures.name = "duration"
        exposures = exposures.reset_index(level=exposures.index.names[1:])

        return exposures
