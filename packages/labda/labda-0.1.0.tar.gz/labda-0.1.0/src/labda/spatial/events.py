from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal, Self

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiPoint

from ..core.utils import rle
from .expander import SpatialExpander

STATIONARY_BUFFER = 30
PAUSE_BUFFER = 15


@dataclass
class Base:
    id: str
    start: datetime
    end: datetime
    duration: timedelta
    status: Literal["stationary", "pause", "transport"]
    geometry: gpd.GeoSeries

    @staticmethod
    def get_base(gdf: gpd.GeoDataFrame, epoch: timedelta) -> dict[str, Any]:
        id = str(gdf["id"].iloc[0].item())
        status = gdf["status"].iloc[0]
        indexes = gdf.index
        start, end = indexes[0].to_pydatetime(), indexes[-1].to_pydatetime()
        duration = end - start + epoch
        geometry = MultiPoint(gdf.geometry)

        return {
            "id": id,
            "start": start,
            "end": end,
            "duration": duration,
            "status": status,
            "geometry": geometry,
        }

    @classmethod
    def from_dataframe(cls, gdf: gpd.GeoDataFrame, epoch: timedelta) -> Self:
        base = cls.get_base(gdf, epoch)

        return cls(**base)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


@dataclass
class Transport(Base):
    mode: Literal["walk", "run", "bicycle", "vehicle", "multi-mode"]
    distance: float

    @classmethod
    def from_dataframe(cls, gdf: gpd.GeoDataFrame, epoch: timedelta) -> Self:
        base = cls.get_base(gdf, epoch)
        mode = gdf["transport"].iloc[0]
        distance = SpatialExpander().distance(gdf).sum().item()

        return cls(**base, mode=mode, distance=distance)

    def transform_geometry(self) -> None:
        """Convert MultiPoint geometry to LineString for transport events."""

        if len(self.geometry.geoms) >= 2:
            self.geometry = LineString(self.geometry.geoms)  # type: ignore


@dataclass
class Stationary(Base):
    location: str | None = None

    @staticmethod
    def _get_location(gdf: gpd.GeoDataFrame) -> str | None:
        location = None

        if "location" in gdf.columns:
            location = gdf["location"].value_counts().idxmax()

        return location  # type: ignore

    @classmethod
    def from_dataframe(cls, gdf: gpd.GeoDataFrame, epoch: timedelta) -> Self:
        base = cls.get_base(gdf, epoch)
        location = cls._get_location(gdf)

        return cls(**base, location=location)

    def transform_geometry(self) -> None:
        """Convert MultiPoint geometry to Polygon for stationary events."""

        self.geometry = self.geometry.centroid.buffer(STATIONARY_BUFFER)


@dataclass
class Pause(Base):
    pass

    def transform_geometry(self) -> None:
        """Convert MultiPoint geometry to Polygon for pause events."""

        self.geometry = self.geometry.centroid.buffer(PAUSE_BUFFER)


@dataclass
class MultiTransport(Transport):
    partials: list[Transport | Pause]

    @staticmethod
    def _get_partial_events(
        df: pd.DataFrame, epoch: timedelta
    ) -> list[Transport | Pause]:
        partials = []

        for id, event in df.groupby("partial"):
            func = (
                Transport.from_dataframe
                if event["status"].iloc[0] == "transport"
                else Pause.from_dataframe
            )
            event_obj = func(event, epoch)  # type: ignore
            event_obj.id = f"{event_obj.id}_{id}"  # type: ignore
            partials.append(event_obj)

        return partials

    @classmethod
    def from_dataframe(cls, gdf: gpd.GeoDataFrame, epoch: timedelta) -> Self:
        base = cls.get_base(gdf, epoch)
        partials = cls._get_partial_events(gdf, epoch)
        distance = sum([p.distance for p in partials if isinstance(p, Transport)])
        mode = "multi-mode"

        return cls(**base, partials=partials, mode=mode, distance=distance)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if k != "partials"}

    def transform_geometry(self) -> None:
        self.geometry = LineString(self.geometry.geoms)  # type: ignore

        for partial in self.partials:
            partial.transform_geometry()


@dataclass
class SpatialEvents:
    events: list[Stationary | Transport | Pause | MultiTransport]
    crs: str | None = None
    # TODO: Transports should overflow to neighbour events, so we account for the time and distance.

    @classmethod
    def from_dataframe(
        cls,
        gdf: gpd.GeoDataFrame,
        epoch: timedelta,
        id: str = "id",
        status: str = "status",
        transport: str = "transport",
    ) -> Self:
        events = []

        gdf = gdf.rename(columns={id: "id", status: "status", transport: "transport"})
        gdf["partial"] = rle(gdf["status"])

        for _, event in gdf.groupby("id"):
            if event["partial"].nunique() > 1:
                event["partial"] = rle(event["partial"])
                events.append(MultiTransport.from_dataframe(event, epoch))  # type: ignore
            else:
                if event["status"].iloc[0] == "transport":
                    events.append(Transport.from_dataframe(event, epoch))  # type: ignore
                else:
                    events.append(Stationary.from_dataframe(event, epoch))  # type: ignore

        return cls(events=events, crs=gdf.crs)

    def to_dataframe(self) -> gpd.GeoDataFrame:
        dicts = []

        for event in self.events:
            dicts.append(event.to_dict())

            if isinstance(event, MultiTransport):
                dicts.extend([partial.to_dict() for partial in event.partials])

        gdf = gpd.GeoDataFrame(dicts, geometry="geometry", crs=self.crs)
        ids = gdf["id"].str.split("_")
        gdf["partial"] = ids.str[1]
        gdf["id"] = ids.str[0]

        columns = [
            "id",
            "partial",
            "start",
            "end",
            "duration",
            "status",
            "mode",
            "distance",
            "location",
            "geometry",
        ]
        gdf = gdf.reindex(columns=columns, fill_value=pd.NA)

        return gdf[columns]

    def transform_geometries(self) -> None:
        for event in self.events:
            event.transform_geometry()
