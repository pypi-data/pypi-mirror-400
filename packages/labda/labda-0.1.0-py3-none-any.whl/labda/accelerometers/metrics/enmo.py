from datetime import timedelta
from typing import Literal

import numpy as np
import pandas as pd


def get_enmo(
    df: pd.DataFrame,
    epoch: timedelta,
    *,
    absolute: bool = False,
    trim: bool = True,
) -> pd.Series:
    name: Literal["enmo", "enmoa"] = "enmo"

    # Calculate vector magnitude and subtract 1g (gravity)
    time = df.index
    vm = np.linalg.norm(df.values, axis=1) - 1.0
    del df

    # Apply absolute if requested
    if absolute:
        vm = np.abs(vm)
        name = "enmoa"

    # Apply trimming if requested
    vm = np.maximum(vm, 0.0) if trim else vm

    # Create series with proper index
    enmo = pd.Series(vm, index=time, name=name, dtype=np.float32)
    del vm, time

    # Resample to epoch
    enmo = enmo.resample(epoch).mean().fillna(0)

    return enmo * 1000  # Convert to mg units
