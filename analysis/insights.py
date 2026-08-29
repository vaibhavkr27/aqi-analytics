"""
CityAir — Insight Generation

Converts analytical results and statistical anomalies
into human-readable insights.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# ============================================================
# Helpers
# ============================================================

PARAMETER_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "so2": "SO₂",
    "co": "CO",
}


def parameter_label(parameter: str) -> str:
    """Return a user-friendly pollutant name."""

    return PARAMETER_LABELS.get(
        parameter,
        parameter.upper(),
    )


def format_value(value: Any) -> str:
    """Format numerical values for human-readable output."""

    if pd.isna(value):
        return "N/A"

    value = float(value)

    if value >= 100:
        return f"{value:.0f}"

    if value >= 10:
        return f"{value:.1f}"

    return f"{value:.2f}"


def format_datetime(timestamp: Any) -> str:
    """Format timestamp in a readable IST format."""

    if pd.isna(timestamp):
        return "Unknown time"

    timestamp = pd.Timestamp(timestamp)

    return (
        timestamp.strftime("%B")
        + f" {timestamp.day}, "
        + timestamp.strftime(
            "%Y at %H:%M IST"
        )
    )


# ============================================================
# Pollution Spike Insights
# ============================================================

def generate_anomaly_insights(
    df: pd.DataFrame,
    max_insights: int = 10,
) -> list[str]:
    """
    Generate human-readable insights for statistically
    significant anomalies.

    An anomaly is NOT removed from the dataset.
    It is interpreted as an unusual observation.
    """

    if df.empty:
        return []

    if "is_statistical_anomaly" not in df.columns:
        return []

    anomalies = df[
        df["is_statistical_anomaly"]
    ].copy()

    if anomalies.empty:
        return []

    # Rank strongest anomalies first.
    if "robust_z_score" in anomalies.columns:

        anomalies["_severity"] = (
            anomalies["robust_z_score"]
            .abs()
        )

        anomalies = anomalies.sort_values(
            "_severity",
            ascending=False,
        )

    insights = []

    for _, row in anomalies.head(
        max_insights
    ).iterrows():

        parameter = parameter_label(
            row["parameter"]
        )

        value = format_value(
            row["value_standardized"]
        )

        unit = row[
            "standardized_unit"
        ]

        timestamp = format_datetime(
            row["measured_at_ist"]
        )

        deviation = row.get(
            "deviation_percent"
        )

        robust_z = row.get(
            "robust_z_score"
        )

        # ----------------------------------------------------
        # Build explanation
        # ----------------------------------------------------

        message = (
            f"{parameter} pollution spike detected: "
            f"on {timestamp}, the concentration "
            f"reached {value} {unit}"
        )

        if not pd.isna(deviation):

            message += (
                f", approximately "
                f"{float(deviation):.0f}% "
                f"away from its recent local baseline"
            )

        if not pd.isna(robust_z):

            message += (
                f" (robust Z-score: "
                f"{float(robust_z):.2f})"
            )

        message += "."

        insights.append(message)

    return insights


# ============================================================
# Peak Pollution Insights
# ============================================================

def generate_peak_insights(
    df: pd.DataFrame,
) -> list[str]:
    """
    Identify the highest recorded concentration
    for each pollutant.
    """

    if df.empty:
        return []

    insights = []

    for parameter in (
        df["parameter"]
        .dropna()
        .unique()
    ):

        parameter_df = df[
            df["parameter"] == parameter
        ].copy()

        if parameter_df.empty:
            continue

        peak_index = (
            parameter_df[
                "value_standardized"
            ]
            .idxmax()
        )

        peak = parameter_df.loc[
            peak_index
        ]

        pollutant = parameter_label(
            parameter
        )

        value = format_value(
            peak["value_standardized"]
        )

        unit = peak[
            "standardized_unit"
        ]

        timestamp = format_datetime(
            peak["measured_at_ist"]
        )

        insights.append(
            f"Highest {pollutant} concentration "
            f"was {value} {unit}, recorded on "
            f"{timestamp}."
        )

    return insights


# ============================================================
# Hourly Pattern Insights
# ============================================================

def generate_hourly_insights(
    df: pd.DataFrame,
) -> list[str]:
    """
    Identify the hour with the highest and lowest
    average concentration for PM2.5 and PM10.
    """

    if df.empty:
        return []

    insights = []

    for parameter in [
        "pm25",
        "pm10",
    ]:

        parameter_df = df[
            df["parameter"] == parameter
        ].copy()

        if parameter_df.empty:
            continue

        hourly = (
            parameter_df
            .groupby("hour")[
                "value_standardized"
            ]
            .mean()
            .dropna()
        )

        if hourly.empty:
            continue

        highest_hour = hourly.idxmax()
        lowest_hour = hourly.idxmin()

        highest_value = hourly.max()
        lowest_value = hourly.min()

        pollutant = parameter_label(
            parameter
        )

        unit = parameter_df[
            "standardized_unit"
        ].iloc[0]

        insights.append(
            f"{pollutant} had its highest "
            f"average concentration around "
            f"{int(highest_hour):02d}:00 IST "
            f"({format_value(highest_value)} "
            f"{unit})."
        )

        insights.append(
            f"{pollutant} had its lowest "
            f"average concentration around "
            f"{int(lowest_hour):02d}:00 IST "
            f"({format_value(lowest_value)} "
            f"{unit})."
        )

    return insights


# ============================================================
# Daily Trend Insights
# ============================================================

def generate_daily_insights(
    df: pd.DataFrame,
) -> list[str]:
    """
    Identify highest and lowest average pollution days.
    """

    if df.empty:
        return []

    insights = []

    for parameter in [
        "pm25",
        "pm10",
    ]:

        parameter_df = df[
            df["parameter"] == parameter
        ].copy()

        if parameter_df.empty:
            continue

        daily = (
            parameter_df
            .groupby("date")[
                "value_standardized"
            ]
            .mean()
            .dropna()
        )

        if daily.empty:
            continue

        highest_day = daily.idxmax()
        lowest_day = daily.idxmin()

        highest_value = daily.max()
        lowest_value = daily.min()

        pollutant = parameter_label(
            parameter
        )

        unit = parameter_df[
            "standardized_unit"
        ].iloc[0]

        insights.append(
            f"{pollutant} had its highest "
            f"daily average on "
            f"{highest_day.strftime('%B %-d, %Y')}, "
            f"at {format_value(highest_value)} "
            f"{unit}."
        )

        insights.append(
            f"{pollutant} had its lowest "
            f"daily average on "
            f"{lowest_day.strftime('%B %-d, %Y')}, "
            f"at {format_value(lowest_value)} "
            f"{unit}."
        )

    return insights


# ============================================================
# Main Insight Generator
# ============================================================

def generate_insights(
    df: pd.DataFrame,
) -> dict[str, list[str]]:
    """
    Generate all user-facing insights.
    """

    return {
        "pollution_spikes": generate_anomaly_insights(
            df
        ),

        "peak_concentrations": generate_peak_insights(
            df
        ),

        "hourly_patterns": generate_hourly_insights(
            df
        ),

        "daily_patterns": generate_daily_insights(
            df
        ),
    }


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    print(
        "CityAir — Insight Generator"
    )

    print(
        "This module is designed to be "
        "called from analytics.py."
    )