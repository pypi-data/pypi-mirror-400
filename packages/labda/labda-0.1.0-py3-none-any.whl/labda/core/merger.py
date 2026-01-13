from dataclasses import dataclass

import geopandas as gpd
import pandas as pd

from .sampling_frequency import SamplingFrequency


@dataclass
class Merger:
    pass

    def _check_sampling_frequency(
        self,
        left: pd.DataFrame | gpd.GeoDataFrame,
        right: pd.DataFrame | gpd.GeoDataFrame,
    ) -> None:
        sampling_frequency = SamplingFrequency(round_to_nearest=0)

        left_sf = sampling_frequency.compute_epoch(left)
        right_sf = sampling_frequency.compute_epoch(right)

        if left_sf != right_sf:
            raise ValueError(
                f"Sampling frequencies do not match (left: {left_sf}, right: {right_sf})."
            )

    def _check_timezone(
        self,
        left: pd.DataFrame | gpd.GeoDataFrame,
        right: pd.DataFrame | gpd.GeoDataFrame,
    ) -> None:
        left_tz = left.index.tz
        right_tz = right.index.tz

        if left_tz != right_tz:
            raise ValueError(
                f"Timezones do not match (left: {left_tz}, right: {right_tz})."
            )

    def _check_duplicate_columns(
        self,
        left: pd.DataFrame | gpd.GeoDataFrame,
        right: pd.DataFrame | gpd.GeoDataFrame,
    ) -> None:
        duplicate_cols = left.columns.intersection(right.columns)
        if not duplicate_cols.empty:
            raise ValueError(f"Duplicate columns found: {duplicate_cols.tolist()}")

    def _check_crs(
        self,
        left: pd.DataFrame | gpd.GeoDataFrame,
        right: pd.DataFrame | gpd.GeoDataFrame,
    ) -> None:
        if isinstance(left, pd.DataFrame) or isinstance(right, pd.DataFrame):
            return

        if left.crs != right.crs:
            raise ValueError(
                f"CRS do not match (left: {left.crs}, right: {right.crs})."
            )

    def merge(
        self,
        left: pd.DataFrame | gpd.GeoDataFrame,
        right: pd.DataFrame | gpd.GeoDataFrame,
        validate: bool = True,
    ) -> pd.DataFrame | gpd.GeoDataFrame:
        if validate:
            self._check_sampling_frequency(left, right)
            self._check_timezone(left, right)
            self._check_duplicate_columns(left, right)
            self._check_crs(left, right)

        merged = pd.merge(
            left,
            right,
            left_index=True,
            right_index=True,
            how="inner",
            suffixes=(None, None),
            validate="one_to_one",
        )

        if isinstance(left, gpd.GeoDataFrame) or isinstance(right, gpd.GeoDataFrame):
            crs = left.crs if isinstance(left, gpd.GeoDataFrame) else right.crs
            merged = gpd.GeoDataFrame(merged, crs=crs, geometry="geometry")

        return merged
