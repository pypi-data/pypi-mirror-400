import logging
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

# Path object for the script file
SCRIPT_FOLDER = Path(__file__).resolve().parent

logger = logging.getLogger(__name__)


class Indicators:
    def __init__(self):
        """Initializes the Indicators class."""
        # Load the z-scores data from a parquet file
        self.z_scores = pd.read_parquet(SCRIPT_FOLDER / "who_bmi_z_score.parquet")

    def _age_to_months(self, age: float) -> int:
        return round(age * 12)

    def bmi(self, height: float, weight: float):
        height_metres = height / 100
        bmi = weight / (height_metres**2)
        return bmi

    def _get_lms_values(self, gender: Literal["male", "female"], months: int) -> tuple:
        gender = gender.lower()  # type: ignore[assignment]

        if gender not in ["male", "female"]:
            raise ValueError(f"Invalid gender: {gender}. Expected 'male' or 'female'.")

        df = self.z_scores
        row = df[(df["Month"] == months) & (df["Gender"] == gender)].iloc[0]

        if row.empty:
            raise ValueError(f"No data found for age {months} months.")

        return row["L"], row["M"], row["S"]

    def _calculate_bmi_z_score(self, bmi: float, l: float, m: float, s: float) -> float:
        return (((bmi / m) ** l - 1) / (l * s)).round(4).item()

    def bmiz(
        self,
        age: float,
        gender: Literal["male", "female"],
        height: float,
        weight: float,
    ) -> float | None:
        if np.isnan(age) or np.isnan(height) or np.isnan(weight):
            logger.warning(
                "Age, height, or weight is NaN. Cannot compute BMI z-score. Returning None."
            )
            return None

        bmi = self.bmi(height, weight)
        age_in_months = self._age_to_months(age)
        l, m, s = self._get_lms_values(gender, age_in_months)
        return self._calculate_bmi_z_score(bmi, l, m, s)
