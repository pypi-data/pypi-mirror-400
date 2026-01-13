import logging
from datetime import timedelta
from typing import Any

import pandas as pd

from ...core.utils import check_for_required_data

logger = logging.getLogger(__name__)

ENMO_CUT_POINTS: dict[str, Any] = {
    "hildebrand_2014-2017": {
        "name": "Hildebrand (2014-2017, Actigraph)",
        "reference": [
            "https://doi.org/10.1249/MSS.0000000000000289",
            "https://doi.org/10.1111/sms.12795",
        ],
        "epoch": "5s",
        "category": "adults",
        "placement": "hip",
        "required_data": ["enmo"],
        "thresholds": [
            {"name": "sedentary", "max": 47.4},
            {"name": "light", "max": 69.1},
            {"name": "moderate", "max": 258.7},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
}


MAD_CUT_POINTS: dict[str, Any] = {
    "aittasalo_children_2015": {
        "name": "Aittasalo (2015, Actigraph)",
        "reference": "https://doi.org/10.1186/s13102-015-0010-0",
        "epoch": "5s",
        "category": "children",
        "placement": "hip",
        "required_data": ["mad"],
        "thresholds": [
            {"name": "sedentary", "max": 26.9},
            {"name": "light", "max": 332.0},
            {"name": "moderate", "max": 558.3},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
    "beck_children_thigh_2023": {
        "name": "Beck Children (2023, Thigh, Move4)",
        "reference": "https://doi.org/10.1186/s13102-023-00775-4",
        "epoch": "5s",
        "category": "children",
        "placement": "thigh",
        "required_data": ["mad"],
        "thresholds": [
            {"name": "sedentary", "max": 62.4},
            {"name": "light", "max": 260.7},
            {"name": "moderate", "max": 674.5},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
    "beck_children_hip_2023": {
        "name": "Beck Children (2023, Hip, Move4)",
        "reference": "https://doi.org/10.1186/s13102-023-00775-4",
        "epoch": "5s",
        "category": "children",
        "placement": "hip",
        "required_data": ["mad"],
        "thresholds": [
            {"name": "sedentary", "max": 52.9},
            {"name": "light", "max": 173.3},
            {"name": "moderate", "max": 543.6},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
    "vaha-ypya_hip_2015-2017": {
        "name": "Vaha-Ypya Adults (2015-2017, Hip, Hookie AM20)",
        "reference": [
            "https://doi.org/10.1371/journal.pone.0134813",
            "https://doi.org/10.1111/sms.13017",
        ],
        "epoch": "5s",  # Originally 6s, but opted for 5s here for consistency, and should have minimal impact
        "category": "adults",
        "placement": "hip",
        "required_data": ["mad"],
        "thresholds": [
            {"name": "sedentary", "max": 22.5},
            {"name": "light", "max": 91},
            {"name": "moderate", "max": 414},
            {"name": "vigorous", "max": float("inf")},
        ],
    },
}


def get_activity_intensities_from_acceleration_metric(
    df: pd.DataFrame,
    thresholds: dict[str, Any],
    epoch: timedelta,
):
    # TODO: Reformat this function and function from counts.py to reduce redundancy
    epoch_cut_points = pd.to_timedelta(thresholds["epoch"])
    required_data = thresholds["required_data"]

    cut_points = thresholds["thresholds"]
    bins = [-float("inf")] + [cp["max"] for cp in cut_points]
    labels = [cp["name"] for cp in cut_points]

    check_for_required_data(required_data, df.columns)

    if epoch_cut_points != epoch:
        raise ValueError(
            "Resampling is not supported for acceleration metric based intensity classification. Please provide data with the same epoch as the cut points."
        )

    if not len(required_data) == 1:
        raise ValueError("For acceleration metric data, only one axis (variable) is supported.")

    required_data = required_data[0]

    intensities = pd.cut(df[required_data], bins=bins, labels=labels)
    intensities.name = "activity_intensity"

    return intensities
