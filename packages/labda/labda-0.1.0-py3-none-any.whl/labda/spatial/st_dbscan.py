from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN


@dataclass
class ST_DBSCAN:
    distance: float
    time: timedelta | str
    samples: int
    metric: Literal["euclidean"] = "euclidean"

    def __post_init__(self):
        self.time = pd.to_timedelta(self.time)

    def fit(self, gdf: gpd.GeoDataFrame | gpd.GeoSeries) -> pd.Series:
        coords = gdf.geometry.get_coordinates().to_numpy(dtype=np.float64)
        timestamps = (gdf.index.astype(np.int64) // 10**9).to_numpy()

        # Precompute the pairwise time and euclidean distances
        time_dist = pdist(
            timestamps.reshape(-1, 1), metric=self.metric
        )  # Pairwise time differences
        euc_dist = pdist(coords, metric=self.metric)  # Pairwise euclidean distances
        del coords, timestamps

        dist = np.where(
            time_dist <= self.time.total_seconds(),  # type: ignore
            euc_dist,
            2 * self.distance,
        )
        dist = squareform(dist)
        del time_dist, euc_dist

        db = DBSCAN(eps=self.distance, min_samples=self.samples, metric="precomputed")
        db.fit(dist)

        clusters = pd.Series(db.labels_, index=gdf.index, name="cluster")
        clusters = clusters.replace(-1, np.nan)

        return clusters
