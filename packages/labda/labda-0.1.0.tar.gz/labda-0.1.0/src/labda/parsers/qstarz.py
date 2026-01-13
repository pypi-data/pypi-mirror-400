from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import geopandas as gpd
import numpy as np
import pandas as pd

from .parser import FileParser


@dataclass
class Qstarz(FileParser):
    satellites_type: Literal["A", "B"] | None = None
    datetime_format: str = "%Y/%m/%d %H:%M:%S"

    def _remove_headers(self, df: pd.DataFrame) -> None:
        header = df.columns
        indexes = df[df.eq(header).all(axis=1)].index
        df.drop(indexes, inplace=True)

    def _remove_invalid_rows(self, df: pd.DataFrame) -> None:
        invalid = ["no fix", "estimated (dead reckoning)", "unknown mode"]

        if "valid" in df.columns:
            df["valid"] = df["valid"].str.lower().str.strip()
            indexes = df[(df["valid"].isin(invalid))].index
            df.drop(indexes, inplace=True)

    def _parse_coordinates(self, df: pd.DataFrame) -> None:
        df[["latitude", "longitude"]] = df[["latitude", "longitude"]].apply(
            pd.to_numeric
        )

        if "n/s" in df.columns and "e/w" in df.columns:
            df["n/s"] = df["n/s"].str.strip().str.upper()
            df["e/w"] = df["e/w"].str.strip().str.upper()

            df[["latitude", "longitude"]] = df[["latitude", "longitude"]].abs()
            df["latitude"] = np.where(df["n/s"] == "S", -df["latitude"], df["latitude"])
            df["longitude"] = np.where(
                df["e/w"] == "W", -df["longitude"], df["longitude"]
            )

            df.drop(columns=["n/s", "e/w"], inplace=True)

    def _parse_datetimes(self, df: pd.DataFrame) -> None:
        if "utc_date" in df.columns and "utc_time" in df.columns:
            utc, date, time = True, "utc_date", "utc_time"
        elif "date" in df.columns and "time" in df.columns:
            utc, date, time = False, "date", "time"
        else:
            raise ValueError("Date and time columns not found in the data.")

        df["datetime"] = df[date] + " " + df[time]
        df["datetime"] = pd.to_datetime(
            df["datetime"], format=self.datetime_format, utc=utc
        )
        df.drop(columns=[date, time], inplace=True)
        df.set_index("datetime", inplace=True)

    def satellites_type_a(self, df: pd.DataFrame) -> None:
        # Format: -20;-22;-30;-33;-26;-27
        df["snr"] = df["snr"].str.replace("-", "").str.split(";")
        df["satellites_viewed"] = df["snr"].apply(len)
        df["snr_viewed"] = df["snr"].apply(lambda x: sum([int(s) for s in x]))

    def satellites_type_b(self, df: pd.DataFrame) -> None:
        # Format: #25-48;#31-41;#29-48;#02-44;12-44,
        df["snr"] = df["snr"].str.split(";")
        df["satellites_viewed"] = df["snr"].apply(len)
        df["snr_viewed"] = df["snr"].apply(
            lambda x: sum([int(s) for s in x.str.split("-").str[1]])
        )

    def _parse_satellites(self, df: pd.DataFrame) -> None:
        columns = ["sat info (sid-snr)"]

        for col in columns:
            df.rename(columns={col: "snr"}, inplace=True)

        if "snr" not in df.columns:
            raise ValueError("Satellites column not found in the data.")

        match self.satellites_type:
            case "A":
                self.satellites_type_a(df)
            case "B":
                self.satellites_type_b(df)

    def _keep_columns(self, df: pd.DataFrame) -> None:
        columns = [
            "latitude",
            "longitude",
            "satellites_viewed",
            "snr_viewed",
        ]
        # Keep only specified columns
        df.drop(columns=[col for col in df.columns if col not in columns], inplace=True)

    def from_csv(self, path: Path | str) -> gpd.GeoDataFrame:
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".csv")
        df = pd.read_csv(path, engine="pyarrow", on_bad_lines="skip")

        # self._remove_headers(df)
        self.normalize_column_names(df)
        self._remove_invalid_rows(df)
        self._parse_coordinates(df)
        self._parse_datetimes(df)

        if self.satellites_type:
            self._parse_satellites(df)

        self._keep_columns(df)

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
            crs="EPSG:4326",
        )
        gdf.drop(columns=["latitude", "longitude"], inplace=True)
        gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty]

        # Move geometry column to the front
        gdf = gdf[["geometry"] + [c for c in gdf.columns if c != "geometry"]]

        return gdf
