from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import geopandas as gpd
import pandas as pd

from .parser import FileParser

GNSS_STATUS = {
    -1: pd.NA,
    0: "invalid",
    1: "valid",
    2: "first-fix",
    3: "last-fix",
    4: "last-valid-fix",
    5: "lone-fix",
    6: "inserted-fix",
}


@dataclass
class Palms(FileParser):
    counts: Literal["counts_x", "counts_y", "counts_z", "counts_vm"] = "counts_y"

    def from_csv(self, path: Path | str) -> gpd.GeoDataFrame:
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".csv")
        df = pd.read_csv(
            path,
            engine="pyarrow",
            usecols=["lat", "lon", "identifier", "fixTypeCode", "dateTime", "activity"],
            index_col="dateTime",
        )
        df.index.name = "datetime"

        self.normalize_column_names(df)
        df["fixtypecode"] = df["fixtypecode"].map(GNSS_STATUS).astype("category")
        df = df.loc[
            df["fixtypecode"].notna()
            & ~df["fixtypecode"].isin(["invalid", "inserted-fix"])
        ]
        df.drop(columns=["fixtypecode"], inplace=True)

        df["activity"] = df["activity"].replace({-1: pd.NA, -2: 0})
        df = df.loc[df["activity"].notna()]
        df.rename(columns={"identifier": "id", "activity": self.counts}, inplace=True)

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["lon"], df["lat"]),
            crs="EPSG:4326",
        )
        del df

        gdf.drop(columns=["lat", "lon"], inplace=True)
        gdf = gdf[~gdf.geometry.isna() & ~gdf.geometry.is_empty]

        return gdf
