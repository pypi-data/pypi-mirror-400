import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import altair as alt
import pandas as pd

from .acceleration import get_activity_intensities_from_acceleration_metric
from .counts import get_activity_intensities_from_counts
from .vilpa import get_vilpa

logger = logging.getLogger(__name__)


INTENSITY_PLOT = {
    "activity_intensity": {
        "non-wear": {"text": "Non-wear", "color": "#BDBDBD"},
        "sedentary": {"text": "Sedentary", "color": "#42A5F5"},
        "light": {"text": "Light", "color": "#66BB6A"},
        "moderate": {"text": "Moderate", "color": "#FF7043"},
        "vigorous": {"text": "Vigorous", "color": "#E53935"},
    },
    "title": "Activity Intensity",
    "x": "Time",
    "y": "Day",
    "legend": "Intensity",
    "weekdays": {
        "Monday": "Monday",
        "Tuesday": "Tuesday",
        "Wednesday": "Wednesday",
        "Thursday": "Thursday",
        "Friday": "Friday",
        "Saturday": "Saturday",
        "Sunday": "Sunday",
    },
}


@dataclass
class ActivityIntensity:
    output_epoch: timedelta | None = None

    def __post_init__(self) -> None:
        if self.output_epoch is not None:
            self.output_epoch = pd.Timedelta(self.output_epoch).to_pytimedelta()

    def _resample_output(
        self,
        intensities: pd.Series,
        epoch: timedelta,
    ) -> pd.Series:
        # Resample to epochs if requested
        if self.output_epoch is not None:
            if self.output_epoch < epoch:
                raise ValueError(f"Output epoch {self.output_epoch} cannot be smaller than input epoch {epoch}.")
            elif self.output_epoch > epoch:
                logger.warning(
                    f"Resampling intensities from {epoch} to {self.output_epoch}. Majority voting will be used to determine the intensity for each output epoch."
                )

                # Use mode to resample activity intensities (most frequent intensity in the epoch)
                intensities = intensities.resample(self.output_epoch).apply(
                    lambda x: None if x.empty else x.mode()[0]  # type: ignore
                )

        return intensities

    def from_counts(
        self,
        df: pd.DataFrame,
        cut_points: dict[str, Any],
        epoch: timedelta,
    ) -> pd.Series:
        counts = get_activity_intensities_from_counts(df, cut_points, epoch)
        counts = self._resample_output(counts, epoch)

        return counts

    def from_acceleration(
        self,
        df: pd.DataFrame | pd.Series,
        thresholds: dict[str, Any],
        epoch: timedelta,
    ) -> pd.Series:
        df = df.to_frame() if isinstance(df, pd.Series) else df
        accelerations = get_activity_intensities_from_acceleration_metric(df, thresholds, epoch)
        accelerations = self._resample_output(accelerations, epoch)

        return accelerations

    @staticmethod
    def vilpa(
        vpa: pd.Series,
        epoch: timedelta,
        min_duration: int = 30,
        min_epochs: int = 20,
        max_duration: int = 120,
    ) -> pd.Series:
        return get_vilpa(
            vpa,
            epoch,
            min_duration,
            min_epochs,
            max_duration,
        )

    def plot(
        self,
        df: pd.DataFrame | pd.Series,
        sampling_frequency: timedelta | float,
        lang: dict = INTENSITY_PLOT,
    ) -> Any:
        # Setting up
        labels = {k: v["text"] for k, v in lang["activity_intensity"].items()}
        colors = [v["color"] for k, v in lang["activity_intensity"].items()]
        domain = list(labels.values())

        if isinstance(sampling_frequency, float):
            sampling_frequency = timedelta(seconds=1 / sampling_frequency)

        # Preparing data
        if isinstance(df, pd.DataFrame):
            series = df["activity_intensity"].astype(str).copy()

            if "wear" in df.columns:
                series.loc[~df["wear"]] = "non-wear"
        else:
            series = df.astype(str).copy()

        start = series.index[0]
        end = series.index[-1]

        full_idx = pd.date_range(start=start, end=end, freq=sampling_frequency, name="datetime")
        series = series.reindex(full_idx, fill_value="non-wear")

        df = series.to_frame(name="activity_intensity").reset_index()
        del series

        df["rle"] = (df["activity_intensity"] != df["activity_intensity"].shift()).cumsum()
        df["date"] = df["datetime"].dt.date  # type: ignore

        df = (
            df.groupby(["rle", "date"])
            .agg(
                activity_intensity=("activity_intensity", "first"),
                start_time=("datetime", "first"),
                end_time=("datetime", "last"),
            )
            .reset_index(drop=True)
        )
        df["end_time"] += sampling_frequency

        df["activity_intensity"] = df["activity_intensity"].replace(labels)
        df["start_time"] = df["start_time"].dt.tz_localize(None)  # type: ignore
        df["end_time"] = df["end_time"].dt.tz_localize(None)  # type: ignore

        df["duration"] = df["end_time"] - df["start_time"]
        df["duration"] = df["duration"].dt.total_seconds() / 60.0  # duration in minutes # type: ignore
        df["end_time"] -= pd.Timedelta(seconds=1)  # Adjust end time for proper display

        df["y_label"] = (
            df["start_time"].dt.strftime("%d-%m-%Y") + " (" + df["start_time"].dt.day_name().map(lang["weekdays"]) + ")"  # type: ignore
        )

        heatmap = (
            alt.Chart(df)
            .mark_rect(opacity=1)
            .encode(
                x=alt.X(
                    "hoursminutesseconds(start_time):T",
                    title=lang["x"],
                    axis=alt.Axis(
                        labelFontSize=12,
                        titleFontSize=14,
                        format="%H:%M",
                        ticks=True,
                    ),
                ),
                x2=alt.X2("hoursminutesseconds(end_time):T"),
                y=alt.Y(
                    "y_label:O",
                    title=lang["y"],
                    axis=alt.Axis(
                        labelFontSize=12,
                        titleFontSize=14,
                        ticks=True,
                        grid=True,
                        gridColor="gray",
                        gridOpacity=0.1,
                    ),
                    sort=None,
                ),
                color=alt.Color(
                    "activity_intensity:N",
                    title=lang["legend"],
                    scale=alt.Scale(domain=domain, range=colors),
                    legend=alt.Legend(labelFontSize=12, titleFontSize=14),
                ),
                tooltip=[
                    alt.Tooltip("hoursminutesseconds(start_time):T", title="Start Time", format="%H:%M:%S"),
                    alt.Tooltip("activity_intensity:N", title="Activity Intensity"),
                    alt.Tooltip("duration:Q", title="Duration (min)", format=".2f"),
                ],
            )
            .properties(
                width=960,
                height=270,
                title=alt.TitleParams(text=lang["title"], fontSize=16),
            )
        )

        return heatmap
