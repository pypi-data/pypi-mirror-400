import logging
import warnings
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd
from skdh.preprocessing import AccelThresholdWearDetection

from ...core.bouts import Bouts
from ...core.expander import Expander
from ...core.resampler import Resampler
from ...core.wear import Wear

logger = logging.getLogger(__name__)

WEAR_COUNTS_ALGORITHMS: dict[str, Any] = {
    "troiano_2007": {
        "name": "Troiano (2007)",
        "reference": " https://doi.org/10.1249/mss.0b013e31815a51b3",
        "epoch": "60s",
        "category": ["children", "adolescents", "adults"],
        "placement": "hip",
        "required_data": [
            "counts_x",
            "counts_y",
            "counts_z",
        ],  # Originally developed for a uniaxial accelerometer but can be extended to work on triaxial accelerometers by calculating the VM. And it is commonly used that way.
        "params": {
            "bout_min_duration": "60m",
            "bout_max_value": 0,
            "artefact_max_duration": "2m",
            "artefact_max_value": 100,
        },
    },
    "choi_2011": {
        "name": "Choi (2011)",
        "reference": "https://doi.org/10.1249/MSS.0b013e318258cb36",
        "epoch": "60s",
        "category": ["children", "adolescents", "adults"],
        "placement": "hip",
        "required_data": [
            "counts_x",
            "counts_y",
            "counts_z",
        ],  # Originally developed for a uniaxial accelerometer but can be extended to work on triaxial accelerometers by calculating the VM. And it is commonly used that way.
        "params": {
            "bout_min_duration": "90m",
            "bout_max_value": 0,
            "artefact_max_duration": "2m",
            "artefact_between_duration": "30m",
            "artefact_max_value": 0,
        },
    },
}


@dataclass
class AccelerometerWear(Wear):
    output_epoch: timedelta | None = None

    def __post_init__(self) -> None:
        if self.output_epoch is not None:
            self.output_epoch = pd.Timedelta(self.output_epoch).to_pytimedelta()

    def from_acceleration(
        self,
        df: pd.DataFrame,
        hertz: float,
        **kwargs: Any,
    ) -> pd.Series:
        # Prepare data for wear detection
        time = df.index
        accel = df[["acc_x", "acc_y", "acc_z"]]
        del df

        # Initialize wear detector
        wear_detector = AccelThresholdWearDetection(**kwargs)

        # Perform wear detection with error handling
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            wear = wear_detector.predict(
                time=(time.astype(np.int64) // 10**9).values,
                accel=accel.values,
                fs=hertz,
            ).get("wear")

        if wear is None or len(wear) == 0:
            raise ValueError(
                "No wear periods found. Ensure the accelerometer data is valid and contains wear periods."
            )

        # Create boolean mask more efficiently using vectorized operations
        wear_mask = np.zeros(len(accel), dtype=bool)

        for start_idx, end_idx in wear:
            wear_mask[start_idx:end_idx] = True

        # Create Series with proper index
        wear_series = pd.Series(wear_mask, index=time, name="wear")

        # Resample to epochs if requested
        if self.output_epoch is not None:
            # Use max aggregation: if any sample in epoch is wear time, epoch is wear time
            wear_series = wear_series.resample(self.output_epoch).max().fillna(0)

        return wear_series.astype(bool)

    def check_for_required_data(
        self, required_data: list[str] | str, columns: Any
    ) -> None:
        if isinstance(required_data, str):
            required_data = [required_data]

        missing = [col for col in required_data if col not in columns]
        if missing:
            raise ValueError(
                f"Required data '{', '.join(missing)}' not found in the dataframe. Please check the input data and if the column exists, name it accordingly."
            )

    def from_counts(
        self, df: pd.DataFrame, algorithm: dict[str, Any], epoch: timedelta
    ) -> pd.Series:
        indexes = df.index

        epoch_cut_points = pd.to_timedelta(algorithm["epoch"])
        required_data = algorithm["required_data"]
        params = algorithm["params"]

        self.check_for_required_data(required_data, df.columns)

        if epoch_cut_points > epoch:
            df = Resampler(epoch_cut_points).resample(df[required_data], epoch)
        elif epoch_cut_points < epoch:
            raise ValueError(
                f"Epoch for cut points ({epoch_cut_points}) is smaller than the epoch of the data ({epoch}). Upsampling is not supported."
            )

        if required_data == ["counts_x", "counts_y", "counts_z"]:
            df = df[["counts_x", "counts_y", "counts_z"]].copy()
            df["counts_vm"] = Expander().vector_magnitude(df[required_data])
            required_data = "counts_vm"
        elif len(required_data) == 1:
            required_data = required_data[0]
        else:
            raise ValueError(
                "For counts data, only uniaxial or vector magnitude data is supported."
            )

        min_value = 0
        max_value = params["bout_max_value"]
        min_duration = params["bout_min_duration"]
        interruption_min_value = 0
        interruption_max_value = params.get("artefact_max_value", None)
        interruption_max_duration = params.get("artefact_max_duration", None)
        interruption_between_duration = params.get("artefact_between_duration", None)
        bouts = Bouts(
            epoch=epoch,
            min_value=min_value,
            max_value=max_value,
            min_duration=min_duration,
            interruption_min_value=interruption_min_value,
            interruption_max_value=interruption_max_value,
            interruption_max_duration=interruption_max_duration,
            interruption_between_duration=interruption_between_duration,
        ).compute(df[required_data])
        wear = pd.Series(~bouts, index=indexes, dtype="boolean").ffill().astype(bool)
        wear.name = "wear"

        # Resample to epochs if requested
        if self.output_epoch is not None:
            # Use max aggregation: if any sample in epoch is wear time, epoch is wear time
            wear = wear.resample(self.output_epoch).max().fillna(0)

        return wear.astype(bool)
