from dataclasses import dataclass
from datetime import datetime, time, timedelta

import geopandas as gpd
import pandas as pd
from shapely import Polygon

from ..core import Bouts
from ..core.utils import parse_datetime_or_time

# NOTE: SpatialContexts could be created to seperate logic into the correct modules.


@dataclass
class Contexts:
    epoch: str | timedelta
    min_duration: str | timedelta | None = None
    interruption_max_duration: str | timedelta | None = None

    def __post_init__(self) -> None:
        self.epoch = pd.Timedelta(self.epoch).to_pytimedelta()

        if self.min_duration is not None:
            self.min_duration = pd.Timedelta(self.min_duration).to_pytimedelta()

        if self.interruption_max_duration is not None:
            self.interruption_max_duration = pd.Timedelta(
                self.interruption_max_duration
            ).to_pytimedelta()

    def _filter_by_temporal_intervals(
        self,
        df: pd.DataFrame | gpd.GeoDataFrame,
        start: str | time | datetime,
        end: str | time | datetime,
    ) -> pd.DataFrame:
        start = parse_datetime_or_time(start)
        end = parse_datetime_or_time(end)

        if isinstance(start, time) and isinstance(end, time):
            temporal = df.between_time(start, end, inclusive="left")

        elif isinstance(start, time) or isinstance(end, time):
            raise ValueError("If one of the start or end is a time, both must be.")

        elif isinstance(start, datetime) and isinstance(end, datetime):
            temporal = df.loc[(df.index >= start) & (df.index < end)]

        return temporal

    def temporal(
        self,
        df: pd.DataFrame | gpd.GeoDataFrame,
        start: str | time | datetime,
        end: str | time | datetime,
    ) -> pd.Series:
        temporal = self._filter_by_temporal_intervals(
            df,
            start=start,
            end=end,
        )

        context = pd.Series(False, index=df.index)
        context[temporal.index] = True

        return context

    def spatial(
        self,
        gdf: gpd.GeoDataFrame,
        geometry: Polygon,
    ) -> pd.Series:
        context = gdf.within(geometry)

        return context

    def combined(
        self,
        gdf: gpd.GeoDataFrame,
        start: str | time | datetime | None,
        end: str | time | datetime | None,
        geometry: Polygon | None,
    ) -> pd.Series:
        context = pd.DataFrame(index=gdf.index)

        if start is not None and end is not None:
            context["temporal"] = self.temporal(
                gdf,
                start=start,
                end=end,
            )

        if geometry:
            context["spatial"] = self.spatial(gdf, geometry)

        if "spatial" in context and "temporal" in context.columns:
            context["context"] = context["spatial"] & context["temporal"]
        elif "spatial" in context.columns:
            context["context"] = context["spatial"]
        elif "temporal" in context.columns:
            context["context"] = context["temporal"]

        if self.min_duration is not None:
            bouts = Bouts(
                epoch=self.epoch,
                min_value=1,
                max_value=1,
                min_duration=self.min_duration,
                interruption_min_value=0,
                interruption_max_value=0,
                interruption_max_duration=self.interruption_max_duration,
            )
            context["context"] = context["context"].astype(int)
            context["context"] = bouts.compute(context["context"])

        return context["context"]

    def compute(
        self, gdf: gpd.GeoDataFrame, contexts: gpd.GeoDataFrame
    ) -> pd.DataFrame:
        if gdf.crs != contexts.crs:
            raise ValueError("CRS of gdf and contexts must match.")

        results = pd.DataFrame(index=gdf.index)

        priority = True if "priority" in contexts.columns else False

        if priority:
            contexts = contexts.sort_values("priority", ascending=False)
            results["context"] = "other"

        for context in contexts.to_dict(orient="records"):
            label = f"context_{context['label']}"
            geometry = context["geometry"]
            start, end = context.get("start"), context.get("end")

            results[label] = self.combined(gdf, start=start, end=end, geometry=geometry)

            if priority:
                results.loc[results[label], "context"] = context["label"]

        return results
