import logging
from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from typing import Any, Callable

import geopandas as gpd

from ..core.resampler import Resampler
from ..spatial import SpatialExpander

SPATIAL_CLEANING = {
    "max_pdop": 7,
    "max_hdop": 5,
    "max_gnss_accuracy": 50,
    "min_satellites_used": 4,
    "max_speed": {"speed": 200, "iter": 3},
}

logger = logging.getLogger(__name__)


@dataclass
class SpatialPreprocessor:
    pass

    def log(
        self, func: Callable, gdf: gpd.GeoDataFrame, column: str | None, message: str
    ) -> tuple[gpd.GeoDataFrame, dict[str, Any] | None]:
        if column is not None and column not in gdf.columns:
            logger.info(f"{message} Column '{column}' not found. Skipping.")
            return gdf, None

        n = len(gdf)
        gdf = func(gdf=gdf)
        n_removed = n - len(gdf)

        if n_removed > 0:
            logger.info(
                f"{message} Removed {n_removed} ({n_removed / n * 100:.2f}%) points."
            )
        else:
            logger.info(f"{message} No points removed.")

        return gdf, {"in": n, "out": len(gdf)}

    def remove_duplicates(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf[~gdf.index.duplicated(keep="first")]

    def remove_invalid_geometries(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty]

    def check_crs_unit(self, gdf: gpd.GeoDataFrame | gpd.GeoSeries, unit: str) -> None:
        if gdf.crs is not None:
            if gdf.crs.axis_info[0].unit_name != unit:
                message = f"The CRS of the GeoDataFrame must have a unit of '{unit}'."
                logger.error(message)

                raise ValueError(message)
        else:
            message = "The GeoDataFrame must have a CRS defined."
            logger.error(message)
            raise ValueError(message)

        logger.info(f"CRS unit is correctly set to '{unit}'.")

    def remove_satellites_used(
        self, gdf: gpd.GeoDataFrame, min_satellites: int = 4
    ) -> gpd.GeoDataFrame:
        # NOTE: https://www.euspa.europa.eu/sites/default/files/understanding_gnss_performance_on_android_using_the_gps_testc_app.pdf
        return gdf[gdf["satellites_used"] >= min_satellites]

    def remove_pdop(self, gdf: gpd.GeoDataFrame, max_pdop: int = 7) -> gpd.GeoDataFrame:
        # NOTE: Check for reference
        return gdf[gdf["pdop"] <= max_pdop]

    def remove_hdop(self, gdf: gpd.GeoDataFrame, max_hdop: int = 5) -> gpd.GeoDataFrame:
        # NOTE: Check for reference
        return gdf[gdf["hdop"] <= max_hdop]

    def remove_gnss_accuracy(
        self, gdf: gpd.GeoDataFrame, max_metre: float = 50
    ) -> gpd.GeoDataFrame:
        # NOTE: Reference does not exist but it is based on our thresholds for trip detection
        return gdf[gdf["gnss_accuracy"] <= max_metre]

    def remove_speed_outliers(
        self,
        gdf: gpd.GeoDataFrame,
        max_speed: float = 200,
        iter: int = 3,
    ) -> gpd.GeoDataFrame:
        # NOTE: Reference from PALMS and others, it is kind of standard way
        expander = SpatialExpander()

        for _ in range(iter):
            speed = expander.speed(gdf)
            gdf = gdf[speed <= max_speed]

        return gdf

    def uniform(self, gdf: gpd.GeoDataFrame, epoch: timedelta) -> gpd.GeoDataFrame:
        return Resampler(epoch).resample(gdf, epoch)  # type: gpd.GeoDataFrame # type: ignore

    def compute(
        self,
        gdf: gpd.GeoDataFrame,
        epoch: timedelta,
        config: dict[str, Any] = SPATIAL_CLEANING,
    ) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
        report = {}
        cleaned = gdf.copy()

        cleaned.sort_values("datetime", inplace=True)

        self.check_crs_unit(cleaned, "metre")

        cleaned, report["duplicate_datetimes"] = self.log(
            self.remove_duplicates,
            cleaned,
            column=None,
            message="Duplicate datetime removal.",
        )

        cleaned, report["invalid_geometries"] = self.log(
            self.remove_invalid_geometries,
            cleaned,
            column="geometry",
            message="Invalid geometries removal.",
        )

        satellites_used = config.get("min_satellites_used")
        if satellites_used is not None:
            cleaned, report["satellites_used"] = self.log(
                partial(self.remove_satellites_used, min_satellites=satellites_used),
                cleaned,
                column="satellites_used",
                message="Satellites used removal.",
            )

        pdop = config.get("max_pdop")
        if pdop is not None:
            cleaned, report["pdop"] = self.log(
                partial(self.remove_pdop, max_pdop=pdop),
                cleaned,
                column="pdop",
                message="PDOP removal.",
            )

        max_hdop = config.get("max_hdop")
        if max_hdop is not None:
            cleaned, report["hdop"] = self.log(
                partial(self.remove_hdop, max_hdop=max_hdop),
                cleaned,
                column="hdop",
                message="HDOP removal.",
            )

        max_gnss_accuracy = config.get("max_gnss_accuracy")
        if max_gnss_accuracy is not None:
            cleaned, report["gnss_accuracy"] = self.log(
                partial(self.remove_gnss_accuracy, max_metre=max_gnss_accuracy),
                cleaned,
                column="gnss_accuracy",
                message="GNSS accuracy removal.",
            )

        max_speed = config.get("max_speed")
        if max_speed is not None:
            speed = max_speed["speed"]
            iter = max_speed["iter"]

            cleaned, report["speed"] = self.log(
                partial(self.remove_speed_outliers, max_speed=speed, iter=iter),
                cleaned,
                column=None,
                message="Speed outliers removal.",
            )

        cleaned, report["uniform"] = self.log(
            partial(self.uniform, epoch=epoch), cleaned, column=None, message="Uniform."
        )

        return cleaned, report
