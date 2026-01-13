from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import geopandas as gpd
import pandas as pd

from labda.core import Filter
from labda.core.utils import rle
from labda.spatial import SpatialExpander

TRANSPORTATION_MODES = pd.CategoricalDtype(
    [
        "walk",
        "run",
        "bicycle",
        "vehicle",
        "unspecified",
    ]
)


TRANSPORTATION_CUT_POINTS: dict[str, Any] = {
    "heidler_intensity_2025": {
        "name": "Heidler (Intensity, 2025)",
        "reference": None,
        "epoch": "15s",
        "category": "adult",
        "speed": {
            "units": "kph",
            "thresholds": [
                {
                    "name": "walk",
                    "min": 0,
                    "max": 7,
                    "boost": -0.3,
                },
                {
                    "name": "run",
                    "min": 7,
                    "max": 12,
                    "boost": 0,
                },
                {
                    "name": "bicycle",
                    "min": 12,
                    "max": 35,
                    "boost": 0,
                },
                {
                    "name": "vehicle",
                    "min": 35,
                    "max": float("inf"),
                    "boost": 0.3,
                },
            ],
            "alpha": 3,
        },
        "activity_intensity": {
            "thresholds": [
                {
                    "name": "walk",
                    "values": ["light", "moderate"],
                    "boost": -0.2,
                },
                {
                    "name": "run",
                    "values": ["vigorous", "very-vigorous"],
                    "boost": 0,
                },
                {
                    "name": "bicycle",
                    "values": [
                        "light",
                        "moderate",
                    ],
                    "boost": -0.1,
                },
                {
                    "name": "vehicle",
                    "values": ["sedentary"],
                    "boost": 0,
                },
            ],
        },
        "fuzzy": "mean",
    }
}


@dataclass
class Transports:
    id: str = "trip_id"
    status: str = "trip_status"
    window: str | timedelta = "5min"
    smooth: int | None = 3

    def __post_init__(self) -> None:
        self.window = pd.Timedelta(self.window).to_pytimedelta()

    def _classify_categories(
        self, series: pd.Series, thresholds: dict[str, Any]
    ) -> pd.Series:
        n = len(series)
        cut_points = thresholds["thresholds"]
        values = []
        indexes = []

        for cp in cut_points:
            fuzzy = (series.loc[series.isin(cp["values"])].count() / n) + cp["boost"]  # type: ignore
            values.append(fuzzy)
            indexes.append(cp["name"])  # type: ignore

        return pd.Series(values, index=indexes, name=series.name)

    def _classify_speed(
        self, series: gpd.GeoSeries, thresholds: dict[str, Any]
    ) -> pd.Series:
        n = len(series)
        speed = SpatialExpander().speed(series)

        alpha = thresholds.get("alpha", None)

        if alpha:
            speed = Filter().iqr(speed, alpha)

        cut_points = thresholds["thresholds"]
        values = []
        indexes = []

        for cp in cut_points:
            fuzzy = (
                speed.loc[speed.between(cp["min"], cp["max"], inclusive="both")].count()
                / n
            ) + cp["boost"]
            values.append(fuzzy)
            indexes.append(cp["name"])

        return pd.Series(values, index=indexes, name="speed")

    def _get_transport(self, gdf: gpd.GeoDataFrame, thresholds: dict[str, Any]) -> str:
        results = []

        for var in ["activity_intensity", "activity"]:
            cut_points = thresholds.get(var)

            if var in gdf.columns and cut_points:
                categories = self._classify_categories(gdf[var], cut_points)
                results.append(categories)

        speed_cut_points = thresholds["speed"]
        if speed_cut_points:
            speed = self._classify_speed(gdf.geometry, speed_cut_points)
            results.append(speed)

        results = pd.concat(results, axis=1, join="outer")
        results["mean"] = results.mean(axis=1)
        results["max"] = results.max(axis=1)

        result = results[thresholds["fuzzy"]].idxmax()

        return result

    def compute(
        self,
        gdf: gpd.GeoDataFrame,
        cut_points: dict[str, Any],
    ) -> pd.Series:
        indexes = gdf.index

        gdf = gdf[gdf[self.status].isin(["pause", "transport"])].copy()
        gdf["rle"] = rle(gdf[self.id].astype(str) + "_" + gdf[self.status].astype(str))
        # gdf = gdf.loc[gdf[self.status] == "transport"]
        gdf["transport"] = pd.Series(pd.NA, dtype=TRANSPORTATION_MODES, index=gdf.index)

        mapper = dict(enumerate(gdf["transport"].cat.categories))

        for _, temp in gdf.groupby(["rle", pd.Grouper(freq=self.window)]):  # type: ignore
            gdf.loc[gdf.index.isin(temp.index), "transport"] = self._get_transport(
                temp,  # type: ignore
                cut_points,
            )

        if self.smooth:
            for index, temp in gdf.groupby("rle"):
                transport = (
                    temp["transport"]
                    .cat.codes.rolling(window=self.smooth * self.window, center=True)
                    .apply(lambda x: x.mode()[0])
                )
                gdf.loc[gdf["rle"] == index, "transport"] = transport.map(mapper)

        return gdf["transport"].reindex(indexes)  # type: pd.Series # type: ignore
