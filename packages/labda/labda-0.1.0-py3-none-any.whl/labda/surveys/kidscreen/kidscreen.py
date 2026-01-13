from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .kidscreen27 import get_alphas, get_scores, questions


@dataclass
class Kidscreen:
    version: Literal[10, 27, 52]
    respondent: Literal["child", "parent"]
    type: Literal["self", "proxy"]

    def __post_init__(self):
        if self.version not in [10, 27, 52]:
            raise ValueError("Version must be one of: 10, 27, 52")

        if self.respondent not in ["child", "parent"]:
            raise ValueError("Respondent must be either 'child' or 'parent'")

        if self.type not in ["self", "proxy"]:
            raise ValueError("Type must be either 'self' or 'proxy'")

        if self.version != 27 and self.respondent != "child" and self.type != "self":
            raise NotImplementedError(
                "Only KIDSCREEN-27 for child self-report is implemented."
            )

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        return get_scores(df)

    def cronbach_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        return get_alphas(df)

    @property
    def questions(self) -> list[str]:
        return questions()
