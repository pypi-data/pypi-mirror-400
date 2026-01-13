import logging
from dataclasses import dataclass
from datetime import timedelta

import geopandas as gpd
import pandas as pd
from pandas.api.types import CategoricalDtype

from ..core import Expander, Filter, SamplingFrequency
from ..core.utils import rle
from . import SpatialExpander
from .filter import SpatialFilter
from .utils import check_crs_unit, remove_invalid_geometries

logger = logging.getLogger(__name__)

TRIP_CATEGORIES = CategoricalDtype(categories=["stationary", "transport", "pause"])


@dataclass
class Trips:
    stop_radius: float = 50
    stop_duration: str | timedelta = "5min"
    pause_radius: float | None = 25
    pause_duration: str | timedelta | None = "2.5min"
    min_length: float | None = 100  # Originally None
    min_duration: str | timedelta | None = "1min"  # Originally 1min
    indoor_limit: float | None = 0.8
    turn_angle: float | None = None

    def __post_init__(self) -> None:
        self.stop_duration = pd.Timedelta(self.stop_duration).to_pytimedelta()

        if self.pause_duration:
            self.pause_duration = pd.Timedelta(self.pause_duration).to_pytimedelta()

        if self.min_duration:
            self.min_duration = pd.Timedelta(self.min_duration).to_pytimedelta()

        if (
            self.pause_duration
            and self.pause_duration >= self.stop_duration
            and self.pause_radius
            and self.pause_radius >= self.stop_radius
        ):
            raise ValueError(
                "At least one of the pause parameters must be greater than the stop parameters."
            )

        if self.turn_angle:
            logger.warning(
                "Turn angle filtering is experimental. Be cautious when using it."
            )

    def _fix_adjacent_pauses(self, gdf: gpd.GeoDataFrame) -> None:
        gdf["rle"] = rle(gdf["pause"])
        gdf["temp"] = gdf["stationary"].shift(-1) | gdf["stationary"].shift(
            1
        )  # Expands stationary intervals by 1 row in both directions

        # Get pause segments that are adjacent to stationary segments.
        adjacent_pauses = (
            gdf[gdf["pause"]]
            .groupby("rle", group_keys=False)["temp"]
            .apply(
                lambda x: True if x.any() else False,  # type: ignore
                include_groups=False,
            )
        )
        adjacent_pauses = adjacent_pauses.index[adjacent_pauses]
        adjacent_pauses = gdf.index[gdf["rle"].isin(adjacent_pauses)]

        if not adjacent_pauses.empty:
            gdf.loc[adjacent_pauses, "pause"] = False
            gdf.loc[adjacent_pauses, "transport"] = False
            gdf.loc[adjacent_pauses, "stationary"] = True

        gdf.drop(columns=["rle", "temp"], inplace=True)

    def _remove_short_length_trips(self, gdf: gpd.GeoDataFrame) -> None:
        if not self.min_length:
            return

        expander = SpatialExpander()

        gdf["temp"] = gdf["transport"] | gdf["pause"]
        gdf["rle"] = rle(gdf["temp"])

        # TODO: All of this can be done with pd.transform instead of apply. Even for other similar methods.
        short_length_trips = (
            gdf[gdf["temp"]]
            .groupby("rle", group_keys=False)["geometry"]
            .apply(
                lambda x: True
                if expander.distance(x).sum() < self.min_length
                else False,  # type: ignore
                include_groups=False,
            )
        )
        short_length_trips = short_length_trips.index[short_length_trips]
        short_length_trips = gdf.index[gdf["rle"].isin(short_length_trips)]

        if not short_length_trips.empty:
            gdf.loc[short_length_trips, "transport"] = False
            gdf.loc[short_length_trips, "pause"] = False
            gdf.loc[short_length_trips, "stationary"] = True

        gdf.drop(columns=["rle", "temp"], inplace=True)

    def _remove_short_duration_trips(self, gdf: gpd.GeoDataFrame) -> None:
        if not self.min_duration:
            return

        gdf["temp"] = gdf["transport"] | gdf["pause"]
        gdf["rle"] = rle(gdf["temp"])

        short_duration_trips = (
            gdf[gdf["temp"]]
            .groupby("rle", group_keys=False)["geometry"]
            .apply(
                lambda x: True
                if x.index.max() - x.index.min() < self.min_duration
                else False,  # type: ignore
                include_groups=False,
            )
        )
        short_duration_trips = short_duration_trips.index[short_duration_trips]
        short_duration_trips = gdf.index[gdf["rle"].isin(short_duration_trips)]

        if not short_duration_trips.empty:
            gdf.loc[short_duration_trips, "transport"] = False
            gdf.loc[short_duration_trips, "pause"] = False
            gdf.loc[short_duration_trips, "stationary"] = True

        gdf.drop(columns=["rle", "temp"], inplace=True)

    def _remove_indoor_trips(self, gdf: gpd.GeoDataFrame) -> None:
        if not self.indoor_limit:
            return

        if "indoor" not in gdf.columns:
            print(
                "Indoor limit is provided but the 'indoor' column is missing. Skipping."
            )  # FIXME: Logging, better text.
            return

        gdf["temp"] = gdf["transport"] | gdf["pause"]
        gdf["rle"] = rle(gdf["temp"])

        indoor_trips = (
            gdf[gdf["temp"]]
            .groupby("rle", group_keys=False)["indoor"]
            .apply(
                lambda x: True if x.mean() > self.indoor_limit else False,  # type: ignore
                include_groups=False,
            )
        )
        indoor_trips = indoor_trips.index[indoor_trips]
        indoor_trips = gdf.index[gdf["rle"].isin(indoor_trips)]

        if not indoor_trips.empty:
            gdf.loc[indoor_trips, "transport"] = False
            gdf.loc[indoor_trips, "pause"] = False
            gdf.loc[indoor_trips, "stationary"] = True

        gdf.drop(columns=["rle", "temp"], inplace=True)

    def _remove_turn_angle_trips(self, gdf: gpd.GeoDataFrame) -> None:
        if not self.turn_angle:
            return

        gdf["temp"] = gdf["transport"] | gdf["pause"]
        gdf["rle"] = rle(gdf["temp"])

        turn_angle_trips = (
            gdf[gdf["temp"]]
            .groupby("rle", group_keys=False)["geometry"]
            .apply(
                lambda x: True
                if SpatialExpander().turn_angle(x).mean() < self.turn_angle  # type: ignore
                else False,
                include_groups=False,
            )
        )
        turn_angle_trips = turn_angle_trips.index[turn_angle_trips]
        turn_angle_trips = gdf.index[gdf["rle"].isin(turn_angle_trips)]

        if not turn_angle_trips.empty:
            gdf.loc[turn_angle_trips, "transport"] = False
            gdf.loc[turn_angle_trips, "pause"] = False
            gdf.loc[turn_angle_trips, "stationary"] = True

    def _compute(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        spatial_filter = SpatialFilter()

        gdf["transport"] = True
        gdf["stationary"] = spatial_filter.stop_detector(
            gdf,
            self.stop_radius,
            self.stop_duration,
        )
        gdf.loc[gdf["stationary"], "transport"] = False

        if self.pause_radius and self.pause_duration:
            gdf["pause"] = spatial_filter.stop_detector(
                gdf[~gdf["stationary"]],
                self.pause_radius,
                self.pause_duration,
            )
            gdf["pause"] = gdf["pause"].astype("boolean").fillna(False).astype(bool)
            gdf.loc[gdf["pause"], "transport"] = False

            self._fix_adjacent_pauses(gdf)

        self._remove_short_length_trips(gdf)
        self._remove_short_duration_trips(gdf)
        self._remove_indoor_trips(gdf)
        self._remove_turn_angle_trips(gdf)  # TODO: Needs to be tested!

        gdf["status"] = pd.Series(pd.NA, index=gdf.index, dtype=TRIP_CATEGORIES)

        gdf.loc[gdf["stationary"], "status"] = "stationary"

        # The pause points are also considered as transport points at this stage to get the RLE for whole transport segments (including pause points).
        gdf.loc[gdf["transport"] | gdf["pause"], "status"] = "transport"

        gdf["id"] = rle(gdf["status"])
        gdf.loc[gdf["pause"], "status"] = "pause"  # Fix the status of the pause points.

        return gdf[["id", "status"]]

    def compute(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        # TODO: Would be nice to remove short trips (pauses excluded) but then we need change pause to stationary again - assess after.

        check_crs_unit(gdf, "metre")

        columns = ["geometry"]

        if "indoor" in gdf.columns:
            columns += ["indoor"]

        gdf = gdf[columns].copy()

        # Keep only valid geometries
        gdf = remove_invalid_geometries(gdf)

        sf = SamplingFrequency().compute_epoch(gdf)

        if self.stop_duration <= sf:  # type: ignore
            raise ValueError(
                f"Stop duration must be greater than sampling frequency ({sf})."
            )

        if self.min_duration and self.min_duration <= sf:  # type: ignore
            raise ValueError(
                f"Min duration must be greater than sampling frequency ({sf})."
            )

        segments = Filter().gap_splitter(
            timedelta=Expander().timedelta(gdf),
            duration=self.stop_duration,  # type: ignore
        )

        trips = []

        for _, segment in gdf.groupby(segments):
            temp = self._compute(segment)  # type: ignore
            trips.append(temp)

        del gdf

        trips = pd.concat(trips)
        trips["id"] = segments.astype(str) + "_" + trips["id"].astype(str)
        trips["id"] = rle(trips["id"])

        return trips  # type: ignore
