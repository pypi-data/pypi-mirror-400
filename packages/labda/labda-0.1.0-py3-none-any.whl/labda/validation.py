import altair as alt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def _get_metrics(true: pd.Series, pred: pd.Series, labels: list[str]) -> pd.DataFrame:
    metrics = precision_recall_fscore_support(
        true.values,  # type: ignore
        pred.values,  # type: ignore
        average=None,
        labels=labels,
        zero_division=np.nan,  # type: ignore
    )
    metrics = pd.DataFrame(
        metrics,
        columns=labels,
        index=["precision", "recall", "fscore", "support"],
    )
    no_support = metrics.loc["support"] == 0
    metrics.loc[:, no_support] = np.nan  # type: ignore
    accuracy = accuracy_score(
        true.values,  # type: ignore
        pred.values,  # type: ignore
    )
    accuracy = pd.DataFrame(accuracy, columns=metrics.columns, index=["accuracy"])
    metrics = pd.concat([metrics, accuracy], axis=0)
    metrics = metrics.melt(
        var_name="label",
        value_name="value",
        ignore_index=False,
    ).reset_index(names="metric")

    return metrics


def get_metrics(
    df: pd.DataFrame, true: str, pred: str, group: str, labels: list[str]
) -> pd.DataFrame:
    metrics = []

    for id, temp in df.groupby(group):
        results = _get_metrics(temp[true], temp[pred], labels=labels)
        results["id"] = id
        metrics.append(results)

    metrics = pd.concat(metrics, ignore_index=True)

    return metrics


def _get_scores(true: pd.Series, pred: pd.Series) -> pd.DataFrame:
    total = pd.crosstab(
        index=true,
        columns=pred,
        dropna=False,
    ).sum(axis=1)

    df = pd.crosstab(
        index=true,
        columns=pred,
        dropna=False,
        normalize="index",
    )
    df["support"] = total
    df = df.melt(var_name="pred", value_name="value", ignore_index=False).reset_index(
        names="true"
    )

    return df


def get_scores(
    df: pd.DataFrame,
    true: str,
    pred: str,
    group: str,
) -> pd.DataFrame:
    scores = []

    for id, temp in df.groupby(group):
        results = _get_scores(temp[true], temp[pred])
        results["id"] = id
        scores.append(results)

    scores = pd.concat(scores, axis=0)

    return scores


def get_mean_ci(df: pd.DataFrame) -> pd.Series:
    return df.apply(
        lambda x: f"{x['mean']:.2f} [{x['lower']:.2f}, {x['upper']:.2f}]", axis=1
    )


def get_mean_std(df: pd.DataFrame) -> pd.Series:
    return df.apply(lambda x: f"{x['mean']:.2f} ± {x['std']:.2f}", axis=1)


def summarize_values(df: pd.DataFrame, group: list[str]) -> pd.DataFrame:
    metrics = []

    for id, temp in df.groupby(group):
        n_total = len(temp)

        values = temp.loc[temp["value"].notna(), "value"]

        n = len(values)

        if values.empty:
            continue

        sum = values.sum()
        mean = values.mean()
        std = values.std()
        t = stats.t.ppf(0.95, df=n - 1)
        e = t * (std / np.sqrt(n))
        lower, upper = mean - e, mean + e
        lower, upper = np.clip(lower, 0, 1), np.clip(upper, 0, 1)

        results = {}
        for col in group:
            results[col] = id[group.index(col)]

        results.update(
            {
                "n": n,
                "n_total": n_total,
                "sum": sum,
                "mean": mean,
                "std": std,
                "lower": lower,
                "upper": upper,
            }
        )

        metrics.append(results)

    return pd.DataFrame(metrics)


def get_table(df: pd.DataFrame):
    df = df.copy()
    df["table"] = get_mean_ci(df)
    support = df["metric"] == "support"
    df.loc[support, "table"] = get_mean_std(df.loc[support])

    other = df.loc[support, ["label"]]
    other["support_total"] = df.loc[support, "sum"]
    other["n"] = df.loc[support, "n"]
    other["n_total"] = df.loc[support, "n_total"]
    other.set_index("label", inplace=True)
    df = df.pivot(index="label", columns="metric", values="table")
    df = pd.concat([df, other], axis=1)

    return df


def get_confusion_matrix(
    true: pd.Series,
    pred: pd.Series,
    labels: list[str],
    title: str = "Confusion Matrix",
    color: str = "purples",
    x_title: str | None = "Predicted",
    y_title: str | None = "True",
    hide_yaxis: bool = False,
    size: tuple[int, int] = (250, 250),
) -> alt.LayerChart:
    matrix = confusion_matrix(true, pred, labels=labels, normalize="true").round(2)
    matrix = np.flip(matrix, axis=1)

    labels = [label.capitalize() for label in labels]
    df = (
        pd.DataFrame(matrix, index=labels, columns=labels[::-1])
        .reset_index()
        .melt(id_vars="index")
    )
    df.columns = ["True", "Predicted", "Value"]

    title_size = 14
    axes_title_size = 12
    label_size = 12

    font = "Open Sans"
    axis = alt.Axis(
        titleFont=font,
        titleFontSize=axes_title_size,
        labelFont=font,
        labelFontSize=label_size,
    )

    x = alt.X(
        "Predicted:N",
        sort=labels[::-1],
        axis=axis,
        title=x_title,
    )
    y = alt.Y(
        "True:N",
        sort=labels,
        axis=None if hide_yaxis else axis,
        title=y_title,
    )

    # Base heatmap layer
    heatmap = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=x,
            y=y,
            color=alt.Color("Value:Q", scale=alt.Scale(scheme=color), legend=None),
        )
        .properties(
            title=alt.Title(
                text=title,
                fontSize=title_size,
                fontWeight="bold",
                font=font,
            ),
            width=size[0],
            height=size[1],
        )
    )

    text_mean = (
        alt.Chart(df)
        .mark_text(
            align="center",
            baseline="middle",
            fontSize=label_size,
            font=font,
        )
        .encode(
            x=x,
            y=y,
            text=alt.condition(
                alt.datum.Value == 0,
                alt.value(""),  # If the count is 0, display an empty string
                alt.Text("Value:Q", format=".2f"),  # Otherwise, display the count
            ),
            color=alt.condition(
                alt.datum.Value > 0.50, alt.value("white"), alt.value("black")
            ),
        )
    )

    chart = heatmap + text_mean

    return chart


def create_report(
    df: pd.DataFrame,
    true: str,
    pred: str,
    group: str,
    title: str,
    labels: list[str],
    hide_yaxis: bool = False,
    color: str = "greens",
    size: tuple[int, int] = (300, 300),
) -> tuple[alt.LayerChart, pd.DataFrame]:
    metrics = get_metrics(df, true, pred, group, labels)

    summarized_metrics = summarize_values(metrics, ["metric", "label"])
    table = get_table(summarized_metrics).T
    table = table[labels]

    chart = get_confusion_matrix(
        df[true],
        df[pred],
        labels,
        title=title,
        color=color,
        y_title="True",
        x_title="Predicted",
        hide_yaxis=hide_yaxis,
        size=size,
    )

    return chart, table
