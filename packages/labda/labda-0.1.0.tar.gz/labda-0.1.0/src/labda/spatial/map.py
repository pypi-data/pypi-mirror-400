from dataclasses import dataclass

import colorcet as cc
import geopandas as gpd
import pandas as pd
import pydeck as pdk
from PIL import ImageColor

from .events import SpatialEvents


@dataclass
class Map:
    pass

    @staticmethod
    def colorize(series: pd.Series, pallete: str = "glasbey") -> pd.Series:
        pallete = [ImageColor.getrgb(color) for color in cc.palette[pallete]]  # type: ignore
        values = series.unique().tolist()
        colors = dict(zip(values, pallete))
        series = series.map(colors)

        return series

    def _get_contexts_layer(self, gdf: gpd.GeoDataFrame) -> pdk.Layer:
        """Creates a layer for contexts."""

        gdf = gdf.to_crs("EPSG:4326")  # Convert to WGS84 if not already in that CRS

        if "color" not in gdf.columns:
            gdf["color"] = gdf.geometry.apply(lambda x: [255, 255, 255])

        if "tooltip" not in gdf.columns:
            gdf["tooltip"] = gdf.apply(
                lambda x: f"Context: {x['label']}",
                axis=1,
            )

        return pdk.Layer(
            "GeoJsonLayer",
            data=gdf,
            stroked=True,
            filled=False,
            get_line_color=[255, 255, 255],
            get_line_width=2.5,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255, 255, 0],
        )

    def _compute_raw(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> pdk.Layer:
        if "datetime" not in gdf.columns:
            gdf["datetime"] = gdf.index.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore

        if "color" not in gdf.columns:
            gdf["color"] = gdf.geometry.apply(lambda x: [255, 0, 0])

        if "tooltip" not in gdf.columns:
            gdf["tooltip"] = gdf.apply(
                lambda x: f"Datetime: {x['datetime']}<br>Coordinates: {x['geometry'].centroid.y}, {x['geometry'].centroid.x}",
                axis=1,
            )

        layer = pdk.Layer(
            "GeoJsonLayer",
            data=gdf,
            stroked=False,
            filled=True,
            get_position="geometry.coordinates",
            get_fill_color="color",  # ImageColor.getcolor("red", "RGB")
            get_radius=10,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255, 255, 0],
        )

        return layer

    def _compute_events(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> pdk.Layer:
        gdf = gdf.loc[gdf["mode"] != "multi-mode"].copy()

        gdf["context"] = gdf["mode"]
        stationary = gdf[gdf["status"] == "stationary"]
        gdf.loc[stationary.index, "context"] = stationary["location"].fillna("other")

        pauses = gdf[gdf["status"] == "pause"]
        gdf.loc[pauses.index, "context"] = "pause"
        gdf["color"] = Map.colorize(gdf["context"].astype(str))

        gdf["tooltip"] = gdf.apply(
            lambda x: f"""Start: {x["start"]}<br>End: {x["end"]}<br>
            Duration: {x["duration"].total_seconds() / 60:.2f} minutes⁠<br>
            Context: {x["status"]} ({x["context"]})⁠<br>""",
            axis=1,
        )

        layer = pdk.Layer(
            "GeoJsonLayer",
            data=gdf,
            stroked=False,
            filled=True,
            get_fill_color="color",
            get_line_color="color",
            get_line_width=5,
            get_radius=5,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255, 255, 0],
        )

        return layer

    def compute(
        self,
        gdf: SpatialEvents | gpd.GeoDataFrame,
        contexts: gpd.GeoDataFrame | None = None,
    ) -> pdk.Deck:
        compute_function = self._compute_raw
        layers = []

        if isinstance(gdf, SpatialEvents):
            gdf = gdf.to_dataframe()
            compute_function = self._compute_events

        gdf = gdf.to_crs("EPSG:4326")  # Convert to WGS84 if not already in that CRS
        layer = compute_function(gdf)
        layers.append(layer)

        # Set the initial view state based on centroid of all points
        centroid = gdf.geometry.union_all().centroid
        view_state = pdk.ViewState(latitude=centroid.y, longitude=centroid.x, zoom=10)

        if contexts is not None:
            contexts_layer = self._get_contexts_layer(contexts)
            layers.append(contexts_layer)

        # Create the deck.gl map visualization
        r = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={
                "html": "{tooltip}",
            },  # type: ignore
            # map_style=pdk.map_styles.CARTO_LIGHT,
        )

        return r
