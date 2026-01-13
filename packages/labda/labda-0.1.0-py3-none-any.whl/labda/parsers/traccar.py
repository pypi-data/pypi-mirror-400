import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Self
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import geopandas as gpd
import httpx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


UTC = ZoneInfo("UTC")


@dataclass
class TraccarServer:
    url: str
    token: str

    @staticmethod
    def endpoint(url: str, path: str) -> str:
        return urljoin(url, path)

    @classmethod
    def authenticate(
        cls,
        username: str,
        password: str,
        url: str,
        expires: timedelta = timedelta(days=7),
    ) -> Self:
        expiration = (datetime.now() + expires).isoformat() + "Z"

        response = httpx.post(
            cls.endpoint(url, "api/session/token"),
            auth=httpx.BasicAuth(username, password),
            data={"expiration": expiration},
        )

        response.raise_for_status()

        return cls(url=url, token=response.text)

    def _get_subject_id(self, subject: str):
        params = {"uniqueId": subject}

        response = httpx.get(
            self.endpoint(self.url, "api/devices"),
            params=params,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        response_json = response.json()

        if len(response_json) > 1:
            raise ValueError(f"Multiple devices found for {subject}.")

        if not response_json:
            raise ValueError(f"No device found for {subject}.")

        return response_json[0]["id"]

    @staticmethod
    def _parse_records(records: list[dict[str, Any]]) -> gpd.GeoDataFrame:
        df = pd.DataFrame(records)
        attributes = pd.json_normalize(df["attributes"]).add_prefix("attributes_")  # type: ignore
        df = pd.concat([df, attributes], axis=1).drop(columns=["attributes"])
        df.rename(
            columns={
                "fixTime": "datetime",
                "altitude": "elevation",
                "accuracy": "gnss_accuracy",
            },
            inplace=True,
        )
        df = df.loc[
            df["valid"],
            [
                "datetime",
                "latitude",
                "longitude",
                "gnss_accuracy",
                "elevation",  # Unit defaults to: meters
            ],
        ]
        df["elevation"] = df["elevation"].astype(np.float32)

        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude, df.latitude, crs="EPSG:4326"),
        ).drop(columns=["latitude", "longitude"])
        del df
        gdf = gdf[
            ~gdf.geometry.isna()
            & ~gdf.geometry.is_empty
            & (gdf.geometry.x != 0)
            & (gdf.geometry.y != 0)
        ]

        return gdf

    def from_server(
        self,
        subject: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> gpd.GeoDataFrame:
        if start is None:
            start = datetime.fromtimestamp(0)

        if end is None:
            end = datetime.now()

        params = {
            "deviceId": self._get_subject_id(subject),
            "from": start.astimezone(UTC).isoformat(),
            "to": end.astimezone(UTC).isoformat(),
        }

        response = httpx.get(
            self.endpoint(self.url, "api/reports/route"),
            params=params,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        response_json = response.json()

        if not response_json:
            logger.warning(f"No records found for subject {subject}.")
            return gpd.GeoDataFrame(
                columns=[
                    "datetime",
                    "gnss_accuracy",
                    "elevation",
                    "geometry",
                ],
                geometry="geometry",
                crs="EPSG:4326",
            )

        gdf = self._parse_records(response_json)

        return gdf
