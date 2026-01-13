import logging
from dataclasses import dataclass
from datetime import time, timedelta
from typing import Any

import altair as alt
import pandas as pd

from .utils import parse_datetime_or_time

logger = logging.getLogger(__name__)
alt.data_transformers.enable("vegafusion")

WEAR_PLOT = {
    "wear": {
        True: {"text": "Wear", "color": "#66BB6A"},
        False: {"text": "Non-wear", "color": "#BDBDBD"},
    },
    "title": "Wear",
    "x": "Time",
    "y": "Day",
    "legend": "Wear",
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
class Wear:
    pass

    def days(
        self,
        df: pd.DataFrame | pd.Series,
        sampling_frequency: timedelta | float,
        start: str | time | None = None,
        end: str | time | None = None,
    ) -> pd.Series:
        series = df["wear"] if isinstance(df, pd.DataFrame) else df

        if start:
            start = parse_datetime_or_time(start)  # type: ignore
            series = series.loc[series.index.time >= start]  # type: ignore

        if end:
            end = parse_datetime_or_time(end)  # type: ignore
            series = series.loc[series.index.time < end]  # type: ignore

        grouped = series.groupby(pd.Grouper(freq="D", origin="start_day", sort=True))

        if isinstance(sampling_frequency, timedelta):
            sampling_frequency = 1 / sampling_frequency.total_seconds()

        stats = grouped.apply(lambda x: x.sum() / sampling_frequency)
        stats = stats[stats > 0]  # Filter out zero-duration days
        stats = pd.to_timedelta(stats, unit="s")
        stats.name = "duration"

        return stats

    def filter_days(
        self,
        df: pd.DataFrame | pd.Series,
        sampling_frequency: timedelta | float,
        min_duration: str | timedelta,
        start: str | time | None = None,
        end: str | time | None = None,
    ) -> pd.DataFrame:
        days = self.days(df, sampling_frequency, start, end)

        min_duration = pd.Timedelta(min_duration).to_pytimedelta()
        valid_days = days[days > min_duration]

        if valid_days.empty:
            logger.warning("No valid days found.")
            return pd.DataFrame(columns=df.columns)

        return df[df.index.normalize().isin(valid_days.index)].copy()  # type: ignore

    def plot(
        self,
        df: pd.DataFrame | pd.Series,
        sampling_frequency: timedelta | float,
        lang: dict = WEAR_PLOT,
    ) -> Any:
        # Setting up
        labels = {k: v["text"] for k, v in lang["wear"].items()}
        colors = [v["color"] for k, v in lang["wear"].items()]
        domain = list(labels.values())

        if isinstance(sampling_frequency, float):
            sampling_frequency = timedelta(seconds=1 / sampling_frequency)

        # Preparing data
        series = df["wear"] if isinstance(df, pd.DataFrame) else df
        start = series.index[0]
        end = series.index[-1]

        full_idx = pd.date_range(start=start, end=end, freq=sampling_frequency, name="datetime")
        series = series.reindex(full_idx, fill_value=False)

        df = series.to_frame(name="wear").reset_index()
        del series

        df["rle"] = (df["wear"] != df["wear"].shift()).cumsum()
        df["date"] = df["datetime"].dt.date  # type: ignore

        df = (
            df.groupby(["rle", "date"])
            .agg(
                wear=("wear", "first"),
                start_time=("datetime", "first"),
                end_time=("datetime", "last"),
            )
            .reset_index(drop=True)
        )
        df["end_time"] += sampling_frequency

        df["wear"] = df["wear"].replace(labels)
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
                    "wear:N",
                    title=lang["legend"],
                    scale=alt.Scale(domain=domain, range=colors),
                    legend=alt.Legend(labelFontSize=12, titleFontSize=14),
                ),
                tooltip=[
                    alt.Tooltip("hoursminutesseconds(start_time):T", title="Start Time", format="%H:%M"),
                    alt.Tooltip("wear:N", title="Wear"),
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
