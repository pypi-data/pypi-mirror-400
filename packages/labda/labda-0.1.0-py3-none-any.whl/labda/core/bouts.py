from dataclasses import dataclass
from datetime import timedelta

import pandas as pd

from .utils import rle


@dataclass
class Bouts:
    epoch: str | timedelta
    min_value: float
    max_value: float
    min_duration: str | timedelta
    interruption_min_value: float | None = None
    interruption_max_value: float | None = None
    interruption_max_duration: str | timedelta | None = None
    interruption_between_duration: str | timedelta | None = None

    def __post_init__(self) -> None:
        self.epoch = pd.Timedelta(self.epoch).to_pytimedelta()
        self.min_duration = pd.Timedelta(self.min_duration).to_pytimedelta()

        if self.min_value > self.max_value:
            raise ValueError("Min value must be less than max value.")

        if (
            self.interruption_min_value is not None
            or self.interruption_max_value is not None
        ) and self.interruption_min_value > self.interruption_max_value:
            raise ValueError("Interruption min value must be less than max value.")

        if self.interruption_max_duration is not None:
            self.interruption_max_duration = pd.Timedelta(
                self.interruption_max_duration
            ).to_pytimedelta()

        if self.interruption_between_duration is not None:
            self.interruption_between_duration = pd.Timedelta(
                self.interruption_between_duration
            ).to_pytimedelta()

    def fix_long_bouts(
        self, series: pd.Series, epoch: timedelta, max_duration: timedelta
    ) -> pd.Series:
        """Fixes long bouts in a series by marking them as False. Input series must be boolean."""
        df = series.to_frame("valid").copy()
        df["id"] = rle(df["valid"])
        durations = (
            df[df["valid"]]
            .groupby("id")
            .apply(lambda x: x.index[-1] - x.index[0], include_groups=False)
        )
        if not durations.empty:
            durations += epoch  # Accounting for epoch calculation (last - first which is always short by one period)
            invalid = durations[durations > max_duration].index.values
            df.loc[df["id"].isin(invalid), "valid"] = False

        return df["valid"]

    def fix_surrounding_interruptions(
        self, df: pd.DataFrame, protected_duration: timedelta
    ) -> pd.Series:
        """Fixes interruptions which are too close to another interruption. Input dataframe must have 'valid' and 'interruption' columns (boolean)."""
        df = df[["valid", "interruption"]].copy()
        df["interruption_id"] = rle(df["interruption"])

        invalid_interruptions = []

        for index, interruption in df[df["interruption"]].groupby("interruption_id"):
            start = interruption.index[0] - protected_duration
            end = interruption.index[-1] + protected_duration
            protected = df.loc[
                (df.index >= start)
                & (df.index <= end)
                & ~df.index.isin(interruption.index),
                "interruption",
            ]  # type: pd.Series # type:ignore

            if protected.any():
                invalid_interruptions.append(index)

        df.loc[df["interruption_id"].isin(invalid_interruptions), "interruption"] = (
            False
        )

        return df["interruption"]

    def get_valid_bouts(
        self, series: pd.Series, epoch: timedelta, min_duration: timedelta
    ) -> pd.Series:
        """Extracts bouts from a series based on validity and duration."""
        df = series.to_frame("valid").copy()
        df["id"] = rle(df["valid"])
        durations = (
            df[df["valid"]]
            .groupby("id")
            .apply(lambda x: x.index[-1] - x.index[0], include_groups=False)
        )
        durations += epoch  # Accounting for epoch calculation (last - first which is always short by one period)
        invalid = durations[durations < min_duration].index.values
        df.loc[df["id"].isin(invalid), "valid"] = False

        return df["valid"]

    def compute(self, series: pd.Series) -> pd.Series:
        df = series.to_frame("value").asfreq(self.epoch, fill_value=0).copy()
        df["valid"] = df["value"].between(
            self.min_value, self.max_value, inclusive="both"
        )  # Mark valid values

        if (
            self.interruption_min_value is not None
            and self.interruption_max_value is not None
            and self.interruption_max_duration is not None
        ):
            df["interruption"] = (
                df["value"].between(
                    self.interruption_min_value,
                    self.interruption_max_value,
                    inclusive="both",
                )
                & ~df["valid"]
            )  # Mark interruptions
            df["interruption"] = self.fix_long_bouts(
                df["interruption"],
                self.epoch,  # type: ignore
                self.interruption_max_duration,  # type: ignore
            )

            if self.interruption_between_duration is not None:
                df["interruption"] = self.fix_surrounding_interruptions(
                    df,
                    self.interruption_between_duration,  # type: ignore
                )

            df["valid"] = df["valid"] | df["interruption"]

        if df["valid"].any():
            df["bouts"] = self.get_valid_bouts(
                df["valid"],
                self.epoch,  # type: ignore
                self.min_duration,  # type: ignore
            )
        else:
            df["bouts"] = False

        return df["bouts"]
