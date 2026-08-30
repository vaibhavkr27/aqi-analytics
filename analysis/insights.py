"""
CityAir — Insight Generation

Converts analytical results and statistical anomalies
into human-readable insights.
"""

from __future__ import annotations

from typing import Any


# ============================================================
# Helpers
# ============================================================

PARAMETER_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
}


def parameter_label(
    parameter: str,
) -> str:
    """Return a user-friendly pollutant name."""

    return PARAMETER_LABELS.get(
        parameter,
        parameter.upper(),
    )


def format_value(
    value: Any,
) -> str:
    """Format numerical values for human-readable output."""

    if value is None:
        return "N/A"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if value >= 100:
        return f"{value:.0f}"

    if value >= 10:
        return f"{value:.1f}"

    return f"{value:.2f}"


def format_datetime(
    timestamp: Any,
) -> str:
    """Format timestamp in a readable format."""

    if timestamp is None:
        return "Unknown time"

    try:
        timestamp = str(timestamp)

        # Expected:
        # 2026-08-05 17:00:00+05:30

        date_part, time_part = timestamp.split(
            " ",
            1,
        )

        year, month, day = date_part.split(
            "-"
        )

        hour = time_part[:5]

        months = {
            "01": "January",
            "02": "February",
            "03": "March",
            "04": "April",
            "05": "May",
            "06": "June",
            "07": "July",
            "08": "August",
            "09": "September",
            "10": "October",
            "11": "November",
            "12": "December",
        }

        month_name = months.get(
            month,
            month,
        )

        return (
            f"{month_name} {int(day)}, "
            f"{year} at {hour} IST"
        )

    except (ValueError, AttributeError):
        return str(timestamp)


# ============================================================
# Pollution Spike Insights
# ============================================================


def generate_anomaly_insights(
    report: dict[str, Any],
    max_insights: int = 5,
) -> list[str]:
    """
    Convert statistical anomalies into meaningful
    pollution spike insights.
    """

    anomalies = report.get(
        "anomalies",
        [],
    )

    if not anomalies:
        return []

    valid_anomalies = []

    for anomaly in anomalies:

        value = anomaly.get("value")
        baseline = anomaly.get("local_median")
        deviation = anomaly.get("deviation_percent")

        if value is None:
            continue

        if baseline is None:
            continue

        if deviation is None:
            continue

        try:
            value = float(value)
            baseline = float(baseline)
            deviation = float(deviation)
        except (TypeError, ValueError):
            continue

        # Ignore unreliable zero-baseline anomalies,
        # such as the CO records in the current dataset.
        if baseline <= 0:
            continue

        # Only positive deviations represent pollution spikes.
        if deviation <= 0:
            continue

        valid_anomalies.append(anomaly)

    if not valid_anomalies:
        return []

    valid_anomalies.sort(
        key=lambda anomaly: float(
            anomaly.get(
                "deviation_percent",
                0,
            )
        ),
        reverse=True,
    )

    insights = []

    for anomaly in valid_anomalies[:max_insights]:

        pollutant = parameter_label(
            anomaly.get(
                "parameter",
                "pollutant",
            )
        )

        value = anomaly.get("value")
        unit = anomaly.get("unit", "")
        timestamp = format_datetime(
            anomaly.get("timestamp")
        )
        baseline = anomaly.get("local_median")
        deviation = anomaly.get("deviation_percent")

        insights.append(
            f"{pollutant} experienced a "
            f"significant pollution spike at "
            f"{timestamp}, reaching "
            f"{format_value(value)} {unit}. "
            f"This was approximately "
            f"{format_value(deviation)}% above "
            f"its local baseline of "
            f"{format_value(baseline)} {unit}."
        )

    return insights

def generate_peak_insights(
    report: dict[str, Any],
) -> list[str]:
    """
    Convert pollution peak records into
    human-readable insights.
    """

    peaks = report.get(
        "pollution_peaks",
        [],
    )

    if not peaks:
        return []

    insights = []

    for peak in peaks:

        parameter = peak.get(
            "parameter"
        )

        value = peak.get(
            "value"
        )

        unit = peak.get(
            "unit",
            "",
        )

        timestamp = peak.get(
            "timestamp"
        )

        if parameter is None:
            continue

        if value is None:
            continue

        pollutant = parameter_label(
            parameter
        )

        insights.append(
            f"Highest {pollutant} concentration "
            f"was {format_value(value)} {unit}, "
            f"recorded on "
            f"{format_datetime(timestamp)}."
        )

    return insights


# ============================================================
# Hourly Pattern Insights
# ============================================================

def generate_hourly_insights(
    report: dict[str, Any],
) -> list[str]:
    """
    Convert hourly pollution extremes into
    human-readable insights.
    """

    hourly = report.get(
        "hourly_extremes"
    )

    if not hourly:
        return []

    if not isinstance(
        hourly,
        dict,
    ):
        return []

    parameter = hourly.get(
        "parameter",
        "pm25",
    )

    pollutant = parameter_label(
        parameter
    )

    highest_hour = hourly.get(
        "highest_hour_ist"
    )

    highest_average = hourly.get(
        "highest_average"
    )

    lowest_hour = hourly.get(
        "lowest_hour_ist"
    )

    lowest_average = hourly.get(
        "lowest_average"
    )

    insights = []

    if highest_hour is not None:

        insights.append(
            f"{pollutant} had its highest "
            f"average concentration around "
            f"{highest_hour} IST, at "
            f"{format_value(highest_average)} "
            f"µg/m³."
        )

    if lowest_hour is not None:

        insights.append(
            f"{pollutant} had its lowest "
            f"average concentration around "
            f"{lowest_hour} IST, at "
            f"{format_value(lowest_average)} "
            f"µg/m³."
        )

    return insights

# ============================================================
# Daily Pattern Insights
# ============================================================

def generate_daily_insights(
    report: dict[str, Any],
) -> list[str]:
    """
    Convert PM2.5 daily extremes into insights.
    """

    daily = report.get(
        "daily_extremes",
    )

    if not daily:
        return []

    parameter = daily.get(
        "parameter",
        "pm25",
    )

    pollutant = parameter_label(
        parameter
    )

    highest_day = daily.get(
        "highest_day"
    )

    highest_average = daily.get(
        "highest_average"
    )

    lowest_day = daily.get(
        "lowest_day"
    )

    lowest_average = daily.get(
        "lowest_average"
    )

    insights = []

    if highest_day:

        insights.append(
            f"{pollutant} had its highest "
            f"daily average on "
            f"{highest_day}, at "
            f"{format_value(highest_average)} "
            f"µg/m³."
        )

    if lowest_day:

        insights.append(
            f"{pollutant} had its lowest "
            f"daily average on "
            f"{lowest_day}, at "
            f"{format_value(lowest_average)} "
            f"µg/m³."
        )

    return insights


# ============================================================
# Main Insight Generator
# ============================================================

def generate_insights(
    report: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Generate all user-facing insights from
    the analytics report.
    """

    if not report:
        return {
            "pollution_spikes": [],
            "peak_concentrations": [],
            "hourly_patterns": [],
            "daily_patterns": [],
        }

    return {
        "pollution_spikes": generate_anomaly_insights(
            report
        ),

        "peak_concentrations": generate_peak_insights(
            report
        ),

        "hourly_patterns": generate_hourly_insights(
            report
        ),

        "daily_patterns": generate_daily_insights(
            report
        ),
    }


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CityAir — Insight Generator")
    print("=" * 60)

    print(
        "\nThis module is designed to be "
        "called from report.py."
    )