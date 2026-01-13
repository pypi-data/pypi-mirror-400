from collections import deque
from dataclasses import dataclass
from datetime import timedelta

import geopandas as gpd
import pandas as pd

from .utils import check_crs_unit


@dataclass
class SpatialFilter:
    pass

    def min_distance(
        self,
        gdf: gpd.GeoDataFrame | gpd.GeoSeries,
        epoch: timedelta | str,
        min_distance: float,
    ) -> pd.Series:
        check_crs_unit(gdf, "metre")

        seconds = pd.to_timedelta(epoch).total_seconds()
        min_distance = min_distance / (60 / seconds)

        geometry = gdf.geometry

        keep_pts = [gdf.index[0]]  # Keep first point, always.
        prev_pt = geometry.iloc[0]

        for idx, pt in geometry.items():
            distance = pt.distance(prev_pt)  # type: ignore

            if distance >= min_distance:
                keep_pts.append(idx)
                prev_pt = pt

        keep_pts.append(gdf.index[-1])  # Keep last point, always.

        valid = pd.Series(False, index=gdf.index, name="valid")
        valid[keep_pts] = True

        return valid

    def stop_detector(
        self, gdf: gpd.GeoDataFrame, max_radius: float, min_duration: str | timedelta
    ) -> pd.Series:
        check_crs_unit(gdf, "metre")

        gdf = gdf[~gdf.is_empty]  # Select only non-empty geometries.
        min_duration = pd.Timedelta(min_duration)

        stops = pd.Series(False, index=gdf.index, name="stop", dtype=bool)
        buffer = deque()

        for dt in gdf.index:
            buffer.append(dt)

            if dt - buffer[0] >= min_duration:
                selected_rows = gdf[buffer[0] : dt]
                centroid = selected_rows.geometry.union_all().centroid

                for row in selected_rows.geometry:
                    distance = centroid.distance(row)
                    if distance > max_radius:
                        break
                else:
                    stops.loc[selected_rows.index] = (
                        True  # Set all rows in the selected range to True.
                    )

                buffer.popleft()

        # stops = stops.reindex(
        #     df.index
        # )  # Reindex to original DataFrame, so that empty geometries are also included (NaN).

        return stops
