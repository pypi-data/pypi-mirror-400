from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Expander:
    pass

    def timedelta(self, df: pd.DataFrame | pd.Series) -> pd.Series:
        deltas = pd.Series(
            df.index.diff(),  # type: ignore
            index=df.index,
            name="timedelta",
        )

        return deltas

    def vector_magnitude(self, df: pd.DataFrame) -> pd.Series:
        vm = np.linalg.norm(df, axis=1)
        vm = pd.Series(vm, index=df.index, name="vector_magnitude", dtype=np.float32)

        return vm
