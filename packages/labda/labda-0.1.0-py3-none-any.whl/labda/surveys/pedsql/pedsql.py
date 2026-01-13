from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .pedsql4 import get_alphas, get_scores, questions


@dataclass
class Pedsql:
    version: Literal["Generic"]
    respondent: Literal["child", "parent"]
    type: Literal["toddler", "child", "adult"]

    def __post_init__(self):
        if self.version not in ["Generic"]:
            raise ValueError("Version must be one of: 'Generic'")

        if self.respondent not in ["child", "parent"]:
            raise ValueError("Respondent must be either 'child' or 'parent'")

        if self.type not in ["toddler", "child", "adult"]:
            raise ValueError("Type must be either 'toddler', 'child', or 'adult'")

        if (
            self.version != "Generic"
            and self.respondent != "child"
            and self.type != "child"
        ):
            raise NotImplementedError(
                "Only PedsQL Generic for child self-report is implemented."
            )

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        return get_scores(df)

    def cronbach_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        return get_alphas(df)

    @property
    def questions(self) -> list[str]:
        return questions()
