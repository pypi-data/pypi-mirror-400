import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)


def sum(x: pd.Series):
    return x.sum(min_count=1)


def mode(x: pd.Series):
    # FIXME: This is real problem, because mode is not always the best solution. Should be discussed.
    m = x.mode()
    m = None if m.empty else m[0]

    return m


UNIFORM: dict[str, Any] = {
    # --- Base ---
    "timedelta": sum,
    "wear": "max",
    # --- Counts ---
    "counts_x": sum,
    "counts_y": sum,
    "counts_z": sum,
    # # --- Taxonomy ---
    "activity": mode,
    # # --- Other ---
    "activity_intensity": mode,
    "steps": sum,
    # --- Spatial ---
    "geometry": "first",
    "gnss_accuracy": "mean",
    "satellites_viewed": "mean",
    "satellites_used": "mean",
    "satellites_ratio": "mean",
    "snr_viewed": "mean",
    "snr_used": "mean",
    "altitude": "first",
    "distance": sum,
    "speed": "mean",
    "acceleration": "mean",
    "bearing": pd.NA,
    "turn_angle": pd.NA,
    "indoor": "mean",
}

DOWNSAMPLE: dict[str, Any] = {
    # --- Base ---
    "timedelta": sum,
    "wear": "max",
    # --- Counts ---
    "counts_x": sum,
    "counts_y": sum,
    "counts_z": sum,
    # # --- Taxonomy ---
    "activity": mode,
    # # --- Other ---
    "activity_intensity": mode,
    "steps": sum,
    # --- Spatial ---
    "geometry": "first",
    "gnss_accuracy": "mean",
    "satellites_viewed": "mean",
    "satellites_used": "mean",
    "satellites_ratio": "mean",
    "snr_viewed": "mean",
    "snr_used": "mean",
    "altitude": "first",
    "distance": sum,
    "speed": "mean",
    "acceleration": "mean",
    "bearing": pd.NA,
    "turn_angle": pd.NA,
    "indoor": "mean",
}


@dataclass
class Resampler:
    target: str | timedelta
    mapper: dict[str, Any] | None = None

    def resample(
        self, df: pd.DataFrame | gpd.GeoDataFrame, source: str | timedelta
    ) -> pd.DataFrame | gpd.GeoDataFrame:
        spatial = False
        source = pd.Timedelta(source)
        target = pd.Timedelta(self.target)

        if isinstance(df, gpd.GeoDataFrame):
            spatial = True
            crs = df.crs
            active_geometry = df.active_geometry_name

        if not self.mapper:
            if source < target:
                self.mapper = DOWNSAMPLE
            elif source > target:
                if not self.mapper:
                    raise ValueError(
                        f"Upsampling is not supported ({source} < {target})."
                    )
            else:
                self.mapper = UNIFORM

        dropped = [col for col in df.columns if col not in list(self.mapper.keys())]

        if dropped:
            raise ValueError(
                f"Columns are missing in mapper ({', '.join(dropped)}) and will be dropped."
            )

        mapper = {
            col: method for col, method in self.mapper.items() if col in df.columns
        }

        dtypes = df.dtypes.to_dict()
        df = df.resample(target).agg(mapper)  # type: ignore

        df.dropna(how="all", inplace=True)  # Remove rows where all elements are NaN
        df = df.astype(dtypes)  # Reapply original dtypes

        # After resampling, we need to ensure that primary geometry is set.
        if spatial:
            df.set_geometry(active_geometry, crs=crs, inplace=True)  # type: ignore
            df = df[~df.geometry.isna() & ~df.geometry.is_empty]

        logger.info(f"Resampled DataFrame from {source} to {target}.")

        return df
