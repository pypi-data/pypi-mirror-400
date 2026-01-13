from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd

from ..core.expander import Expander
from .utils import check_crs_unit


@dataclass
class SpatialExpander(Expander):
    pass

    def _get_wgs84_geometry(
        self, gdf: gpd.GeoDataFrame | gpd.GeoSeries
    ) -> gpd.GeoSeries:
        return gdf.geometry.copy().to_crs("EPSG:4326")

    def distance(self, gdf: gpd.GeoDataFrame | gpd.GeoSeries) -> pd.Series:
        check_crs_unit(gdf, "metre")

        distance = gdf.distance(gdf.shift(1))  # type: ignore
        distance.name = "distance"
        distance.iat[0] = 0

        return distance.astype(np.float32)

    def speed(
        self, gdf: gpd.GeoDataFrame | gpd.GeoSeries, precomputed: bool = False
    ) -> pd.Series:
        check_crs_unit(gdf, "metre")

        if not precomputed:
            distance = self.distance(gdf)
            timedelta = self.timedelta(gdf)
        else:
            timedelta = gdf["timedelta"]
            distance = gdf["distance"]

        speed = distance / timedelta.dt.total_seconds()  # type: ignore
        speed = speed * 3.6  # Convert to km/h
        speed.name = "speed"
        speed.iat[0] = 0

        return speed.astype(np.float32)

    def acceleration(
        self, gdf: gpd.GeoDataFrame | gpd.GeoSeries, precomputed: bool = False
    ) -> pd.Series:
        check_crs_unit(gdf, "metre")

        if not precomputed:
            distance = self.distance(gdf)
            timedelta = self.timedelta(gdf)
        else:
            timedelta = gdf["timedelta"]
            distance = gdf["distance"]

        acceleration = distance.diff(1) / timedelta.dt.total_seconds()  # type: ignore
        acceleration.name = "acceleration"
        acceleration.iat[0] = 0

        return acceleration.astype(np.float32)

    def bearing(self, gdf: gpd.GeoDataFrame | gpd.GeoSeries) -> pd.Series:
        geometry = self._get_wgs84_geometry(gdf)

        lat1 = np.radians(geometry.y)
        lon1 = np.radians(geometry.x)
        del geometry

        lat2 = lat1.shift(1)  # type: ignore
        lon2 = lon1.shift(1)  # type: ignore

        delta = lon2 - lon1
        x = np.sin(delta) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta)
        del delta, lat1, lat2, lon1, lon2

        bearing = np.arctan2(x, y)
        bearing = (np.degrees(bearing) + 360) % 360
        bearing.name = "bearing"
        bearing.iat[0] = 0  # NOTE: Is this correct?

        return bearing.astype(np.float32)

    def turn_angle(self, gdf: gpd.GeoDataFrame | gpd.GeoSeries) -> pd.Series:
        geometry = self._get_wgs84_geometry(gdf)

        lat1 = np.radians(geometry.y)
        lon1 = np.radians(geometry.x)

        lat2 = lat1.shift(1)  # type: ignore
        lon2 = lon1.shift(1)  # type: ignore

        lat3 = lat1.shift(-1)  # type: ignore
        lon3 = lon1.shift(-1)  # type: ignore

        angle = np.arctan2(lat3 - lat1, lon3 - lon1) - np.arctan2(
            lat2 - lat1, lon2 - lon1
        )
        angle = (np.degrees(angle) + 360) % 360
        angle.loc[angle > 180] = 360 - angle[angle > 180]
        angle.name = "turn_angle"
        angle.iat[0] = 0  # NOTE: Is this correct?
        angle.iat[-1] = 0  # NOTE: Is this correct?

        return angle.astype(np.float32)
