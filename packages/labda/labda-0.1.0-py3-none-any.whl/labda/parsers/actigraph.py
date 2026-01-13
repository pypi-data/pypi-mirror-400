import io
from contextlib import redirect_stdout
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from pygt3x.reader import FileReader

from .parser import FileParser

# Mapping of CSV export modes to column names.
CSV_EXPORT_MODES = {
    12: [
        "counts_y",
        "counts_x",
        "counts_z",
    ],
    61: [
        "counts_y",
        "counts_x",
        "counts_z",
        "steps",
        "lux",
        "non_wear",
        "standing",
        "sitting",
        "lying",
    ],
}


@dataclass
class Actigraph(FileParser):
    """Parses ActiGraph accelerometer data from binary and CSV formats.

    This parser supports two distinct ActiGraph file types:

    1.  **.gt3x (Binary):** High-frequency raw acceleration data.
    2.  **.csv (Export):** Aggregated "epoch" data (counts), often containing
        derived metrics like steps or lux.

    The parser automatically handles the manufacturer's proprietary header formats,
    timestamp decoding, and timezone conversion to UTC.
    """

    pass

    def from_gt3x(
        self,
        path: Path | str,
        idle: Literal["ffill", "zero"] = "ffill",
    ) -> pd.DataFrame:
        """Parses a raw binary .gt3x file.

        Extracts x, y, z acceleration data. If the file contains timezone
        information, the datetime index is converted to UTC.

        Args:
            path (Path | str): Path to the .gt3x file.
            idle (Literal["ffill", "zero"]): Strategy for handling samples flagged as "Idle Sleep Mode" by the device.
            `'ffill'` (default): Preserves the raw values recorded by the device (often the last known value repeated).
            `'zero'`: Overwrites acceleration values with `0` during idle periods.

        Returns:
            pd.DataFrame: Standardized raw accelerometer data.

        Raises:
            ValueError: If `idle` is not one of 'ffill' or 'zero'.
            FileNotFoundError: If the file does not exist.
        """
        if idle not in ["ffill", "zero"]:
            raise ValueError(f"Invalid idle value: {idle}. Expected 'ffill' or 'zero'.")

        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".gt3x")

        with (
            FileReader(path.as_posix()) as reader,
            redirect_stdout(io.StringIO()),
        ):
            df = reader.to_pandas()
            tz = reader.info.timezone

        self.check_empty(df)

        df.rename(
            columns={"X": "acc_x", "Y": "acc_y", "Z": "acc_z", "IdleSleepMode": "idle"},
            inplace=True,
        )
        df.index.name = "datetime"
        df.index = pd.to_datetime(df.index, unit="s")

        if tz:
            tz = timezone(pd.Timedelta(tz))
            df.index = df.index.tz_localize(tz).tz_convert("UTC")

        if idle == "zero":
            df.loc[df["idle"], ["acc_x", "acc_y", "acc_z"]] = 0

        df.drop(columns="idle", inplace=True)

        return df

    def _parse_csv_dataframe(self, lines: list[str], mode: int) -> pd.DataFrame:
        """Internal helper to parse the data section of an ActiGraph CSV.

        Args:
            lines (list[str]): List of strings representing the CSV lines.
            mode (int): The ActiGraph export mode ID (e.g., 12, 61).

        Returns:
            pd.DataFrame: Dataframe with columns mapped based on `mode`.
        """
        columns = CSV_EXPORT_MODES.get(mode)

        if columns is None:
            raise ValueError(f"Unsupported mode: {mode}")

        df = pd.read_csv(io.StringIO("\n".join(lines)), header="infer")
        df.columns = columns

        return df

    def _parse_csv_header(self, lines: list[str], datetime_format: str) -> dict[str, Any]:
        """Internal helper to parse the 10-line metadata header of an ActiGraph CSV.

        Extracts the start datetime, epoch duration, and export mode.
        """
        start_time = lines[2].split()[-1].strip()
        start_date = lines[3].split()[-1].strip()
        start_datetime = pd.to_datetime(f"{start_date} {start_time}", format=datetime_format)

        epoch = pd.to_timedelta(lines[4].split()[-1].strip())
        mode = int(lines[-2].split("Mode =")[-1].strip())

        return {"epoch": epoch, "start_datetime": start_datetime, "mode": mode}

    def from_csv(
        self,
        path: str | Path,
        datetime_format: str = "ISO8601",
        header_rows: int = 10,
    ) -> pd.DataFrame:
        """Parses an ActiGraph CSV export (Epoch/Count data).

        ActiGraph CSVs typically contain aggregated "counts" rather than raw
        acceleration. This method parses the metadata header to reconstruct
        the correct datetime index.

        Args:
            path (str | Path): Path to the .csv file.
            datetime_format (str): Format string for parsing the header date/time.
                Defaults to "ISO8601".
            header_rows (int): Number of header lines to skip before data begins.
                Defaults to 10 (standard ActiGraph export).

        Returns:
            pd.DataFrame: A DataFrame containing epoch-level data.
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".csv")

        with path.open("r") as f:
            lines = f.readlines()

        header = self._parse_csv_header(lines[:header_rows], datetime_format)
        df = self._parse_csv_dataframe(lines[header_rows:], header["mode"])
        df.index = pd.date_range(
            start=header["start_datetime"],
            periods=len(df),
            freq=header["epoch"],
            name="datetime",
        )

        return df
