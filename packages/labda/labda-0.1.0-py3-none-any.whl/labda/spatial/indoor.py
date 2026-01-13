from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class IndoorDetector:
    variable: Literal[
        "satellites_viewed",  # 9 (F1: 42,93)
        "satellites_used",  # 7 (F1: 48,86)
        "satellites_ratio",  # 0.7 (F1: 46,40)
        "snr_viewed",  # 260 (F1: 71,18)
        "snr_used",  # 225 (F1: 46,80)
        "gnss_accuracy",
    ]
    limit: float

    def _post_init(self):
        if self.variable not in [
            "satellites_viewed",
            "satellites_used",
            "satellites_ratio",
            "snr_viewed",
            "snr_used",
            "gnss_accuracy",
        ]:
            raise ValueError(
                f"Invalid variable '{self.variable}'. Choose from: satellites_viewed, satellites_used, satellites_ratio, snr_viewed, snr_used, gnss_accuracy."
            )

    def _calculate_sat_ratio(self, df: pd.DataFrame) -> pd.Series:
        if (
            "satellites_viewed" not in df.columns
            and "satellites_used" not in df.columns
        ):
            raise ValueError(
                "Columns 'satellites_viewed' and 'satellites_used' are required to calculate 'satellites_ratio'."
            )

        df = df.loc[df["satellites_used"].notna() & df["satellites_viewed"].notna()]
        sat_ratio = df["satellites_used"] / df["satellites_viewed"]

        return sat_ratio

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        if self.variable not in df.columns:
            if self.variable == "satellites_ratio":
                print("Satellites ratio not found. Calculating satellites ratio.")
                indoor = self._calculate_sat_ratio(df)

            raise ValueError(f"Column '{self.variable}' does not exist in dataframe.")

        else:
            indoor = df[self.variable].dropna()

        if self.variable == "gnss_accuracy":
            indoor = (indoor >= self.limit).astype(int)
        else:
            indoor = (indoor <= self.limit).astype(int)

        indoor = pd.Series(indoor, index=df.index, name="indoor")

        return indoor
