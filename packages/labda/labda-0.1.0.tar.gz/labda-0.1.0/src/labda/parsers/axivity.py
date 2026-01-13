from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from skdh.io import ReadCwa

from .parser import FileParser


@dataclass
class Axivity(FileParser):
    """Parses Axivity .cwa files into a standardized DataFrame format.

    This parser handles the binary reading of Axivity files (`.cwa`), extracting
    tri-axial acceleration and temperature data. It ensures the resulting data
    is properly indexed with datetimes and validated against corruption.

    Attributes:
        timezone (ZoneInfo | str | None): The timezone to which the resulting datetime
            index will be localized. If `None` (default), the index remains
            timezone-naive.
    """

    timezone: ZoneInfo | str | None = None

    def __post_init__(self):
        if self.timezone is not None and not isinstance(self.timezone, ZoneInfo):
            self.timezone = ZoneInfo(self.timezone)

    def from_cwa(
        self,
        path: Path | str,
    ) -> pd.DataFrame:
        """Parses a .cwa file and returns a standardized accelerometer DataFrame.

        This method wraps the `skdh` reader logic, adding specific validation
        checks for data corruption (negative timestamps) and normalizing column
        names to the package standard.

        Args:
            path (Path | str): The file system path to the .cwa file.

        Returns:
            pd.DataFrame: Standardized accelerometer data.

        Raises:
            FileNotFoundError: If `path` does not exist.
            ValueError: If the file is not a valid `.cwa`, is empty, or contains
                corrupted data (e.g., negative timestamps).
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".cwa")

        cwa = ReadCwa().predict(file=path, tz_name=self.timezone)

        has_negative = np.any(cwa["time"] < 0)
        if has_negative:
            raise ValueError("File is corrupted.")

        df = pd.DataFrame(
            cwa["accel"].astype(np.float32),
            columns=["acc_x", "acc_y", "acc_z"],
            index=cwa["time"],
        )

        self.check_empty(df)

        temperature = cwa.get("temperature")
        if temperature is not None:
            df["temperature"] = temperature.astype(np.float32)

        del cwa

        df.index.name = "datetime"
        if self.timezone:
            df.index = pd.to_datetime(df.index, utc=True, unit="s")
            df.index = df.index.tz_convert(self.timezone)  # type: ignore
        else:
            df.index = pd.to_datetime(df.index, unit="s")

        return df
