import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Self
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
from rich.progress import Progress

from .file import Sens

UTC = ZoneInfo("UTC")


@dataclass
class SensServer:
    token: str
    url: str = "https://app.sens.dk"
    version: float = 1.0
    scopes: list[dict[str, Any]] = field(init=False)
    projects: list[dict[str, Any]] = field(init=False)
    sensors: list[dict[str, Any]] = field(init=False)

    def __post_init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.scopes = self.get_scopes()
        self.projects = self.get_projects(self.scopes)
        self.sensors = self.get_sensors(self.projects)

    @staticmethod
    def endpoint(url: str, version: float, path: str) -> str:
        return urljoin(url, f"/api/{version}/{path}")

    @classmethod
    def authenticate(
        cls,
        username: str,
        password: str,
        url: str = "https://app.sens.dk",
        version: float = 1.0,
    ) -> Self:
        response = httpx.post(
            cls.endpoint(url, version, "auth/login"),
            json={
                "user_email": username,
                "password": password,
            },
        )

        response.raise_for_status()

        return cls(url=url, token=response.json()["value"]["auth_token"])

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        response = httpx.get(
            self.endpoint(self.url, self.version, path),
            params=params,
            headers={"Auth-Token": self.token},
        )

        response.raise_for_status()

        return response

    def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        response = httpx.post(
            self.endpoint(self.url, self.version, path),
            json=params,
            headers={
                "Auth-Token": self.token,
            },
        )

        response.raise_for_status()

        return response

    def get_scopes(self) -> list[dict[str, Any]]:
        response = self.get("access_scopes/list")
        response_json = response.json()

        return response_json.get("value").get("scopes")

    def get_projects(self, scopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        projects = []

        for scope in scopes:
            response = self.get("projects", params={"scope_id": scope["id"]})

            response_json = response.json()
            response_json = response_json.get("value")
            response_json = response_json[0].get("projects") if response_json else []
            projects.extend(response_json)

        return projects

    def get_sensors(self, projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sensors = []

        for project in projects:
            response = self.get(
                "sensors",
                params={"scope_id": project["parent_id"], "project_id": project["id"]},
            )

            response_json = response.json()
            response_json = response_json.get("value")
            response_json = response_json.get("sensors") if response_json else []

            for sensor in response_json:
                sensor["project_id"] = project["id"]

            sensors.extend(response_json)

        return sensors

    def _poll_and_download(
        self,
        params: dict[str, Any],
        sensor: str,
        poll_interval: int = 2,
    ) -> bytes | bytearray:
        with Progress() as progress:
            finished = False
            queuing_task = progress.add_task(f"Queuing for '{sensor}'...", total=100)

            while not finished:
                response = self.post("export/sensor/raw", params).json()
                status = response["value"]["queue_entry"]["status"]

                if status == "export_status/completed":
                    finished = True

                time.sleep(poll_interval)
                progress.update(queuing_task, advance=1)

            progress.update(queuing_task, completed=100)

            url = response["value"]["queue_entry"]["url"]
            buffer = bytearray()

            with httpx.stream("GET", url, follow_redirects=True) as file:
                file.raise_for_status()
                total_size = int(file.headers.get("content-length", 0))

                if total_size > 0:
                    download_task = progress.add_task(
                        f"Downloading for '{sensor}'...", total=total_size
                    )

                    for data in file.iter_bytes(chunk_size=1024):
                        buffer.extend(data)
                        progress.update(download_task, advance=len(data))

                    progress.update(download_task, completed=total_size)
                else:
                    raise ValueError("File has zero length.")

            time.sleep(0.1)

        return buffer

    def from_server(
        self,
        sensor: str,
        start: datetime,
        end: datetime,
    ) -> pd.DataFrame:
        stream_name = "acc/3ax/4g"
        file_format = "bin"

        start_datetime = start.astimezone(UTC)
        end_datetime = end.astimezone(UTC)

        if end_datetime - start_datetime > timedelta(days=90):
            raise ValueError("Time range cannot exceed 90 days.")

        sensor_obj = next((s for s in self.sensors if s["short_name"] == sensor), None)

        if not sensor_obj:
            raise ValueError(f"Sensor '{sensor}' not found.")

        params = {
            "scope_id": sensor_obj["scope_id"],
            "project_id": sensor_obj["project_id"],
            "sensor_id": sensor_obj["id"],
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "stream_name": stream_name,
            "file_format": file_format,
        }

        buffer = self._poll_and_download(params, sensor)

        df = Sens().from_buffer(buffer)

        return df
