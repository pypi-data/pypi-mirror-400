from datetime import timedelta
from typing import Any

import pandas as pd

from ...core.expander import Expander
from ...core.resampler import Resampler
from ...core.utils import check_for_required_data

COUNTS_CUT_POINTS: dict[str, Any] = {
    "freedson_adults_1998": {
        "name": "Freedson Adults (1998)",
        "reference": "https://journals.lww.com/acsm-msse/fulltext/1998/05000/calibration_of_the_computer_science_and.21.aspx",
        "epoch": "60s",
        "category": "adults",
        "placement": "hip",
        "required_data": ["counts_y"],
        "thresholds": [
            {"name": "sedentary", "max": 99},
            {"name": "light", "max": 1951},
            {"name": "moderate", "max": 5724},
            {"name": "vigorous", "max": 9498},
            {"name": "very-vigorous", "max": float("inf")},
        ],
    },
    "freedson_adults_vm3_2011": {
        "name": "Freedson Adults VM3 (2011)",
        "reference": "https://doi.org/10.1016/j.jsams.2011.04.003",
        "epoch": "60s",
        "category": "adults",
        "placement": "hip",
        "required_data": ["counts_x", "counts_y", "counts_z"],
        "thresholds": [
            {"name": "light", "max": 2689},
            {"name": "moderate", "max": 6166},
            {"name": "vigorous", "max": 9642},
            {"name": "very-vigorous", "max": float("inf")},
        ],
    },
    "freedson_children_2005": {
        "name": "Freedson Children (2005)",
        "reference": "https://doi.org/10.1249/01.mss.0000185658.28284.ba",
        "epoch": "60s",
        "category": "children",
        "placement": "hip",
        "required_data": ["counts_y"],
        "thresholds": [
            {"name": "sedentary", "max": 149},
            {"name": "light", "max": 499},
            {"name": "moderate", "max": 3999},
            {"name": "vigorous", "max": 7599},
            {"name": "very-vigorous", "max": float("inf")},
        ],
    },
    "evenson_children_2018": {
        "name": "Evenson Children (2008)",
        "reference": "https://doi.org/10.1080/02640410802334196",
        "epoch": "15s",
        "category": "children",
        "placement": "hip",
        "required_data": ["counts_y"],
        "thresholds": [
            {"name": "sedentary", "max": 25},
            {"name": "light", "max": 573},
            {"name": "moderate", "max": 1002},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
    "troiano_adults_2008": {
        "name": "Troiano Adults (2008)",
        "reference": "https://doi.org/10.1249/mss.0b013e31815a51b3",
        "epoch": "60s",
        "category": "adults",
        "placement": "hip",
        "required_data": ["counts_y"],
        "thresholds": [
            {"name": "sedentary", "max": 99},
            {"name": "light", "max": 2019},
            {"name": "moderate", "max": 5998},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
}


def get_activity_intensities_from_counts(
    df: pd.DataFrame,
    thresholds: dict[str, Any],
    epoch: timedelta,
) -> pd.Series:
    epoch_cut_points = pd.to_timedelta(thresholds["epoch"])
    required_data = thresholds["required_data"]

    cut_points = thresholds["thresholds"]
    bins = [-float("inf")] + [cp["max"] for cp in cut_points]
    labels = [cp["name"] for cp in cut_points]

    check_for_required_data(required_data, df.columns)

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
        raise ValueError("For counts data, only uniaxial or vector magnitude data is supported.")

    intensities = pd.cut(df[required_data], bins=bins, labels=labels)
    intensities.name = "activity_intensity"

    return intensities
